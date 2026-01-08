from django.db import models
# from django.contrib.auth.models import User # 如果審批人等需要關聯 User

APPLICATION_STATUS_CHOICES = [
    ('pending', '待審批'),
    ('approved', '已批准'),
    ('rejected', '已拒絕'),
]

class StaffApplication(models.Model):
    submission_id = models.AutoField(primary_key=True, verbose_name='申請編號')
    application_date = models.DateTimeField(auto_now_add=True, verbose_name='申請日期')
    status = models.CharField(
        max_length=10,
        choices=APPLICATION_STATUS_CHOICES,
        default='pending',
        verbose_name='審批狀態'
    )
    # approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_applications', verbose_name='審批人')
    # approval_remarks = models.TextField(blank=True, null=True, verbose_name='審批備註')

    # 個人資料 (personal_info)
    name_chinese = models.CharField(max_length=100, blank=True, null=True, verbose_name='員工姓名(中文) Staff Name (Chinese)')
    name_foreign = models.CharField(max_length=150, blank=True, null=True, verbose_name='員工姓名(外文) Staff Name (Foreign)')
    profile_picture = models.ImageField(upload_to='application_photos/', blank=True, null=True, verbose_name='個人相片')
    gender = models.CharField(max_length=10, blank=True, null=True, verbose_name='性別M/F')
    marital_status = models.CharField(max_length=20, blank=True, null=True, verbose_name='婚姻狀況')
    birth_place = models.CharField(max_length=100, blank=True, null=True, verbose_name='出生地點')
    birth_date = models.DateField(blank=True, null=True, verbose_name='出生日期')
    origin = models.CharField(max_length=100, blank=True, null=True, verbose_name='籍貫')
    id_type = models.CharField(max_length=50, blank=True, null=True, verbose_name='證件類別')
    id_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='證件號碼')
    id_expiry_date = models.DateField(blank=True, null=True, verbose_name='證件有效期')
    
    # 全局標記欄位 - 與StaffProfile保持一致
    is_foreign_national = models.BooleanField(default=False, verbose_name='是否外籍人士')
    is_master = models.BooleanField(default=False, verbose_name='是否碩士學位')
    is_phd = models.BooleanField(default=False, verbose_name='是否博士學位')
    is_overseas_study = models.BooleanField(default=False, verbose_name='是否留學')
    
    bank_account_number = models.CharField(max_length=100, blank=True, null=True, verbose_name='大豐銀行澳門幣戶口賬號')
    social_security_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='社保號碼')
    home_phone = models.CharField(max_length=30, blank=True, null=True, verbose_name='住宅電話')
    mobile_phone = models.CharField(max_length=30, verbose_name='手提電話 Mobile Phone')  # 保持必填
    address = models.TextField(blank=True, null=True, verbose_name='住址')
    email = models.EmailField(blank=True, null=True, verbose_name='電郵 Email')  # 改為可選
    alumni_class = models.CharField(max_length=50, blank=True, null=True, verbose_name='級社(校友適用)')
    alumni_class_year = models.CharField(max_length=10, blank=True, null=True, verbose_name='級社_年級(校友適用)')
    alumni_class_duration = models.CharField(max_length=20, blank=True, null=True, verbose_name='級社_年數(校友適用)')
    teacher_certificate_number = models.CharField(max_length=100, blank=True, null=True, verbose_name='教師證號碼')
    teaching_staff_rank = models.CharField(max_length=100, blank=True, null=True, verbose_name='教學人員職級')
    teaching_staff_rank_effective_date = models.DateField(blank=True, null=True, verbose_name='教學人員職級生效日期')
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='緊急聯絡人姓名 Emergency Contact Name')
    emergency_contact_phone = models.CharField(max_length=30, blank=True, null=True, verbose_name='緊急聯絡人電話 Emergency Contact Phone')
    emergency_contact_relationship = models.CharField(max_length=50, blank=True, null=True, verbose_name='與緊急聯絡人之關係 Emergency Contact Relationship')

    class Meta:
        verbose_name = '入職申請主表'
        verbose_name_plural = '入職申請主表'
        ordering = ['-application_date']

    def __str__(self):
        return f"申請: {self.name_chinese} ({self.submission_id} - {self.get_status_display()})"

