from django.contrib import admin
from .models import Staff, FamilyMember, EducationHistory, WorkExperience, ProfessionalQualification # 導入其他模型

# Inline Admins for related models
class FamilyMemberInline(admin.TabularInline):
    model = FamilyMember
    extra = 1

class EducationHistoryInline(admin.TabularInline):
    model = EducationHistory
    extra = 1

class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    extra = 1

class ProfessionalQualificationInline(admin.TabularInline):
    model = ProfessionalQualification
    extra = 1

# Register your models here.

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'staff_name', 'name_chinese', 'employment_type', 'entry_date', 'email')
    search_fields = ('staff_id', 'staff_name', 'name_chinese', 'email')
    list_filter = ('employment_type', 'entry_date')
    ordering = ('staff_id',)

    fieldsets = (
        ('校方資料', {
            'fields': ('staff_id', 'staff_name', 'position', 'teaching_grade', 'employment_type', 'employment_type_remark', 
                       'dsej_registration_status', 'dsej_registration_rank', 'entry_date', 'departure_date', 
                       'retirement_date', 'position_grade', 'teaching_staff_salary_grade', 'basic_salary_points', 
                       'adjusted_salary_points', 'provident_fund_type', 'remark', 'seniority_calculation_effective')
        }),
        ('個人資料', {
            'fields': ('name_chinese', 'name_foreign', 'gender', 'marital_status', 'birth_place', 'birth_date', 'origin',
                       'id_type', 'id_number', 'id_expiry_date', 'is_macao_pr', 'bank_account_number', 
                       'social_security_number', 'home_phone', 'mobile_phone', 'address', 'email', 
                       'alumni_class', 'alumni_class_year', 'alumni_class_duration', 'teacher_certificate_number', 
                       'teaching_staff_rank', 'teaching_staff_rank_effective_date', 'emergency_contact_name', 
                       'emergency_contact_phone', 'emergency_contact_relationship')
        }),
    )
    # add_fieldsets 用於創建新員工時的表單佈局，可以與 fieldsets 相同或簡化
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('staff_id', 'staff_name', 'name_chinese', 'name_foreign', 'email', 'employment_type', 'entry_date'), # 初始創建時可能只需要部分核心字段
        }),
    )
    inlines = [FamilyMemberInline, EducationHistoryInline, WorkExperienceInline, ProfessionalQualificationInline] # 添加其他 Inlines

# 註冊其他直接管理的模型 (如果有的話，但看起來大部分都是 Inline)
# admin.site.register(FamilyMember) # 如果也想單獨管理家庭成員，可以這樣註冊
