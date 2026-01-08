from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from dateutil.relativedelta import relativedelta


class User(AbstractUser):
    position = models.CharField('職稱', max_length=100, blank=True, null=True) # 確保 blank=True, null=True 允許為空
    teaching_grade = models.CharField('任教年級', max_length=100, blank=True, null=True) # 確保 blank=True, null=True 允許為空
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time_teacher', '全職教學人員(教師證)'),
        ('part_time_teacher', '兼職教學人員(教師證)'),
        ('full_time_staff', '全職職員(職員證)'),
        ('part_time_staff', '兼職職員(職員證)'),
        ('part_time_staff_no_id', '兼職職員'),
        ('full_time_janitor', '全職校工(職員證)'),
        ('part_time_janitor', '兼職校工'),
        ('intern_staff', '兼職實習生(職員證)'),
        ('short_term_intern', '短期實習生'),
        ('substitute_teacher', '代課老師'),
        ('partner_company', '合作單位(請註明公司名)'),
        ('leisure_activity_tutor', '正課餘暇導師'),
        ('co_curricular_teacher', '聯課活動導師'),
        ('volunteer_co_curricular', '義務聯課活動導師'),
        ('part_time_librarian', '圖書館兼職人員'),
    ]

    # 校方資料
    staff_id = models.CharField(max_length=20, unique=True, verbose_name="員工編號") # 員工的唯一識別號碼
    staff_name = models.CharField(max_length=100, verbose_name="員工姓名") # 員工的姓名，不可為空
    employment_type = models.CharField(max_length=50, choices=EMPLOYMENT_TYPE_CHOICES, blank=True, verbose_name="受聘形式") # 員工的受聘形式（例如：全職、兼職）
    employment_type_remark = models.CharField(max_length=255, blank=True, verbose_name="受聘形式備註") # 受聘形式的額外說明
    dsej_registration_status = models.CharField(max_length=50, blank=True, verbose_name="教青局登記資料") # 在教青局的登記狀態（全職/兼職/不適用）
    dsej_registration_rank = models.CharField(max_length=50, blank=True, verbose_name="教青局登記職級") # 在教青局的登記職級
    entry_date = models.DateField(null=True, blank=True, verbose_name="入職日期") # 員工的入職日期
    departure_date = models.DateField(null=True, blank=True, verbose_name="離職日期") # 員工的離職日期
    retirement_date = models.DateField(null=True, blank=True, verbose_name="退休日期") # 員工的退休日期
    position_grade = models.CharField(max_length=50, blank=True, verbose_name="職稱/任教年級") # 員工的職稱或任教年級
    teaching_staff_salary_grade = models.CharField(max_length=50, blank=True, verbose_name="教學人員薪級") # 教學人員的薪級
    basic_salary_points = models.IntegerField(null=True, blank=True, verbose_name="薪級基本點數") # 基本薪級點數值
    adjusted_salary_points = models.IntegerField(null=True, blank=True, verbose_name="調整增薪點數") # 調整後的增薪點數值
    provident_fund_type = models.CharField(max_length=50, blank=True, verbose_name="公積金類別") # 公積金的類型
    remark = models.TextField(blank=True, verbose_name="備註") # 其他備註資訊
    seniority_calculation_effective = models.BooleanField(default=True, verbose_name="年資計算有效") # 標記年資計算是否有效
    seniority = models.IntegerField(default=0, verbose_name="在職年資") # 保留此字段用於可能的存儲，但顯示時使用計算值

    def calculate_seniority(self):
        """Calculate and return the user's seniority based on EmploymentRecord."""
        total_days = 0
        # 過濾出需要計算年資的僱佣記錄，並按開始日期排序
        records = self.employment_records.filter(count_for_seniority=True).order_by('start_date')

        if not records:
            return "0年0月"

        # 處理連續的僱佣記錄
        # 這裡的邏輯需要仔細處理記錄的連續性，一個簡化的版本是直接加總所有有效記錄的時長
        # 更精確的計算可能需要考慮記錄間的間斷
        for record in records:
            start_date = record.start_date
            end_date = record.end_date if record.end_date else timezone.now().date()
            
            if start_date:
                delta = end_date - start_date
                total_days += delta.days
        
        if total_days < 0: # 避免結束日期早於開始日期的情況導致負數
            total_days = 0
            
        years = total_days // 365
        remaining_days = total_days % 365
        months = remaining_days // 30 # 大約的月份計算
        
        return f"{years}年{months}月"

    # 個人資料
    name_chinese = models.CharField(max_length=100, blank=True, verbose_name="員工姓名(中文)") # 員工的中文姓名
    name_foreign = models.CharField(max_length=100, verbose_name="員工姓名(外文)") # 員工的外文姓名，不可為空
    gender = models.CharField(max_length=10, blank=True, verbose_name="性別") # 員工的性別
    marital_status = models.CharField(max_length=20, blank=True, verbose_name="婚姻狀況") # 員工的婚姻狀況
    birth_place = models.CharField(max_length=100, blank=True, verbose_name="出生地點") # 員工的出生地點
    birth_date = models.DateField(null=True, blank=True, verbose_name="出生日期") # 員工的出生日期
    origin = models.CharField(max_length=100, blank=True, verbose_name="籍貫") # 員工的籍貫

    ID_TYPE_CHOICES = [
        ('macao_id', '澳門居民身份證'),
        ('passport', '護照'),
        ('other', '其他'),
    ]
    id_type = models.CharField(max_length=50, blank=True, verbose_name="證件類別", choices=ID_TYPE_CHOICES) # 員工的證件類型
    id_number = models.CharField(max_length=50, unique=True, verbose_name="證件號碼") # 員工的證件號碼，不可為空，加密存儲
    id_expiry_date = models.DateField(null=True, blank=True, verbose_name="證件有效期") # 證件的有效期
    is_macao_pr = models.BooleanField(default=True, verbose_name="澳門永久性居民") # 是否為澳門永久性居民

    bank_account_number = models.CharField(max_length=50, blank=True, verbose_name="大豐銀行澳門幣戶口賬號") # 員工的銀行帳號
    social_security_number = models.CharField(max_length=50, blank=True, verbose_name="社保號碼") # 員工的社會保障號碼
    home_phone = models.CharField(max_length=20, blank=True, verbose_name="住宅電話") # 員工的住家電話號碼
    mobile_phone = models.CharField(max_length=20, blank=True, verbose_name="手提電話") # 員工的手機號碼
    address = models.CharField(max_length=255, blank=True, verbose_name="住址") # 員工的住家地址
    email = models.EmailField(blank=True, verbose_name="電郵") # 員工的電子郵件地址
    alumni_class = models.CharField(max_length=100, blank=True, verbose_name="級社(校友適用)") # 如果是校友，所屬的班級
    alumni_class_year = models.IntegerField(null=True, blank=True, verbose_name="級社_年級(校友適用)") # 校友的畢業年份
    alumni_class_duration = models.CharField(max_length=50, blank=True, verbose_name="級社_年數(校友適用)") # 校友的就讀時長
    teacher_certificate_number = models.CharField(max_length=50, blank=True, verbose_name="教師證號碼") # 教師證的號碼
    teaching_staff_rank = models.CharField(max_length=50, blank=True, verbose_name="教學人員職級") # 教學人員的職級
    teaching_staff_rank_effective_date = models.DateField(null=True, blank=True, verbose_name="教學人員職級生效日期") # 教學人員職級的生效日期
    emergency_contact_name = models.CharField(max_length=100, blank=True, verbose_name="緊急聯絡人姓名") # 緊急聯絡人的姓名
    emergency_contact_phone = models.CharField(max_length=20, blank=True, verbose_name="緊急聯絡人電話") # 緊急聯絡人的電話號碼
    emergency_contact_relationship = models.CharField(max_length=50, blank=True, verbose_name="與緊急聯絡人之關係") # 與緊急聯絡人的關係

    # 解決related_name衝突 (保持不變)
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text=
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.',
        related_name="user_set_for_users_app", # 修改此处
        related_query_name="user_for_users_app", # 修改此处
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="user_set_for_users_app", # 修改此处
        related_query_name="user_for_users_app", # 修改此处
    )

    class Meta:
        verbose_name = "教師職員"
        verbose_name_plural = "教師職員"

    def __str__(self):
        return self.username

class FamilyMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='family_members', verbose_name="員工編號")
    name = models.CharField(max_length=100, verbose_name="姓名")
    relationship = models.CharField(max_length=50, verbose_name="關係")
    birth_date = models.DateField(null=True, blank=True, verbose_name="出生日期")
    age = models.IntegerField(null=True, blank=True, verbose_name="年齡")
    education_level = models.CharField(max_length=100, blank=True, verbose_name="學歷程度")
    institution = models.CharField(max_length=255, blank=True, verbose_name="教育機構/任職機構")
    alumni_class = models.CharField(max_length=100, blank=True, verbose_name="級社(校友適用)")

    class Meta:
        verbose_name = "家庭成員"
        verbose_name_plural = "家庭成員"

    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.relationship})"

class EducationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='education_history', verbose_name="員工編號")
    years = models.CharField(max_length=50, blank=True, verbose_name="就讀年份") # 例如: 2016-2020
    school = models.CharField(max_length=255, verbose_name="就讀學校")
    education_level = models.CharField(max_length=100, verbose_name="教育程度")
    major = models.CharField(max_length=255, blank=True, verbose_name="專科學位名稱")
    certificate_date = models.DateField(null=True, blank=True, verbose_name="獲得證書日期")
    is_overseas_study = models.BooleanField(default=False, verbose_name="是否留學經歷") # 標識該學歷是否為留學經歷

    class Meta:
        verbose_name = "學歷狀況"
        verbose_name_plural = "學歷狀況"

    def __str__(self):
        return f"{self.user.username} - {self.school} ({self.education_level})"

