from django.db import models
from django.contrib.auth.models import User # 引入 Django 原生 User
from datetime import date
from dateutil.relativedelta import relativedelta # 用於年月計算
from django.conf import settings # 用於 ForeignKey(User)

# ==============================================
# Phase 4: 權限管理和角色系統
# ==============================================
class UserRole(models.Model):
    """
    用戶角色管理
    定義系統中的不同角色和權限
    """
    ROLE_CHOICES = [
        ('admin', '系統管理員 System Admin'),
        ('hr', '人事管理員 HR Manager'), 
        ('supervisor', '主管 Supervisor'),
        ('staff', '一般員工 Staff'),
        ('readonly', '唯讀用戶 Read Only'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='關聯用戶')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name='角色')
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name='部門')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='創建時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')
    is_active = models.BooleanField(default=True, verbose_name='角色狀態')
    
    # 權限設定
    can_view_all_staff = models.BooleanField(default=False, verbose_name='可查看所有員工')
    can_edit_staff_data = models.BooleanField(default=False, verbose_name='可編輯員工資料')
    can_export_data = models.BooleanField(default=False, verbose_name='可匯出資料')
    can_import_data = models.BooleanField(default=False, verbose_name='可匯入資料')
    can_manage_users = models.BooleanField(default=False, verbose_name='可管理用戶')
    can_view_statistics = models.BooleanField(default=True, verbose_name='可查看統計')
    
    class Meta:
        verbose_name = '用戶角色'
        verbose_name_plural = '用戶角色'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    def save(self, *args, **kwargs):
        """
        根據角色自動設置權限
        """
        if self.role == 'admin':
            self.can_view_all_staff = True
            self.can_edit_staff_data = True
            self.can_export_data = True
            self.can_import_data = True
            self.can_manage_users = True
            self.can_view_statistics = True
        elif self.role == 'hr':
            self.can_view_all_staff = True
            self.can_edit_staff_data = True
            self.can_export_data = True
            self.can_import_data = True
            self.can_manage_users = False
            self.can_view_statistics = True
        elif self.role == 'supervisor':
            self.can_view_all_staff = True
            self.can_edit_staff_data = False
            self.can_export_data = True
            self.can_import_data = False
            self.can_manage_users = False
            self.can_view_statistics = True
        elif self.role == 'staff':
            self.can_view_all_staff = False
            self.can_edit_staff_data = False
            self.can_export_data = False
            self.can_import_data = False
            self.can_manage_users = False
            self.can_view_statistics = False
        elif self.role == 'readonly':
            self.can_view_all_staff = True
            self.can_edit_staff_data = False
            self.can_export_data = False
            self.can_import_data = False
            self.can_manage_users = False
            self.can_view_statistics = True
            
        super().save(*args, **kwargs)

class SystemLog(models.Model):
    """
    系統操作日誌
    記錄用戶的重要操作以供審計
    """
    ACTION_CHOICES = [
        ('create', '新增 Create'),
        ('update', '更新 Update'),
        ('delete', '刪除 Delete'),
        ('view', '查看 View'),
        ('export', '匯出 Export'),
        ('import', '匯入 Import'),
        ('login', '登入 Login'),
        ('logout', '登出 Logout'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='操作用戶')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='操作類型')
    resource_type = models.CharField(max_length=50, verbose_name='資源類型') # 如：StaffProfile, User等
    resource_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='資源ID')
    description = models.TextField(verbose_name='操作描述')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP地址')
    user_agent = models.TextField(blank=True, null=True, verbose_name='瀏覽器信息')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='操作時間')
    
    class Meta:
        verbose_name = '系統日誌'
        verbose_name_plural = '系統日誌'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username if self.user else 'Anonymous'} - {self.get_action_display()} - {self.resource_type}"

