from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import tempfile
import os
import csv
from datetime import datetime
from io import BytesIO
import zipfile
from .models import (
    StaffProfile, FamilyMember, EducationBackground, WorkExperience, 
    ProfessionalQualification, AssociationPosition, EmploymentRecord,
    UserRole, SystemLog  # Phase 4: 新增權限管理模型
)
from .views import import_data  # 導入現有的導入函數

# Inline Admin Definitions
class EmploymentRecordInline(admin.TabularInline):
    model = EmploymentRecord
    extra = 1
    fields = ('employment_type', 'entry_date', 'departure_date', 'is_valid_for_seniority', 'remark')

class EducationBackgroundInline(admin.TabularInline):
    model = EducationBackground
    extra = 1
    # 確保這裡的字段與 EducationBackground 模型中的字段一致，並包含了新增的字段
    fields = ('study_period', 'school_name', 'education_level', 'degree_name', 'certificate_date', 'is_phd', 'is_master', 'is_overseas_study')

class FamilyMemberInline(admin.TabularInline):
    model = FamilyMember
    extra = 1
    # 建議也明確指定 fields，例如：
    # fields = ('name', 'relationship', 'birth_date', 'age', 'education_level', 'institution', 'alumni_class')

class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    extra = 1
    # 建議也明確指定 fields

class ProfessionalQualificationInline(admin.TabularInline):
    model = ProfessionalQualification
    extra = 1
    # 建議也明確指定 fields