class WorkExperience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='work_experience', verbose_name="員工編號")
    years = models.CharField(max_length=50, blank=True, verbose_name="任職年份") # 例如: 2016-2020
    company = models.CharField(max_length=255, verbose_name="任職機構")
    position = models.CharField(max_length=100, verbose_name="任職職位")
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="薪金")

    class Meta:
        verbose_name = "工作經驗"
        verbose_name_plural = "工作經驗"

    def __str__(self):
        return f"{self.user.username} - {self.company} ({self.position})"

class ProfessionalQualification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='professional_qualifications', verbose_name="員工編號")
    name = models.CharField(max_length=255, verbose_name="專業資格名稱")
    issuing_organization = models.CharField(max_length=255, blank=True, verbose_name="頒發機構")
    issue_date = models.DateField(null=True, blank=True, verbose_name="頒授日期")

    class Meta:
        verbose_name = "專業資格"
        verbose_name_plural = "專業資格"

    def __str__(self):
        return f"{self.user.username} - {self.name}"

class SocialActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_activities', verbose_name="員工編號")
    organization_name = models.CharField(max_length=255, verbose_name="社團名稱")
    position = models.CharField(max_length=100, blank=True, verbose_name="職位")
    start_year = models.IntegerField(null=True, blank=True, verbose_name="開始年期")
    end_year = models.IntegerField(null=True, blank=True, verbose_name="結束年期")

    class Meta:
        verbose_name = "社團職務"
        verbose_name_plural = "社團職務"

    def __str__(self):
        return f"{self.user.username} - {self.organization_name} ({self.position})"

class EmploymentRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employment_records')
    start_date = models.DateField(verbose_name="開始日期")
    end_date = models.DateField(null=True, blank=True, verbose_name="結束日期")
    department = models.CharField(max_length=100, verbose_name="部門")
    position = models.CharField(max_length=100, verbose_name="職位")
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time_teacher', '全職教學人員(教師證)'),
        ('part_time_teacher', '兼職教學人員(教師證)'),
        ('full_time_staff', '全職職員(職員證)'),
        ('part_time_staff', '兼職職員(職員證)'),
        ('part_time_staff_no_id', '兼職職員'),
        ('full_time_janitor', '全職校工(職員證)'),
        ('part_time_janitor', '兼職校工'),
        ('intern_staff', '兼職實習生(職員證)'),
        ('short_term_intern', '短期實習生'),
        ('substitute_teacher', '代課老師'),
        ('partner_company', '合作單位(請註明公司名)'),
        ('leisure_activity_tutor', '正課餘暇導師'),
        ('co_curricular_teacher', '聯課活動導師'),
        ('volunteer_co_curricular', '義務聯課活動導師'),
        ('part_time_librarian', '圖書館兼職人員'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employment_records', verbose_name="員工編號")
    employment_type = models.CharField(max_length=50, choices=EMPLOYMENT_TYPE_CHOICES, verbose_name="受聘形式")
    count_for_seniority = models.BooleanField(default=False, help_text='是否計入有效年資')
    remark = models.TextField(blank=True, verbose_name="備註")
    count_for_seniority = models.BooleanField(default=True, verbose_name="計入年資")

    class Meta:
        verbose_name = "在職記錄"
        verbose_name_plural = "在職記錄"

# 確認模型類名為OnboardingApplication
class OnboardingApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', '待審核'),
        ('approved', '已批准'),
        ('rejected', '已拒絕')
    ]
    
    # 基本資料
    name = models.CharField(max_length=100, verbose_name="姓名")
    id_number = models.CharField(max_length=50, unique=True, verbose_name="身份證號")
    mobile_phone = models.CharField(max_length=20, verbose_name="手機號碼")
    
    # 入職資料
    department = models.CharField(max_length=100, verbose_name="部門")
    position = models.CharField(max_length=100, verbose_name="職位")
    proposed_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="建議薪資")
    proposed_start_date = models.DateField(verbose_name="建議入職日期")
    
    # 審核狀態
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="狀態")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="創建時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "入職申請"
        verbose_name_plural = "入職申請"

    def __str__(self):
        return f"{self.name} - {self.department}/{self.position}"


    def clean(self):
        """檢查日期重疊"""
        super().clean()
        if self.start_date > self.end_date:
            raise ValidationError("結束日期不能早於開始日期")
        
        overlaps = EmploymentRecord.objects.filter(
            user=self.user,
            start_date__lt=self.end_date,
            end_date__gt=self.start_date
        ).exclude(id=self.id)
        
        if overlaps.exists():
            raise ValidationError("此期間已有其他聘用記錄，請檢查日期是否重疊")