class StaffProfile(models.Model):
    # 校方資料
    user_account = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='關聯用戶賬號(可選)') # 改為可選
    created_by_admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_staff_profiles', verbose_name='操作創建的管理員')
    staff_id = models.CharField(max_length=50, unique=True, verbose_name='員工編號')
    staff_name = models.CharField(max_length=100, verbose_name='員工姓名') # 校方記錄的員工姓名，可能與個人資料中的姓名不同
    employment_type = models.CharField(max_length=50, blank=True, null=True, verbose_name='受聘形式')
    employment_type_remark = models.TextField(blank=True, null=True, verbose_name='受聘形式備註')
    dsej_registration_status = models.CharField(max_length=50, blank=True, null=True, verbose_name='教青局登記資料') # 例如：全職/兼職/不適用
    dsej_registration_rank = models.CharField(max_length=100, blank=True, null=True, verbose_name='教青局登記職級')
    entry_date = models.DateField(blank=True, null=True, verbose_name='入職日期')
    departure_date = models.DateField(blank=True, null=True, verbose_name='離職日期')
    retirement_date = models.DateField(blank=True, null=True, verbose_name='退休日期')
    position_grade = models.CharField(max_length=100, blank=True, null=True, verbose_name='職稱/任教年級')
    teaching_staff_salary_grade = models.CharField(max_length=50, blank=True, null=True, verbose_name='教學人員薪級')
    basic_salary_points = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='薪級基本點數')
    adjusted_salary_points = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='調整增薪點數')
    provident_fund_type = models.CharField(max_length=100, blank=True, null=True, verbose_name='公積金類別')
    remark = models.TextField(blank=True, null=True, verbose_name='備註')
    contract_number = models.CharField(max_length=100, blank=True, null=True, verbose_name='合約編號')
    is_active = models.BooleanField(default=True, verbose_name='在職狀態')
    school_seniority_description = models.CharField(max_length=50, blank=True, null=True, verbose_name='在校年資(描述)') # 例如 "3年2個月"

    # 個人資料 (personal_info) - 核心部分，其餘在 StaffPersonalDetail
    name_chinese = models.CharField(max_length=100, blank=True, null=True, verbose_name='員工姓名(中文)')
    name_foreign = models.CharField(max_length=150, blank=True, null=True, verbose_name='員工姓名(外文)')
    gender = models.CharField(max_length=10, blank=True, null=True, verbose_name='性別M/F') # 建議使用 choices
    marital_status = models.CharField(max_length=20, blank=True, null=True, verbose_name='婚姻狀況') # 建議使用 choices
    birth_place = models.CharField(max_length=100, blank=True, null=True, verbose_name='出生地點')
    birth_date = models.DateField(blank=True, null=True, verbose_name='出生日期')
    origin = models.CharField(max_length=100, blank=True, null=True, verbose_name='籍貫')
    id_type = models.CharField(max_length=50, blank=True, null=True, verbose_name='證件類別')
    id_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='證件號碼')
    id_expiry_date = models.DateField(blank=True, null=True, verbose_name='證件有效期')
    is_foreign_national = models.BooleanField(default=False, verbose_name='是否外籍人士')
    is_master = models.BooleanField(default=False, verbose_name='是否碩士學位')  # 全局標記
    is_phd = models.BooleanField(default=False, verbose_name='是否博士學位')    # 全局標記  
    is_overseas_study = models.BooleanField(default=False, verbose_name='是否留學') # 全局標記
    bank_account_number = models.CharField(max_length=100, blank=True, null=True, verbose_name='大豐銀行澳門幣戶口賬號')
    social_security_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='社保號碼')
    home_phone = models.CharField(max_length=30, blank=True, null=True, verbose_name='住宅電話')
    mobile_phone = models.CharField(max_length=30, blank=True, null=True, verbose_name='手提電話')  # 改為可選字段
    address = models.TextField(blank=True, null=True, verbose_name='住址')
    email = models.EmailField(blank=True, null=True, verbose_name='電郵')  # 改為可選字段
    alumni_class = models.CharField(max_length=50, blank=True, null=True, verbose_name='級社(校友適用)')
    alumni_class_year = models.CharField(max_length=10, blank=True, null=True, verbose_name='級社_年級(校友適用)')
    alumni_class_duration = models.CharField(max_length=20, blank=True, null=True, verbose_name='級社_年數(校友適用)')
    teacher_certificate_number = models.CharField(max_length=100, blank=True, null=True, verbose_name='教師證號碼')
    teaching_staff_rank = models.CharField(max_length=100, blank=True, null=True, verbose_name='教學人員職級')
    teaching_staff_rank_effective_date = models.DateField(blank=True, null=True, verbose_name='教學人員職級生效日期')
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='緊急聯絡人姓名')
    emergency_contact_phone = models.CharField(max_length=30, blank=True, null=True, verbose_name='緊急聯絡人電話')
    emergency_contact_relationship = models.CharField(max_length=50, blank=True, null=True, verbose_name='與緊急聯絡人之關係')
    
    # Phase 3: 新增員工圖片欄位
    profile_picture = models.ImageField(upload_to='staff_photos/', blank=True, null=True, verbose_name='員工照片')

    class Meta:
        verbose_name = '教職員基本資料'
        verbose_name_plural = '教職員基本資料'

    def __str__(self):
        return f"{self.name_chinese or self.staff_name} ({self.staff_id})"

    def calculate_school_seniority(self):
        """
        計算在校年資，基於入職日期自動計算到今天的年資
        優化後的簡單邏輯：
        1. 如果員工已離職 (is_active=False)，年資為 "0年0個月"
        2. 如果員工在職，優先使用 entry_date 欄位計算年資
        3. 如果 entry_date 為空，嘗試使用 employment_records 中最早的入職日期
        4. 每月自動更新
        """
        if not self.is_active:
            self.school_seniority_description = "0年0個月"
            self.save(update_fields=['school_seniority_description'])
            return

        # 確定入職日期：優先使用 StaffProfile.entry_date
        entry_date = self.entry_date
        
        # 如果 entry_date 為空，嘗試從 employment_records 獲取最早入職日期
        if not entry_date:
            employment_records = self.employment_records.filter(
                is_valid_for_seniority=True
            ).order_by('entry_date')
            
            if employment_records.exists():
                entry_date = employment_records.first().entry_date
        
        # 如果仍然沒有入職日期，設為0年資
        if not entry_date:
            self.school_seniority_description = "0年0個月"
            self.save(update_fields=['school_seniority_description'])
            return
        
        # 計算從入職日期到今天的年資
        today = date.today()
        
        # 確保入職日期不晚於今天
        if entry_date > today:
            self.school_seniority_description = "0年0個月"
            self.save(update_fields=['school_seniority_description'])
            return
        
        # 使用 relativedelta 精確計算年月差
        diff = relativedelta(today, entry_date)
        years = diff.years
        months = diff.months
        
        self.school_seniority_description = f"{years}年{months}個月"
        self.save(update_fields=['school_seniority_description'])

    def update_global_education_flags(self):
        """
        根據學歷記錄更新全局教育標記
        """
        # 檢查是否有相應的學歷記錄
        has_master = self.education_backgrounds.filter(is_master=True).exists()
        has_phd = self.education_backgrounds.filter(is_phd=True).exists()
        has_overseas = self.education_backgrounds.filter(is_overseas_study=True).exists()
        
        # 更新全局標記
        self.is_master = has_master
        self.is_phd = has_phd
        self.is_overseas_study = has_overseas
        
        # 保存更改
        self.save(update_fields=['is_master', 'is_phd', 'is_overseas_study'])

    def clean_staff_name(self):
        """
        自動修復員工姓名顯示問題
        如果name_chinese為空、None或'/'，嘗試使用其他欄位修復
        """
        if not self.name_chinese or self.name_chinese.strip() == '' or self.name_chinese.strip() == '/':
            # 嘗試使用外文姓名
            if self.name_foreign and self.name_foreign.strip() and self.name_foreign.strip() != '/':
                self.name_chinese = self.name_foreign.strip()
            # 如果外文姓名也有問題，嘗試使用staff_name
            elif self.staff_name and self.staff_name.strip() and self.staff_name.strip() != '/':
                self.name_chinese = self.staff_name.strip()

    def save(self, *args, **kwargs):
        # 自動修復姓名問題
        self.clean_staff_name()
        
        # 記錄是否是新創建的記錄
        is_new = self.pk is None
        
        # 檢查關鍵欄位是否有變化（只對已存在的記錄）
        fields_changed = []
        if not is_new:
            try:
                old_instance = StaffProfile.objects.get(pk=self.pk)
                if old_instance.entry_date != self.entry_date:
                    fields_changed.append('entry_date')
                if old_instance.departure_date != self.departure_date:
                    fields_changed.append('departure_date')
                if old_instance.is_active != self.is_active:
                    fields_changed.append('is_active')
            except StaffProfile.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # 如果是新記錄或關鍵欄位有變化，重新計算年資
        if is_new or fields_changed:
            # 避免在update_fields中包含school_seniority_description時重複計算
            update_fields = kwargs.get('update_fields', [])
            if not update_fields or 'school_seniority_description' not in update_fields:
                self.calculate_school_seniority()