class AssociationPositionInline(admin.TabularInline):
    model = AssociationPosition
    extra = 1
    # 建議也明確指定 fields

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'name_chinese', 'employment_type', 'active_status_display', 'entry_date', 'school_seniority_description')
    search_fields = ('staff_id', 'staff_name', 'name_chinese', 'id_number')
    list_filter = ('is_active', 'employment_type', 'position_grade')
    readonly_fields = ('school_seniority_description',)
    
    def active_status_display(self, obj):
        """在職狀態顯示"""
        if obj.is_active:
            return '✅ 在職'
        else:
            return '❌ 離職'
    active_status_display.short_description = '在職狀態'
    active_status_display.admin_order_field = 'is_active'  # 允許按此欄位排序
    
    def get_urls(self):
        """添加自定義URL"""
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', 
                 self.admin_site.admin_view(self.import_csv_view), 
                 name='staffprofile_import_csv'),
            path('batch-photo-upload/', 
                 self.admin_site.admin_view(self.batch_photo_upload_view), 
                 name='staffprofile_batch_photo_upload'),
            path('export-csv/', 
                 self.admin_site.admin_view(self.export_csv_view), 
                 name='staffprofile_export_csv'),
            path('export-photos/', 
                 self.admin_site.admin_view(self.export_photos_view), 
                 name='staffprofile_export_photos'),
        ]
        return custom_urls + urls
    
    def import_csv_view(self, request):
        """處理CSV批量導入"""
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            if not csv_file:
                messages.error(request, '請選擇CSV文件')
                return render(request, 'admin/staff_management/staffprofile/import_csv.html')
            
            if not csv_file.name.endswith('.csv'):
                messages.error(request, '文件格式不正確，請上傳CSV文件')
                return render(request, 'admin/staff_management/staffprofile/import_csv.html')
            
            try:
                # 保存臨時文件
                with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                    for chunk in csv_file.chunks():
                        tmp_file.write(chunk)
                    tmp_file_path = tmp_file.name
                
                # 調用現有的導入函數
                result = import_data(tmp_file_path)
                
                # 清理臨時文件
                os.unlink(tmp_file_path)
                
                # 記錄操作日誌
                from .permissions import log_user_action
                log_user_action(
                    request.user, 'import', 'StaffProfile', None,
                    f"批量導入員工資料: 成功 {result['imported_count']} 筆，失敗 {len(result['errors'])} 筆",
                    request
                )
                
                if result['imported_count'] > 0:
                    messages.success(request, f'成功導入 {result["imported_count"]} 筆員工資料')
                
                if result['errors']:
                    error_msg = f'導入過程中發生 {len(result["errors"])} 個錯誤:\n' + '\n'.join(result['errors'][:5])
                    if len(result['errors']) > 5:
                        error_msg += f'\n... 還有 {len(result["errors"]) - 5} 個錯誤'
                    messages.warning(request, error_msg)
                
                return redirect('admin:staff_management_staffprofile_changelist')
                
            except Exception as e:
                messages.error(request, f'導入失敗: {str(e)}')
                return render(request, 'admin/staff_management/staffprofile/import_csv.html')
        
        return render(request, 'admin/staff_management/staffprofile/import_csv.html')
    
    def batch_photo_upload_view(self, request):
        """處理批量照片上傳"""
        if request.method == 'POST':
            photos = request.FILES.getlist('photos')
            
            if not photos:
                messages.error(request, '請選擇照片文件')
                return render(request, 'admin/staff_management/staffprofile/batch_photo_upload.html')
            
            success_count = 0
            error_count = 0
            errors = []
            
            for photo in photos:
                try:
                    # 從文件名提取員工編號（假設格式為 "ST001.jpg" 或 "ST001_photo.jpg"）
                    filename = photo.name
                    staff_id = filename.split('.')[0].split('_')[0]
                    
                    # 查找員工
                    try:
                        staff = StaffProfile.objects.get(staff_id=staff_id)
                    except StaffProfile.DoesNotExist:
                        errors.append(f'找不到員工編號 {staff_id}')
                        error_count += 1
                        continue
                    
                    # 保存照片
                    staff.profile_picture = photo
                    staff.save()
                    success_count += 1
                    
                except Exception as e:
                    errors.append(f'處理文件 {photo.name} 時出錯: {str(e)}')
                    error_count += 1
            
            # 記錄操作日誌
            from .permissions import log_user_action
            log_user_action(
                request.user, 'import', 'StaffProfile', None,
                f"批量上傳員工照片: 成功 {success_count} 張，失敗 {error_count} 張",
                request
            )
            
            if success_count > 0:
                messages.success(request, f'成功上傳 {success_count} 張員工照片')
            
            if errors:
                error_msg = f'上傳過程中發生 {error_count} 個錯誤:\n' + '\n'.join(errors[:5])
                if len(errors) > 5:
                    error_msg += f'\n... 還有 {len(errors) - 5} 個錯誤'
                messages.warning(request, error_msg)
            
            return redirect('admin:staff_management_staffprofile_changelist')
        
        return render(request, 'admin/staff_management/staffprofile/batch_photo_upload.html')
    
    def export_csv_view(self, request):
        """處理CSV批量導出"""
        def safe_str(value):
            """安全的字符串轉換，處理空值"""
            if value is None or value == '':
                return ''
            if isinstance(value, bool):
                return 'True' if value else 'False'
            return str(value)
        
        def should_export_record(staff):
            """判斷記錄是否應該被導出（只導出有有效staff_id的記錄）"""
            return staff.staff_id and staff.staff_id.strip() and not staff.staff_id.startswith('MISSING_')
        
        def format_date(date_obj):
            """格式化日期為字符串"""
            if date_obj is None:
                return ''
            return date_obj.strftime('%Y-%m-%d')
        
        # 創建CSV響應
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="staff_data_export_{current_time}.csv"'
        
        # 添加BOM以支持Excel正確顯示中文
        response.write('\ufeff')
        
        writer = csv.writer(response)
        
        # 寫入CSV頭部（與導入模板完全一致）
        headers = [
            'staff_id', 'staff_name', 'employment_type', 'employment_type_remark', 
            'dsej_registration_status', 'dsej_registration_rank', 'entry_date', 'departure_date', 
            'retirement_date', 'position_grade', 'teaching_staff_salary_grade', 'basic_salary_points', 
            'adjusted_salary_points', 'provident_fund_type', 'remark', 'name_chinese', 'name_foreign', 
            'gender', 'marital_status', 'birth_place', 'birth_date', 'origin', 'id_type', 'id_number', 
            'id_expiry_date', 'bank_account_number', 'social_security_number', 'home_phone', 'mobile_phone', 
            'address', 'email', 'alumni_class', 'alumni_class_year', 'alumni_class_duration', 
            'teacher_certificate_number', 'teaching_staff_rank', 'teaching_staff_rank_effective_date', 
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            # 家庭成員 (1-5)
            'family_member_1_name', 'family_member_1_relationship', 'family_member_1_birth_date', 
            'family_member_1_age', 'family_member_1_education_level', 'family_member_1_institution', 
            'family_member_1_alumni_class', 'family_member_2_name', 'family_member_2_relationship', 
            'family_member_2_birth_date', 'family_member_2_age', 'family_member_2_education_level', 
            'family_member_2_institution', 'family_member_2_alumni_class', 'family_member_3_name', 
            'family_member_3_relationship', 'family_member_3_birth_date', 'family_member_3_age', 
            'family_member_3_education_level', 'family_member_3_institution', 'family_member_3_alumni_class', 
            'family_member_4_name', 'family_member_4_relationship', 'family_member_4_birth_date', 
            'family_member_4_age', 'family_member_4_education_level', 'family_member_4_institution', 
            'family_member_4_alumni_class', 'family_member_5_name', 'family_member_5_relationship', 
            'family_member_5_birth_date', 'family_member_5_age', 'family_member_5_education_level', 
            'family_member_5_institution', 'family_member_5_alumni_class',
            # 教育背景 (1-4)
            'education_1_study_period', 'education_1_school_name', 'education_1_education_level', 
            'education_1_degree_name', 'education_1_certificate_date', 'education_2_study_period', 
            'education_2_school_name', 'education_2_education_level', 'education_2_degree_name', 
            'education_2_certificate_date', 'education_3_study_period', 'education_3_school_name', 
            'education_3_education_level', 'education_3_degree_name', 'education_3_certificate_date', 
            'education_4_study_period', 'education_4_school_name', 'education_4_education_level', 
            'education_4_degree_name', 'education_4_certificate_date',
            # 工作經驗 (1-4)
            'work_experience_1_employment_period', 'work_experience_1_organization', 'work_experience_1_position', 
            'work_experience_1_salary', 'work_experience_2_employment_period', 'work_experience_2_organization', 
            'work_experience_2_position', 'work_experience_2_salary', 'work_experience_3_employment_period', 
            'work_experience_3_organization', 'work_experience_3_position', 'work_experience_3_salary', 
            'work_experience_4_employment_period', 'work_experience_4_organization', 'work_experience_4_position', 
            'work_experience_4_salary',
            # 專業資格 (1-4)
            'professional_qualification_1_name', 'professional_qualification_1_issuing_organization', 
            'professional_qualification_1_issue_date', 'professional_qualification_2_name', 
            'professional_qualification_2_issuing_organization', 'professional_qualification_2_issue_date', 
            'professional_qualification_3_name', 'professional_qualification_3_issuing_organization', 
            'professional_qualification_3_issue_date', 'professional_qualification_4_name', 
            'professional_qualification_4_issuing_organization', 'professional_qualification_4_issue_date',
            # 社團職務 (1-4)
            'association_1_name', 'association_1_position', 'association_1_start_year', 'association_1_end_year', 
            'association_2_name', 'association_2_position', 'association_2_start_year', 'association_2_end_year', 
            'association_3_name', 'association_3_position', 'association_3_start_year', 'association_3_end_year', 
            'association_4_name', 'association_4_position', 'association_4_start_year', 'association_4_end_year',
            # 全局標記
            'is_foreign_national', 'is_master', 'is_phd', 'is_overseas_study', 'is_active', 'contract_number'
        ]
        writer.writerow(headers)
        
        # 獲取所有員工數據，只導出有效記錄
        staff_queryset = StaffProfile.objects.all().prefetch_related(
            'family_members', 'education_backgrounds', 'work_experiences', 
            'professional_qualifications', 'association_positions'
        )
        
        export_count = 0
        for staff in staff_queryset:
            # 只導出有有效staff_id的記錄
            if not should_export_record(staff):
                continue
                
            try:
                # 獲取相關數據
                family_members = list(staff.family_members.all()[:5])  # 最多5個
                education_backgrounds = list(staff.education_backgrounds.all()[:4])  # 最多4個
                work_experiences = list(staff.work_experiences.all()[:4])  # 最多4個
                professional_qualifications = list(staff.professional_qualifications.all()[:4])  # 最多4個
                association_positions = list(staff.association_positions.all()[:4])  # 最多4個
                
                # 構建數據行
                row = [
                    # 基本信息
                    safe_str(staff.staff_id), safe_str(staff.staff_name), safe_str(staff.employment_type),
                    safe_str(staff.employment_type_remark), safe_str(staff.dsej_registration_status),
                    safe_str(staff.dsej_registration_rank), format_date(staff.entry_date), 
                    format_date(staff.departure_date), format_date(staff.retirement_date),
                    safe_str(staff.position_grade), safe_str(staff.teaching_staff_salary_grade),
                    safe_str(staff.basic_salary_points), safe_str(staff.adjusted_salary_points),
                    safe_str(staff.provident_fund_type), safe_str(staff.remark), safe_str(staff.name_chinese),
                    safe_str(staff.name_foreign), safe_str(staff.gender), safe_str(staff.marital_status),
                    safe_str(staff.birth_place), format_date(staff.birth_date), safe_str(staff.origin),
                    safe_str(staff.id_type), safe_str(staff.id_number), format_date(staff.id_expiry_date),
                    safe_str(staff.bank_account_number), safe_str(staff.social_security_number),
                    safe_str(staff.home_phone), safe_str(staff.mobile_phone), safe_str(staff.address),
                    safe_str(staff.email), safe_str(staff.alumni_class), safe_str(staff.alumni_class_year),
                    safe_str(staff.alumni_class_duration), safe_str(staff.teacher_certificate_number),
                    safe_str(staff.teaching_staff_rank), format_date(staff.teaching_staff_rank_effective_date),
                    safe_str(staff.emergency_contact_name), safe_str(staff.emergency_contact_phone),
                    safe_str(staff.emergency_contact_relationship)
                ]
                
                # 家庭成員 (1-5)
                for i in range(5):
                    if i < len(family_members):
                        fm = family_members[i]
                        row.extend([
                            safe_str(fm.name), safe_str(fm.relationship), format_date(fm.birth_date),
                            safe_str(fm.age), safe_str(fm.education_level), safe_str(fm.institution),
                            safe_str(fm.alumni_class)
                        ])
                    else:
                        row.extend(['', '', '', '', '', '', ''])  # 7個空欄位
                
                # 教育背景 (1-4)
                for i in range(4):
                    if i < len(education_backgrounds):
                        edu = education_backgrounds[i]
                        row.extend([
                            safe_str(edu.study_period), safe_str(edu.school_name), safe_str(edu.education_level),
                            safe_str(edu.degree_name), format_date(edu.certificate_date)
                        ])
                    else:
                        row.extend(['', '', '', '', ''])  # 5個空欄位
                
                # 工作經驗 (1-4)
                for i in range(4):
                    if i < len(work_experiences):
                        we = work_experiences[i]
                        row.extend([
                            safe_str(we.employment_period), safe_str(we.organization), 
                            safe_str(we.position), safe_str(we.salary)
                        ])
                    else:
                        row.extend(['', '', '', ''])  # 4個空欄位
                
                # 專業資格 (1-4)
                for i in range(4):
                    if i < len(professional_qualifications):
                        pq = professional_qualifications[i]
                        row.extend([
                            safe_str(pq.qualification_name), safe_str(pq.issuing_organization),
                            format_date(pq.issue_date)
                        ])
                    else:
                        row.extend(['', '', ''])  # 3個空欄位
                
                # 社團職務 (1-4)
                for i in range(4):
                    if i < len(association_positions):
                        ap = association_positions[i]
                        row.extend([
                            safe_str(ap.association_name), safe_str(ap.position),
                            safe_str(ap.start_year), safe_str(ap.end_year)
                        ])
                    else:
                        row.extend(['', '', '', ''])  # 4個空欄位
                
                # 全局標記
                row.extend([
                    safe_str(staff.is_foreign_national), safe_str(staff.is_master),
                    safe_str(staff.is_phd), safe_str(staff.is_overseas_study), safe_str(staff.is_active),
                    safe_str(staff.contract_number)
                ])
                
                writer.writerow(row)
                export_count += 1
                
            except Exception as e:
                # 記錄錯誤但繼續處理其他記錄
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"導出員工 {staff.staff_id} 時發生錯誤: {e}")
        
        # 記錄操作日誌
        from .permissions import log_user_action
        log_user_action(
            request.user, 'export', 'StaffProfile', None,
            f"導出員工資料CSV: 成功導出 {export_count} 筆記錄",
            request
        )
        
        return response

    def export_photos_view(self, request):
        """導出員工照片為ZIP，檔名採用員工編號"""
        buffer = BytesIO()
        exported = 0

        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            queryset = StaffProfile.objects.exclude(profile_picture='').exclude(profile_picture__isnull=True)
            for staff in queryset:
                if not staff.staff_id:
                    continue
                try:
                    file_obj = staff.profile_picture
                    if not file_obj:
                        continue
                    # 保留原副檔名，預設 .jpg
                    _, ext = os.path.splitext(file_obj.name)
                    ext = ext or '.jpg'
                    filename = f"{staff.staff_id}{ext}"
                    with file_obj.open('rb') as f:
                        zipf.writestr(filename, f.read())
                        exported += 1
                except Exception as exc:  # pragma: no cover - 錯誤記錄後繼續
                    import logging
                    logging.getLogger(__name__).error(f"導出照片 {staff.staff_id} 失敗: {exc}")

        response = HttpResponse(buffer.getvalue(), content_type='application/zip')
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename=\"staff_photos_{current_time}.zip\"'

        from .permissions import log_user_action
        log_user_action(
            request.user, 'export', 'StaffProfile', None,
            f"導出員工照片ZIP: 成功導出 {exported} 張照片",
            request
        )
        return response
    
    # 添加批量操作 - 包括年資計算功能
    actions = ['set_active', 'set_inactive', 'toggle_active_status', 'recalculate_seniority']
    
    def recalculate_seniority(self, request, queryset):
        """批量重新計算員工年資"""
        success_count = 0
        error_count = 0
        
        for staff in queryset:
            try:
                old_seniority = staff.school_seniority_description
                staff.calculate_school_seniority()
                new_seniority = staff.school_seniority_description
                
                # 記錄操作日誌
                from .permissions import log_user_action
                log_user_action(
                    request.user, 'update', 'StaffProfile', staff.id,
                    f"重新計算員工 {staff.staff_name or staff.name_chinese} 年資: {old_seniority} → {new_seniority}",
                    request
                )
                success_count += 1
            except Exception as e:
                error_count += 1
                # 記錄錯誤
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"計算員工 {staff.staff_id} 年資時發生錯誤: {e}")
        
        # 顯示操作結果
        if success_count > 0:
            self.message_user(request, f'成功重新計算 {success_count} 名員工的年資')
        if error_count > 0:
            self.message_user(request, f'{error_count} 名員工年資計算失敗，請檢查日誌', level='warning')
    
    recalculate_seniority.short_description = "📊 重新計算年資 Recalculate Seniority"
    
    def set_active(self, request, queryset):
        """批量設置員工為在職狀態"""
        updated = queryset.update(is_active=True)
        # 記錄操作日誌
        from .permissions import log_user_action
        for staff in queryset:
            log_user_action(
                request.user, 'update', 'StaffProfile', staff.id, 
                f"設置員工 {staff.staff_name or staff.name_chinese} 為在職狀態", request
            )
        self.message_user(request, f'成功設置 {updated} 名員工為在職狀態')
    set_active.short_description = "✅ 設置為在職狀態 Set as Active"
    
    def set_inactive(self, request, queryset):
        """批量設置員工為離職狀態"""
        updated = queryset.update(is_active=False)
        # 記錄操作日誌
        from .permissions import log_user_action
        for staff in queryset:
            log_user_action(
                request.user, 'update', 'StaffProfile', staff.id, 
                f"設置員工 {staff.staff_name or staff.name_chinese} 為離職狀態", request
            )
        self.message_user(request, f'成功設置 {updated} 名員工為離職狀態')
    set_inactive.short_description = "❌ 設置為離職狀態"
    
    def toggle_active_status(self, request, queryset):
        """批量切換員工在職狀態"""
        for staff in queryset:
            old_status = staff.is_active
            staff.is_active = not staff.is_active
            staff.save()
            # 記錄操作日誌
            from .permissions import log_user_action
            status_text = "在職" if staff.is_active else "離職"
            log_user_action(
                request.user, 'update', 'StaffProfile', staff.id, 
                f"切換員工 {staff.staff_name or staff.name_chinese} 狀態為{status_text}", request
            )
        count = queryset.count()
        self.message_user(request, f'成功切換 {count} 名員工的在職狀態')
    toggle_active_status.short_description = "🔄 切換在職狀態"
    fieldsets = (
        ('校方資料', {
            'fields': ('user_account', 'staff_id', 'staff_name', 'employment_type', 'employment_type_remark', 
                       'dsej_registration_status', 'dsej_registration_rank', 'entry_date', 'departure_date', 
                       'retirement_date', 'position_grade', 'teaching_staff_salary_grade', 'basic_salary_points', 
                       'adjusted_salary_points', 'provident_fund_type', 'contract_number', 'remark', 'is_active')
        }),
        ('個人基本資料', {
            'fields': ('name_chinese', 'name_foreign', 'gender', 'marital_status', 'birth_place', 'birth_date', 
                       'origin', 'id_type', 'id_number', 'id_expiry_date', 'is_foreign_national', 
                       'is_master', 'is_phd', 'is_overseas_study',  # 全局教育標記
                       'bank_account_number', 'profile_picture',  # Phase 3: 添加員工照片字段
                       'social_security_number', 'home_phone', 'mobile_phone', 'address', 'email', 
                       'alumni_class', 'alumni_class_year', 'alumni_class_duration', 'teacher_certificate_number', 
                       'teaching_staff_rank', 'teaching_staff_rank_effective_date', 'emergency_contact_name', 
                       'emergency_contact_phone', 'emergency_contact_relationship')
        }),
    )
    inlines = [
        EmploymentRecordInline, 
        EducationBackgroundInline, 
        FamilyMemberInline, 
        WorkExperienceInline, 
        ProfessionalQualificationInline, 
        AssociationPositionInline
    ]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.calculate_school_seniority() 

