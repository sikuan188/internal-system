from django.db import models
from django.utils import timezone
# 如果 User 模型中有一些 choices 或常量也需要在 Staff 模型中使用，可以考慮將它們移到一個公共的地方或在 Staff 模型中重新定義

class Staff(models.Model):
    # 校方資料 - 從原 User 模型遷移過來
    staff_id = models.CharField(max_length=20, unique=True, verbose_name="員工編號")
    staff_name = models.CharField(max_length=100, verbose_name="員工姓名")
    position = models.CharField('職稱', max_length=100, blank=True, null=True)
    teaching_grade = models.CharField('任教年級', max_length=100, blank=True, null=True)
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
    employment_type = models.CharField(max_length=50, choices=EMPLOYMENT_TYPE_CHOICES, blank=True, verbose_name="受聘形式")
    employment_type_remark = models.CharField(max_length=255, blank=True, verbose_name="受聘形式備註")
    dsej_registration_status = models.CharField(max_length=50, blank=True, verbose_name="教青局登記資料")
    dsej_registration_rank = models.CharField(max_length=50, blank=True, verbose_name="教青局登記職級")
    entry_date = models.DateField(null=True, blank=True, verbose_name="入職日期")
    departure_date = models.DateField(null=True, blank=True, verbose_name="離職日期")
    retirement_date = models.DateField(null=True, blank=True, verbose_name="退休日期")
    position_grade = models.CharField(max_length=50, blank=True, verbose_name="職稱/任教年級")
    teaching_staff_salary_grade = models.CharField(max_length=50, blank=True, verbose_name="教學人員薪級")
    basic_salary_points = models.IntegerField(null=True, blank=True, verbose_name="薪級基本點數")
    adjusted_salary_points = models.IntegerField(null=True, blank=True, verbose_name="調整增薪點數")
    provident_fund_type = models.CharField(max_length=50, blank=True, verbose_name="公積金類別")
    remark = models.TextField(blank=True, verbose_name="備註")
    seniority_calculation_effective = models.BooleanField(default=True, verbose_name="年資計算有效")
    # seniority 字段可以保留，或者通過 EmploymentRecord 動態計算

    # 個人資料 - 從原 User 模型遷移過來
    name_chinese = models.CharField(max_length=100, blank=True, verbose_name="員工姓名(中文)")
    name_foreign = models.CharField(max_length=100, verbose_name="員工姓名(外文)") # 根據您的需求，如果外文名不是必須的，可以設 blank=True
    gender = models.CharField(max_length=10, blank=True, verbose_name="性別")
    marital_status = models.CharField(max_length=20, blank=True, verbose_name="婚姻狀況")
    birth_place = models.CharField(max_length=100, blank=True, verbose_name="出生地點")
    birth_date = models.DateField(null=True, blank=True, verbose_name="出生日期")
    origin = models.CharField(max_length=100, blank=True, verbose_name="籍貫")

    ID_TYPE_CHOICES = [
        ('macao_id', '澳門居民身份證'),
        ('passport', '護照'),
        ('other', '其他'),
    ]
    id_type = models.CharField(max_length=50, blank=True, verbose_name="證件類別", choices=ID_TYPE_CHOICES)
    id_number = models.CharField(max_length=50, unique=True, verbose_name="證件號碼") # 考慮是否真的需要 unique=True，如果不同員工可能有相同證件號（例如不同國家的護照號）
    id_expiry_date = models.DateField(null=True, blank=True, verbose_name="證件有效期")
    is_macao_pr = models.BooleanField(default=True, verbose_name="澳門永久性居民")

    bank_account_number = models.CharField(max_length=50, blank=True, verbose_name="大豐銀行澳門幣戶口賬號")
    social_security_number = models.CharField(max_length=50, blank=True, verbose_name="社保號碼")
    home_phone = models.CharField(max_length=20, blank=True, verbose_name="住宅電話")
    mobile_phone = models.CharField(max_length=20, blank=True, verbose_name="手提電話")
    address = models.CharField(max_length=255, blank=True, verbose_name="住址")
    # email 字段可以保留，用於聯繫，但不作為登錄憑證
    email = models.EmailField(blank=True, verbose_name="電郵")
    alumni_class = models.CharField(max_length=100, blank=True, verbose_name="級社(校友適用)")
    alumni_class_year = models.IntegerField(null=True, blank=True, verbose_name="級社_年級(校友適用)")
    alumni_class_duration = models.CharField(max_length=50, blank=True, verbose_name="級社_年數(校友適用)")
    teacher_certificate_number = models.CharField(max_length=50, blank=True, verbose_name="教師證號碼")
    teaching_staff_rank = models.CharField(max_length=50, blank=True, verbose_name="教學人員職級")
    teaching_staff_rank_effective_date = models.DateField(null=True, blank=True, verbose_name="教學人員職級生效日期")
    emergency_contact_name = models.CharField(max_length=100, blank=True, verbose_name="緊急聯絡人姓名")
    emergency_contact_phone = models.CharField(max_length=20, blank=True, verbose_name="緊急聯絡人電話")
    emergency_contact_relationship = models.CharField(max_length=50, blank=True, verbose_name="與緊急聯絡人之關係")

    # 如果需要，可以添加創建時間和更新時間字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="創建時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "教職員工"
        verbose_name_plural = "教職員工"

    def __str__(self):
        return f"{self.staff_name} ({self.staff_id})"

    def calculate_seniority(self):
        """Calculate and return the staff's seniority based on EmploymentRecord."""
        total_days = 0
        # 假設 EmploymentRecord 模型的外鍵已更新為指向 Staff
        records = self.employment_records.filter(count_for_seniority=True).order_by('start_date')

        if not records:
            return "0年0月"

        for record in records:
            start_date = record.start_date
            end_date = record.end_date if record.end_date else timezone.now().date()
            
            if start_date:
                delta = end_date - start_date
                total_days += delta.days
        
        if total_days < 0:
            total_days = 0
            
        years = total_days // 365
        remaining_days = total_days % 365
        months = remaining_days // 30
        
        return f"{years}年{months}月"