class EmploymentRecord(models.Model):
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='employment_records', verbose_name='教職員')
    employment_type = models.CharField(max_length=50, blank=True, null=True, verbose_name='受聘形式')
    entry_date = models.DateField(verbose_name='入職日期')
    departure_date = models.DateField(blank=True, null=True, verbose_name='離職日期')
    is_valid_for_seniority = models.BooleanField(default=True, verbose_name='有效年資')
    remark = models.TextField(blank=True, null=True, verbose_name='備註')

    class Meta:
        verbose_name = '在職記錄'
        verbose_name_plural = '在職記錄'
        ordering = ['-entry_date']

    def __str__(self):
        return f"{self.staff.staff_id} - {self.entry_date} to {self.departure_date or 'Current'}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # 當在職記錄保存後，觸發對應 StaffProfile 的年資重新計算
        self.staff.calculate_school_seniority()

    def delete(self, *args, **kwargs):
        staff_profile = self.staff
        super().delete(*args, **kwargs)
        # 當在職記錄刪除後，觸發對應 StaffProfile 的年資重新計算
        staff_profile.calculate_school_seniority()

class FamilyMember(models.Model):
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='family_members', verbose_name='教職員')
    name = models.CharField(max_length=100, verbose_name='姓名')
    relationship = models.CharField(max_length=50, verbose_name='關係')
    birth_date = models.DateField(blank=True, null=True, verbose_name='出生日期')
    age = models.IntegerField(blank=True, null=True, verbose_name='年齡') # 可以考慮根據 birth_date 自動計算
    education_level = models.CharField(max_length=100, blank=True, null=True, verbose_name='學歷程度')
    institution = models.CharField(max_length=150, blank=True, null=True, verbose_name='教育機構/任職機構')
    alumni_class = models.CharField(max_length=50, blank=True, null=True, verbose_name='級社(校友適用)')

    class Meta:
        verbose_name = '家庭成員'
        verbose_name_plural = '家庭成員'

    def __str__(self):
        return f"{self.staff.name_chinese or self.staff.staff_name} 的家庭成員: {self.name}"

