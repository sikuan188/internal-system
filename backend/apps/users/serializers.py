from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import OnboardingApplication, User, FamilyMember, EducationHistory, WorkExperience, ProfessionalQualification, SocialActivity, EmploymentRecord # 新增導入

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # 调用父类验证
        data = super().validate(attrs)
        
        # 添加额外验证逻辑
        if not self.user.is_active:
            raise serializers.ValidationError("账号未激活")
            
        if self.user.is_locked:
            raise serializers.ValidationError("账号已锁定")
            
        # 添加自定义响应数据
        data.update({
            'user_info': {
                'id': self.user.id,
                'name': self.user.get_full_name()
            }
        })
        return data


class OnboardingApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingApplication
        fields = '__all__' # 或者明確列出需要的字段，例如 ['name', 'id_number', ...]
        read_only_fields = ('status', 'created_at', 'updated_at') # 申請時狀態和時間戳應為唯讀


# 新增序列化器
class FamilyMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMember
        fields = ['name', 'relationship', 'birth_date', 'age', 'education_level', 'institution', 'alumni_class']

class EducationHistorySerializer(serializers.ModelSerializer):
    study_period = serializers.CharField(source='years') # 對應您要求的字段名
    school_name = serializers.CharField(source='school') # 對應您要求的字段名
    degree_name = serializers.CharField(source='major') # 對應您要求的字段名
    class Meta:
        model = EducationHistory
        fields = ['study_period', 'school_name', 'education_level', 'degree_name', 'certificate_date']

class WorkExperienceSerializer(serializers.ModelSerializer):
    employment_period = serializers.CharField(source='years') # 對應您要求的字段名
    organization = serializers.CharField(source='company') # 對應您要求的字段名
    class Meta:
        model = WorkExperience
        fields = ['employment_period', 'organization', 'position', 'salary']

class ProfessionalQualificationSerializer(serializers.ModelSerializer):
    qualification_name = serializers.CharField(source='name') # 對應您要求的字段名
    class Meta:
        model = ProfessionalQualification
        fields = ['qualification_name', 'issuing_organization', 'issue_date']

class SocialActivitySerializer(serializers.ModelSerializer):
    association_name = serializers.CharField(source='organization_name') # 對應您要求的字段名
    class Meta:
        model = SocialActivity
        fields = ['association_name', 'position', 'start_year', 'end_year']

class EmploymentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmploymentRecord
        fields = ['start_date', 'end_date', 'department', 'position', 'employment_type', 'count_for_seniority', 'remark']

class UserDetailSerializer(serializers.ModelSerializer):
    # 校方資料 (直接從 User 模型獲取)
    # staff_id, staff_name, employment_type, employment_type_remark, dsej_registration_status, 
    # dsej_registration_rank, entry_date, departure_date, retirement_date, position_grade, 
    # teaching_staff_salary_grade, basic_salary_points, adjusted_salary_points, 
    # provident_fund_type, remark (User 模型中的 remark)

    # 個人資料 (直接從 User 模型獲取)
    # name_chinese, name_foreign, gender, marital_status, birth_place, birth_date, origin, 
    # id_type, id_number, id_expiry_date, bank_account_number, social_security_number, 
    # home_phone, mobile_phone, address, email, alumni_class, alumni_class_year, 
    # alumni_class_duration, teacher_certificate_number, teaching_staff_rank, 
    # teaching_staff_rank_effective_date, emergency_contact_name, emergency_contact_phone, 
    # emergency_contact_relationship

    # 嵌套序列化器
    family_members = FamilyMemberSerializer(many=True, read_only=True)
    education_history = EducationHistorySerializer(many=True, read_only=True)
    work_experience = WorkExperienceSerializer(many=True, read_only=True)
    professional_qualifications = ProfessionalQualificationSerializer(many=True, read_only=True)
    social_activities = SocialActivitySerializer(many=True, read_only=True)
    employment_records = EmploymentRecordSerializer(many=True, read_only=True)

    # 在職年資
    calculated_seniority = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            # 校方資料
            'staff_id', 'staff_name', 'employment_type', 'employment_type_remark', 
            'dsej_registration_status', 'dsej_registration_rank', 'entry_date', 'departure_date', 
            'retirement_date', 'position_grade', 'teaching_staff_salary_grade', 
            'basic_salary_points', 'adjusted_salary_points', 'provident_fund_type', 'remark',
            # 個人資料
            'name_chinese', 'name_foreign', 'gender', 'marital_status', 'birth_place', 'birth_date', 
            'origin', 'id_type', 'id_number', 'id_expiry_date', 'bank_account_number', 
            'social_security_number', 'home_phone', 'mobile_phone', 'address', 'email', 
            'alumni_class', 'alumni_class_year', 'alumni_class_duration', 
            'teacher_certificate_number', 'teaching_staff_rank', 'teaching_staff_rank_effective_date', 
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            # 關聯資料
            'family_members', 'education_history', 'work_experience', 
            'professional_qualifications', 'social_activities', 'employment_records',
            # 計算字段
            'calculated_seniority',
            # User模型本身的其他必要字段，例如 username, is_active 等，如果需要的話
            'username', 'first_name', 'last_name', 'is_active', 'position', 'teaching_grade' # 'position' 和 'teaching_grade' 是 User 模型頂層的
        ]
        # 確保 User 模型中 'remark' 字段不會與校方資料的 'remark' 衝突，如果 User 模型頂層的 remark 指的是校方資料的備註，則無需額外處理。
        # 如果有其他 User 模型的 remark，需要明確區分。

    def get_calculated_seniority(self, obj):
        return obj.calculate_seniority()