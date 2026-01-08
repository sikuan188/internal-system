from django.contrib import admin
from django.utils.html import format_html
from django.core.files.base import ContentFile
from .models import (
    StaffApplication, ApplicationEducation, 
    ApplicationFamilyMember, ApplicationWorkExperience, 
    ApplicationProfessionalQualification, ApplicationAssociationPosition
)
from staff_management.models import StaffProfile
import uuid

# 創建 ApplicationEducation 的 InlineModelAdmin
class ApplicationEducationInline(admin.TabularInline): 
    model = ApplicationEducation
    extra = 1
    # 添加 is_master 字段到顯示字段中
    fields = ('study_period', 'school_name', 'education_level', 'degree_name', 'certificate_date', 'is_phd', 'is_master', 'is_overseas_study')

class ApplicationFamilyMemberInline(admin.TabularInline):
    model = ApplicationFamilyMember
    extra = 1

class ApplicationWorkExperienceInline(admin.TabularInline):
    model = ApplicationWorkExperience
    extra = 1

class ApplicationProfessionalQualificationInline(admin.TabularInline):
    model = ApplicationProfessionalQualification
    extra = 1

class ApplicationAssociationPositionInline(admin.TabularInline):
    model = ApplicationAssociationPosition
    extra = 1

@admin.register(StaffApplication)
class StaffApplicationAdmin(admin.ModelAdmin):
    list_display = ('submission_id', 'name_chinese', 'profile_picture_thumbnail', 'application_date', 'status')
    list_filter = ('status', 'application_date')
    search_fields = ('name_chinese', 'submission_id')
    
    # 添加個人基本資料的全局選擇項和分組顯示
    fieldsets = (
        ('基本資料', {
            'fields': ('name_chinese', 'name_foreign', 'profile_picture', 'gender', 'marital_status')
        }),
        ('出生資料', {
            'fields': ('birth_place', 'birth_date', 'origin')
        }),
        ('證件資料', {
            'fields': ('id_type', 'id_number', 'id_expiry_date')
        }),
        # 移除全局標記分組 - 這些標記會在批准申請時根據具體學歷記錄自動計算
        # ('全局標記', {
        #     'fields': ('is_foreign_national', 'is_master', 'is_phd', 'is_overseas_study'),
        #     'description': '個人基本資料全局選擇項：外籍人士、碩士學位、博士學位、留學經歷'
        # }),
        ('聯絡資料', {
            'fields': ('bank_account_number', 'social_security_number', 'home_phone', 'mobile_phone', 'address', 'email')
        }),
        ('校友資料', {
            'fields': ('alumni_class', 'alumni_class_year', 'alumni_class_duration')
        }),
        ('職業資料', {
            'fields': ('teacher_certificate_number', 'teaching_staff_rank', 'teaching_staff_rank_effective_date')
        }),
        ('緊急聯絡人', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship')
        }),
        ('申請狀態', {
            'fields': ('status',)
        }),
    )
    
    # 更新 inlines 列表
    inlines = [
        ApplicationEducationInline, 
        ApplicationFamilyMemberInline, 
        ApplicationWorkExperienceInline, 
        ApplicationProfessionalQualificationInline, 
        ApplicationAssociationPositionInline
    ]
    
    def profile_picture_thumbnail(self, obj):
        """在列表頁面和編輯頁面顯示相片縮略圖"""
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%; object-fit: cover;" />',
                obj.profile_picture.url
            )
        return "無相片"
    profile_picture_thumbnail.short_description = "個人相片"
    
    # 可以添加 Action 來批量審批或拒絕
    def approve_applications(self, request, queryset):
        """批准選中的申請並創建對應的StaffProfile記錄"""
        approved_count = 0
        for application in queryset.filter(status='pending'):
            # 檢查是否已經存在對應的StaffProfile
            existing_profile = StaffProfile.objects.filter(
                name_chinese=application.name_chinese,
                birth_date=application.birth_date
            ).first()
            
            if not existing_profile:
                # 生成員工編號
                staff_id = f"TEMP-{application.submission_id}"
                while StaffProfile.objects.filter(staff_id=staff_id).exists():
                    staff_id = f"TEMP-{application.submission_id}-{uuid.uuid4().hex[:4]}"
                
                # 創建StaffProfile記錄，初始全局標記為False
                staff_profile = StaffProfile.objects.create(
                    staff_id=staff_id,
                    staff_name=application.name_chinese,
                    name_chinese=application.name_chinese,
                    name_foreign=application.name_foreign,
                    gender=application.gender,
                    marital_status=application.marital_status,
                    birth_place=application.birth_place,
                    birth_date=application.birth_date,
                    origin=application.origin,
                    id_type=application.id_type,
                    id_number=application.id_number,
                    id_expiry_date=application.id_expiry_date,
                    # 全局標記初始化為False，將由學歷記錄自動更新
                    is_foreign_national=False,
                    is_master=False,
                    is_phd=False,
                    is_overseas_study=False,
                    bank_account_number=application.bank_account_number,
                    social_security_number=application.social_security_number,
                    home_phone=application.home_phone,
                    mobile_phone=application.mobile_phone,
                    address=application.address,
                    email=application.email,
                    alumni_class=application.alumni_class,
                    alumni_class_year=application.alumni_class_year,
                    alumni_class_duration=application.alumni_class_duration,
                    teacher_certificate_number=application.teacher_certificate_number,
                    teaching_staff_rank=application.teaching_staff_rank,
                    teaching_staff_rank_effective_date=application.teaching_staff_rank_effective_date,
                    emergency_contact_name=application.emergency_contact_name,
                    emergency_contact_phone=application.emergency_contact_phone,
                    emergency_contact_relationship=application.emergency_contact_relationship,
                    created_by_admin=request.user
                )
                
                # 同步個人相片
                if application.profile_picture:
                    # 讀取原始圖片內容
                    application.profile_picture.seek(0)
                    image_content = application.profile_picture.read()
                    
                    # 生成新的檔案名
                    original_filename = application.profile_picture.name
                    new_filename = f"staff_photos/{staff_id}_{original_filename.split('/')[-1]}"
                    
                    # 保存到StaffProfile
                    staff_profile.profile_picture.save(
                        new_filename,
                        ContentFile(image_content),
                        save=True
                    )
                
                # 複製學歷記錄並觸發全局標記更新
                from staff_management.models import EducationBackground
                for app_education in application.educations.all():
                    EducationBackground.objects.create(
                        staff=staff_profile,
                        study_period=app_education.study_period,
                        school_name=app_education.school_name,
                        education_level=app_education.education_level,
                        degree_name=app_education.degree_name,
                        certificate_date=app_education.certificate_date,
                        is_phd=app_education.is_phd,
                        is_master=app_education.is_master,
                        is_overseas_study=app_education.is_overseas_study
                    )
                
                # 複製其他關聯記錄
                from staff_management.models import FamilyMember, WorkExperience, ProfessionalQualification, AssociationPosition
                
                # 複製家庭成員
                for family_member in application.family_members.all():
                    FamilyMember.objects.create(
                        staff=staff_profile,
                        name=family_member.name,
                        relationship=family_member.relationship,
                        birth_date=family_member.birth_date,
                        age=family_member.age,
                        education_level=family_member.education_level,
                        institution=family_member.institution,
                        alumni_class=family_member.alumni_class
                    )
                
                # 複製工作經驗
                for work_exp in application.work_experiences.all():
                    WorkExperience.objects.create(
                        staff=staff_profile,
                        employment_period=work_exp.employment_period,
                        organization=work_exp.organization,
                        position=work_exp.position,
                        salary=work_exp.salary
                    )
                
                # 複製專業資格
                for prof_qual in application.professional_qualifications.all():
                    ProfessionalQualification.objects.create(
                        staff=staff_profile,
                        qualification_name=prof_qual.qualification_name,
                        issuing_organization=prof_qual.issuing_organization,
                        issue_date=prof_qual.issue_date
                    )
                
                # 複製社團職務
                for assoc_pos in application.association_positions.all():
                    AssociationPosition.objects.create(
                        staff=staff_profile,
                        association_name=assoc_pos.association_name,
                        position=assoc_pos.position,
                        start_year=assoc_pos.start_year,
                        end_year=assoc_pos.end_year
                    )
                
                approved_count += 1
            
            # 更新申請狀態
            application.status = 'approved'
            application.save()
        
        self.message_user(
            request, 
            f"成功批准 {approved_count} 個申請，並創建了對應的員工檔案"
        )
    approve_applications.short_description = "批准選中的申請並創建員工檔案"

    def reject_applications(self, request, queryset):
        queryset.update(status='rejected')
    reject_applications.short_description = "拒絕選中的申請"
    
    actions = [approve_applications, reject_applications]