class EducationBackground(models.Model):
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='education_backgrounds', verbose_name='教職員')
    study_period = models.CharField(max_length=50, verbose_name='就讀年份(如:2016-2020)')
    school_name = models.CharField(max_length=150, verbose_name='就讀學校')
    education_level = models.CharField(max_length=100, verbose_name='教育程度')
    degree_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='專科學位名稱')
    certificate_date = models.DateField(blank=True, null=True, verbose_name='獲得證書日期')
    is_phd = models.BooleanField(default=False, verbose_name='博士學位')        # 具體學歷標記
    is_master = models.BooleanField(default=False, verbose_name='碩士學位')  # 具體學歷標記
    is_overseas_study = models.BooleanField(default=False, verbose_name='是否留學') # 具體學歷標記
    # is_foreign_national = models.BooleanField(default=False, verbose_name='是否外籍人士') # <--- 移除此行

    class Meta:
        verbose_name = '學歷狀況'
        verbose_name_plural = '學歷狀況'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # 當學歷記錄保存後，觸發全局標記更新
        self.staff.update_global_education_flags()

    def delete(self, *args, **kwargs):
        staff_profile = self.staff
        super().delete(*args, **kwargs)
        # 當學歷記錄刪除後，觸發全局標記更新
        staff_profile.update_global_education_flags()

    def __str__(self):
        return f"{self.staff.name_chinese or self.staff.staff_name} 的學歷: {self.school_name}"

class WorkExperience(models.Model):
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='work_experiences', verbose_name='教職員')
    employment_period = models.CharField(max_length=50, verbose_name='任職年份(如:2016-2020)') # 建議改為 start_date 和 end_date
    organization = models.CharField(max_length=150, verbose_name='任職機構') # 如果是本校，是否與 EmploymentRecord 重複？
    position = models.CharField(max_length=100, verbose_name='任職職位')
    salary = models.CharField(max_length=50, blank=True, null=True, verbose_name='薪金')
    # is_valid_seniority 字段已移除，由 EmploymentRecord.is_valid_for_seniority 替代

    class Meta:
        verbose_name = '工作經驗 (校外為主)' # 建議明確其用途
        verbose_name_plural = '工作經驗'

    def __str__(self):
        return f"{self.staff.name_chinese or self.staff.staff_name} 的工作經驗: {self.organization}"

class ProfessionalQualification(models.Model):
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='professional_qualifications', verbose_name='教職員')
    qualification_name = models.CharField(max_length=150, verbose_name='專業資格名稱')
    issuing_organization = models.CharField(max_length=150, verbose_name='頒發機構')
    issue_date = models.DateField(verbose_name='頒授日期')

    class Meta:
        verbose_name = '專業資格'
        verbose_name_plural = '專業資格'

    def __str__(self):
        return f"{self.staff.name_chinese or self.staff.staff_name} 的專業資格: {self.qualification_name}"

class AssociationPosition(models.Model):
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='association_positions', verbose_name='教職員')
    association_name = models.CharField(max_length=150, verbose_name='社團名稱')
    position = models.CharField(max_length=100, verbose_name='職位')
    start_year = models.CharField(max_length=10, verbose_name='開始年期') # 可以考慮使用 DateField
    end_year = models.CharField(max_length=10, blank=True, null=True, verbose_name='結束年期') # 可以考慮使用 DateField

    class Meta:
        verbose_name = '社團職務'
        verbose_name_plural = '社團職務'

    def __str__(self):
        return f"{self.staff.name_chinese or self.staff.staff_name} 的社團職務: {self.association_name} - {self.position}"

# 之前的 EmploymentRecord 模型可以保留，用於記錄校內職位變動等詳細信息，如果需要的話。
# class EmploymentRecord(models.Model):
#     staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='employment_records', verbose_name='教職員')
#     # ... 在職記錄相關字段 ...
#     class Meta:
#         verbose_name = '在職記錄'
#         verbose_name_plural = '在職記錄'
