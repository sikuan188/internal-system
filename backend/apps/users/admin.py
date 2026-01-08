from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, FamilyMember, EducationHistory, WorkExperience, ProfessionalQualification, SocialActivity
from .forms import CustomUserCreationForm
from .models import OnboardingApplication
from .models import EmploymentRecord


class FamilyMemberInline(admin.TabularInline):
    model = FamilyMember
    extra = 1
    verbose_name = "家庭成員"
    verbose_name_plural = "家庭成員"


class EducationHistoryInline(admin.TabularInline):
    model = EducationHistory
    extra = 1
    verbose_name = "學歷狀況"
    verbose_name_plural = "學歷狀況"


class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    extra = 1
    verbose_name = "工作經驗"
    verbose_name_plural = "工作經驗"


class ProfessionalQualificationInline(admin.TabularInline):
    model = ProfessionalQualification
    extra = 1
    verbose_name = "專業資格"
    verbose_name_plural = "專業資格"


class SocialActivityInline(admin.TabularInline):
    model = SocialActivity
    extra = 1
    verbose_name = "社團職務"
    verbose_name_plural = "社團職務"


class EmploymentRecordInline(admin.TabularInline):
    model = EmploymentRecord
    extra = 1
    verbose_name = "在職記錄"
    verbose_name_plural = "在職記錄"

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # add_form = CustomUserCreationForm # 如果有自定義創建表單
    # form = CustomUserChangeForm # 如果有自定義修改表單
    model = User
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']

    # fieldsets 和 add_fieldsets 會繼承自 BaseUserAdmin
    # 您可以根據簡化後的 User 模型進行調整
    # 例如，移除員工相關的字段組
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password', 'password2'), # 根據您的 UserCreationForm
        }),
    )
    # 由於員工信息相關的 Inline 已經移到 StaffAdmin，這裡應該移除它們
    inlines = [] 

    def display_seniority(self, obj):
        return obj.calculate_seniority() 
    display_seniority.short_description = '在職年資'
    
    def display_employment_type(self, obj):
        latest_record = obj.employment_records.order_by('-start_date').first() # 獲取最新的聘用記錄，通常按開始日期排序更合適
        if latest_record:
            # 使用 get_FOO_display() 方法獲取 choices 的顯示值
            return latest_record.get_employment_type_display()
        return '無記錄'
    display_employment_type.short_description = '受聘形式'
    
    def display_position_grade(self, obj):
        # 假設User模型有position和teaching_grade字段
        position = getattr(obj, 'position', '無')
        grade = getattr(obj, 'teaching_grade', '無')
        return f"{position}/{grade}"
    display_position_grade.short_description = '職稱/任教年級'
    add_form = CustomUserCreationForm
    fieldsets = (
        ("校方資料", {
            "fields": (
                "staff_id",
                "staff_name",
                "employment_type",
                "employment_type_remark",
                "dsej_registration_status",
                "dsej_registration_rank",
                "entry_date",
                "departure_date",
                "retirement_date",
                "position_grade",
                "teaching_staff_salary_grade",
                "basic_salary_points",
                "adjusted_salary_points",
                "provident_fund_type",
                "remark",
                "seniority", # 在此處添加 seniority 字段
                "seniority_calculation_effective", #如果需要在 admin 修改，也添加此字段
            )
        }),
        ("個人資料", {
            "fields": (
                "name_chinese",
                "name_foreign",
                "gender",
                "marital_status",
                "birth_place",
                "birth_date",
                "origin",
                "id_type",
                "id_number",
                "id_expiry_date",
                "bank_account_number",
                "social_security_number",
                "home_phone",
                "mobile_phone",
                "address",
                "email",
                "alumni_class",
                "alumni_class_year",
                "alumni_class_duration",
                "teacher_certificate_number",
                "teaching_staff_rank",
                "teaching_staff_rank_effective_date",
                "emergency_contact_name",
                "emergency_contact_phone",
                "emergency_contact_relationship",
            )
        }),
    )

    add_fieldsets = (
        ("校方資料", {
            "fields": (
                "staff_id",
                "staff_name",
                "employment_type",
                "employment_type_remark",
                "dsej_registration_status",
                "dsej_registration_rank",
                "entry_date",
                # "departure_date", # 新增時通常不需要離職日期
                # "retirement_date", # 新增時通常不需要退休日期
                "position_grade",
                "teaching_staff_salary_grade",
                "basic_salary_points",
                "adjusted_salary_points",
                "provident_fund_type",
                "remark",
                # "seniority", # 新增時年資通常為0或不顯示
                "seniority_calculation_effective",
            )
        }),
        ("個人資料", {
            "fields": (
                "name_chinese",
                "name_foreign",
                "gender",
                "marital_status",
                "birth_place",
                "birth_date",
                "origin",
                "id_type",
                "id_number",
                "id_expiry_date",
                "bank_account_number",
                "social_security_number",
                "home_phone",
                "mobile_phone",
                "address",
                "email",
                "alumni_class",
                "alumni_class_year",
                "alumni_class_duration",
                "teacher_certificate_number",
                "teaching_staff_rank",
                "teaching_staff_rank_effective_date",
                "emergency_contact_name",
                "emergency_contact_phone",
                "emergency_contact_relationship",
            )
        }),
    )

    # 移除這裡重複的 list_display, search_fields, ordering
    # list_display = ("staff_id", "staff_name", "name_foreign")
    # search_fields = ("staff_id", "staff_name", "name_foreign")
    # ordering = ("staff_id",)
    inlines = [
        FamilyMemberInline,
        EducationHistoryInline,
        WorkExperienceInline,
        ProfessionalQualificationInline,
        SocialActivityInline,
        EmploymentRecordInline, # 確保 EmploymentRecordInline 也被添加，以便在 User Admin 中直接管理在職記錄
    ]

    def save_model(self, request, obj, form, change):
        print(f"Saving object: {obj.__dict__}")
        print(f"Form data: {form.cleaned_data}")
        try:
            super().save_model(request, obj, form, change)
            print("Object saved successfully")
        except Exception as e:
            print(f"Error saving object: {e}")
            # 在這裡可以設置斷點進行調試
            # import pdb; pdb.set_trace()
            raise # 重新拋出異常，以便 Django 正常處理
        # 自動生成 username 為 staff_id
        obj.username = obj.staff_id
        super().save_model(request, obj, form, change)

admin.site.register(FamilyMember)
admin.site.register(EducationHistory)
admin.site.register(WorkExperience)
admin.site.register(ProfessionalQualification)
admin.site.register(SocialActivity)


from .models import OnboardingApplication

@admin.register(OnboardingApplication)
class OnboardingApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'position', 'proposed_start_date', 'status')
    list_filter = ('status', 'department')
    search_fields = ('name', 'id_number')
    date_hierarchy = 'proposed_start_date'


@admin.register(EmploymentRecord)
class EmploymentRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'has_overlap')
    
    def has_overlap(self, obj):
        overlaps = EmploymentRecord.objects.filter(
            user=obj.user,
            start_date__lt=obj.end_date,
            end_date__gt=obj.start_date
        ).exclude(id=obj.id)
        return "⚠️ 需人工核查" if overlaps.exists() else ""
    has_overlap.short_description = "重疊檢查"