# Phase 4: 權限管理系統的 Admin 設置
# 將 UserRole 配置移動到認證與授權部分
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'department', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'department', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'department')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'role', 'department', 'is_active')
        }),
        ('權限設定', {
            'fields': ('can_view_all_staff', 'can_edit_staff_data', 'can_export_data', 
                       'can_import_data', 'can_manage_users', 'can_view_statistics'),
            'description': '這些權限會根據角色自動設置，但可以進行微調。'
        }),
        ('時間記錄', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        """保存時記錄操作日誌"""
        super().save_model(request, obj, form, change)
        # 可以在這裡添加角色變更的審計日誌
        action = 'update' if change else 'create'
        try:
            from .permissions import log_user_action
            log_user_action(
                request.user, action, 'UserRole', obj.id,
                f"{action.title()} user role: {obj.user.username} - {obj.get_role_display()}",
                request
            )
        except Exception as e:
            pass  # 避免因為日誌記錄失敗影響主要操作

# 使用自定義方式註冊到auth應用中
# 這樣UserRole會出現在認證與授權部分
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group

# 取消在staff_management中的註冊，轉而在auth應用中註冊
# admin.site.register(UserRole, UserRoleAdmin)

# 創建UserRole的Proxy模型並註冊到auth應用
class UserRoleProxy(UserRole):
    class Meta:
        proxy = True
        verbose_name = '用戶角色'
        verbose_name_plural = '用戶角色'

# 將UserRole透過proxy模型註冊到系統中，並指定app_label為auth
UserRoleProxy._meta.app_label = 'auth'
admin.site.register(UserRoleProxy, UserRoleAdmin)

@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'resource_type', 'resource_id', 'timestamp', 'ip_address')
    list_filter = ('action', 'resource_type', 'timestamp')
    search_fields = ('user__username', 'resource_type', 'resource_id', 'description', 'ip_address')
    readonly_fields = ('user', 'action', 'resource_type', 'resource_id', 'description', 
                       'ip_address', 'user_agent', 'timestamp')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    
    def has_add_permission(self, request):
        """系統日誌不允許手動添加"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """系統日誌不允許修改"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """只有超級管理員可以刪除日誌"""
        return request.user.is_superuser

# 其他模型的 Admin 註冊 (如果有的話)
# admin.site.register(FamilyMember) # 通常 Inline 模型不需要單獨註冊
# admin.site.register(EducationBackground) 
# ...以此類推