class ApplicationFamilyMember(models.Model):
    application = models.ForeignKey(StaffApplication, on_delete=models.CASCADE, related_name='family_members', verbose_name='入職申請')
    name = models.CharField(max_length=100, verbose_name='姓名')
    relationship = models.CharField(max_length=50, verbose_name='關係')
    birth_date = models.DateField(blank=True, null=True, verbose_name='出生日期')
    age = models.IntegerField(blank=True, null=True, verbose_name='年齡')
    education_level = models.CharField(max_length=100, blank=True, null=True, verbose_name='學歷程度')
    institution = models.CharField(max_length=150, blank=True, null=True, verbose_name='教育機構/任職機構')
    alumni_class = models.CharField(max_length=50, blank=True, null=True, verbose_name='級社(校友適用)')

    class Meta:
        verbose_name = '入職申請家庭成員'
        verbose_name_plural = '入職申請家庭成員'

class ApplicationEducation(models.Model):
    application = models.ForeignKey(StaffApplication, related_name='educations', on_delete=models.CASCADE, verbose_name='所屬申請')
    study_period = models.CharField(max_length=100, blank=True, null=True, verbose_name='就讀年份(起-止)')
    school_name = models.CharField(max_length=200, verbose_name='就讀學校')
    education_level = models.CharField(max_length=100, verbose_name='學歷程度')
    degree_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='專科/學位名稱')
    certificate_date = models.DateField(blank=True, null=True, verbose_name='獲授證書日期')
    is_phd = models.BooleanField(default=False, verbose_name='是否博士學位(PhD)') # <--- 確保此行存在或添加
    is_master = models.BooleanField(default=False, verbose_name='是否碩士學位(Master)') # 雙標記策略：具體學歷標記
    is_overseas_study = models.BooleanField(default=False, verbose_name='是否留學')
    # is_foreign_national = models.BooleanField(default=False, verbose_name='是否外籍人士') # <--- 移除此行

    class Meta:
        verbose_name = '入職申請學歷狀況'
        verbose_name_plural = '入職申請學歷狀況'

class ApplicationWorkExperience(models.Model):
    application = models.ForeignKey(StaffApplication, on_delete=models.CASCADE, related_name='work_experiences', verbose_name='入職申請')
    employment_period = models.CharField(max_length=50, verbose_name='任職年份(如:2016-2020)')
    organization = models.CharField(max_length=150, verbose_name='任職機構')
    position = models.CharField(max_length=100, verbose_name='任職職位')
    salary = models.CharField(max_length=50, blank=True, null=True, verbose_name='薪金')

    class Meta:
        verbose_name = '入職申請工作經驗'
        verbose_name_plural = '入職申請工作經驗'

class ApplicationProfessionalQualification(models.Model):
    application = models.ForeignKey(StaffApplication, on_delete=models.CASCADE, related_name='professional_qualifications', verbose_name='入職申請')
    qualification_name = models.CharField(max_length=150, verbose_name='專業資格名稱')
    issuing_organization = models.CharField(max_length=150, verbose_name='頒發機構')
    issue_date = models.DateField(verbose_name='頒授日期')

    class Meta:
        verbose_name = '入職申請專業資格'
        verbose_name_plural = '入職申請專業資格'

class ApplicationAssociationPosition(models.Model):
    application = models.ForeignKey(StaffApplication, on_delete=models.CASCADE, related_name='association_positions', verbose_name='入職申請')
    association_name = models.CharField(max_length=150, verbose_name='社團名稱')
    position = models.CharField(max_length=100, verbose_name='職位')
    start_year = models.CharField(max_length=10, verbose_name='開始年期')
    end_year = models.CharField(max_length=10, blank=True, null=True, verbose_name='結束年期')

    class Meta:
        verbose_name = '入職申請社團職務'
        verbose_name_plural = '入職申請社團職務'