# --- 以下是關聯模型，需要將外鍵指向 Staff --- 

class FamilyMember(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='family_members', verbose_name="員工編號")
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
        return f"{self.staff.staff_name} - {self.name} ({self.relationship})"

class EducationHistory(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='education_history', verbose_name="員工編號")
    years = models.CharField(max_length=50, blank=True, verbose_name="就讀年份")
    school = models.CharField(max_length=255, verbose_name="就讀學校")
    education_level = models.CharField(max_length=100, verbose_name="教育程度")
    major = models.CharField(max_length=255, blank=True, verbose_name="專科學位名稱")
    certificate_date = models.DateField(null=True, blank=True, verbose_name="獲得證書日期")
    is_overseas_study = models.BooleanField(default=False, verbose_name="是否留學經歷")

    class Meta:
        verbose_name = "學歷狀況"
        verbose_name_plural = "學歷狀況"

    def __str__(self):
        return f"{self.staff.staff_name} - {self.school} ({self.education_level})"

# WorkExperience, ProfessionalQualification, SocialActivity, TrainingRecord, 
# AwardRecord, PublicationRecord, HealthRecord, LeaveRecord, EmploymentRecord 
# 這些模型也需要類似地將 ForeignKey 從 User 修改為 Staff
# 例如 EmploymentRecord:
class EmploymentRecord(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='employment_records', verbose_name="員工")
    # ... 其他字段保持不變 ...
    start_date = models.DateField(verbose_name="開始日期")
    end_date = models.DateField(null=True, blank=True, verbose_name="結束日期")
    position = models.CharField(max_length=100, verbose_name="職位")
    department = models.CharField(max_length=100, blank=True, verbose_name="部門")
    employment_type = models.CharField(max_length=50, choices=Staff.EMPLOYMENT_TYPE_CHOICES, blank=True, verbose_name="受聘形式") # 可以引用 Staff 模型的 CHOICES
    count_for_seniority = models.BooleanField(default=True, verbose_name="計算年資")
    remark = models.TextField(blank=True, verbose_name="備註")

    class Meta:
        verbose_name = "僱佣記錄"
        verbose_name_plural = "僱佣記錄"
        ordering = ['start_date']

    def __str__(self):
        return f"{self.staff.staff_name} - {self.position} ({self.start_date} to {self.end_date or 'Present'})"

# 請您繼續修改其他關聯模型的 ForeignKey，將它們指向 Staff 模型。
# 例如 ProfessionalQualification:
class ProfessionalQualification(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='professional_qualifications', verbose_name="員工編號")
    name = models.CharField(max_length=255, verbose_name="專業資格名稱")
    issuing_organization = models.CharField(max_length=255, blank=True, verbose_name="頒發機構")
    issue_date = models.DateField(null=True, blank=True, verbose_name="頒授日期")

    class Meta:
        verbose_name = "專業資格"
        verbose_name_plural = "專業資格"

    def __str__(self):
        return f"{self.staff.staff_name} - {self.name}"

# ... 其他關聯模型 (SocialActivity, TrainingRecord, AwardRecord, PublicationRecord, HealthRecord, LeaveRecord) 也需要類似修改 ...
