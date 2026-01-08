from rest_framework import serializers
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import re
from datetime import date
from .models import (
    StaffApplication, 
    ApplicationFamilyMember, 
    ApplicationEducation, 
    ApplicationWorkExperience, 
    ApplicationProfessionalQualification, 
    ApplicationAssociationPosition
)

class ApplicationFamilyMemberSerializer(serializers.ModelSerializer):
    """
    家庭成員序列化器 - 所有欄位都不是必填項，允許空值
    """
    name = serializers.CharField(required=False, allow_blank=True)
    relationship = serializers.CharField(required=False, allow_blank=True)
    birth_date = serializers.DateField(required=False, allow_null=True)
    age = serializers.IntegerField(required=False, allow_null=True)
    education_level = serializers.CharField(required=False, allow_blank=True)
    institution = serializers.CharField(required=False, allow_blank=True)
    alumni_class = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = ApplicationFamilyMember
        fields = ['name', 'relationship', 'birth_date', 'age', 'education_level', 'institution', 'alumni_class']

class ApplicationEducationSerializer(serializers.ModelSerializer):
    """
    學歷狀況序列化器 - 所有欄位都不是必填項，允許空值
    """
    study_period = serializers.CharField(required=False, allow_blank=True)
    school_name = serializers.CharField(required=False, allow_blank=True)
    education_level = serializers.CharField(required=False, allow_blank=True)
    degree_name = serializers.CharField(required=False, allow_blank=True)
    certificate_date = serializers.DateField(required=False, allow_null=True)
    is_phd = serializers.BooleanField(required=False)
    is_master = serializers.BooleanField(required=False)
    is_overseas_study = serializers.BooleanField(required=False)
    
    class Meta:
        model = ApplicationEducation
        fields = ['study_period', 'school_name', 'education_level', 'degree_name', 'certificate_date', 'is_phd', 'is_master', 'is_overseas_study']

class ApplicationWorkExperienceSerializer(serializers.ModelSerializer):
    """
    工作經驗序列化器 - 所有欄位都不是必填項，允許空值
    """
    employment_period = serializers.CharField(required=False, allow_blank=True)
    organization = serializers.CharField(required=False, allow_blank=True)
    position = serializers.CharField(required=False, allow_blank=True)
    salary = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = ApplicationWorkExperience
        fields = ['employment_period', 'organization', 'position', 'salary']

class ApplicationProfessionalQualificationSerializer(serializers.ModelSerializer):
    """
    專業資格序列化器 - 所有欄位都不是必填項，允許空值
    """
    qualification_name = serializers.CharField(required=False, allow_blank=True)
    issuing_organization = serializers.CharField(required=False, allow_blank=True)
    issue_date = serializers.DateField(required=False, allow_null=True)
    
    class Meta:
        model = ApplicationProfessionalQualification
        fields = ['qualification_name', 'issuing_organization', 'issue_date']

class ApplicationAssociationPositionSerializer(serializers.ModelSerializer):
    """
    社團職務序列化器 - 所有欄位都不是必填項，允許空值
    """
    association_name = serializers.CharField(required=False, allow_blank=True)
    position = serializers.CharField(required=False, allow_blank=True)
    start_year = serializers.CharField(required=False, allow_blank=True)
    end_year = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = ApplicationAssociationPosition
        fields = ['association_name', 'position', 'start_year', 'end_year']

class StaffApplicationSerializer(serializers.ModelSerializer):
    """
    員工申請序列化器 - 只對真正必要的字段進行驗證
    """
    family_members = ApplicationFamilyMemberSerializer(many=True, required=False)
    educations = ApplicationEducationSerializer(many=True, required=False)
    work_experiences = ApplicationWorkExperienceSerializer(many=True, required=False)
    professional_qualifications = ApplicationProfessionalQualificationSerializer(many=True, required=False)
    association_positions = ApplicationAssociationPositionSerializer(many=True, required=False)
    
    # 明確設置非必填字段
    mobile_phone = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    teaching_staff_rank_effective_date = serializers.DateField(required=False, allow_null=True)
    emergency_contact_name = serializers.CharField(required=False, allow_blank=True)
    emergency_contact_phone = serializers.CharField(required=False, allow_blank=True)
    emergency_contact_relationship = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = StaffApplication
        fields = [
            'submission_id', 'application_date', 'status', 
            'name_chinese', 'name_foreign', 'gender', 'marital_status', 'birth_place', 'birth_date', 'origin',
            'id_type', 'id_number', 'id_expiry_date',
            'bank_account_number', 'social_security_number', 
            'home_phone', 'mobile_phone', 'address', 'email',
            'alumni_class', 'alumni_class_year', 'alumni_class_duration',
            'teacher_certificate_number', 'teaching_staff_rank', 'teaching_staff_rank_effective_date',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            'family_members', 'educations', 'work_experiences', 'professional_qualifications', 'association_positions',
        ]
        read_only_fields = ('submission_id', 'application_date', 'status')

    def validate_name_chinese(self, value):
        """驗證中文姓名 - 非必填項"""
        return value.strip() if value else ""
    
    def validate_name_foreign(self, value):
        """驗證外文姓名 - 非必填項"""
        return value.strip() if value else ""
    
    def validate_gender(self, value):
        """驗證性別 - 非必填項"""
        if value and value not in ['M', 'F']:
            raise serializers.ValidationError("性別必須是 M 或 F Gender must be M or F")
        return value
    
    def validate_birth_date(self, value):
        """驗證出生日期 - 非必填項"""
        if value and value > date.today():
            raise serializers.ValidationError("出生日期不能是未來日期 Birth date cannot be in the future")
        return value
    
    def validate_id_number(self, value):
        """驗證證件號碼 - 非必填項"""
        return value.strip() if value else ""
    
    def validate_id_expiry_date(self, value):
        """驗證證件有效期 - 非必填項"""
        if value and value < date.today():
            raise serializers.ValidationError("證件已過期 ID has expired")
        return value

    def create(self, validated_data):
        """創建員工申請記錄"""
        family_members_data = validated_data.pop('family_members', [])
        educations_data = validated_data.pop('educations', [])
        work_experiences_data = validated_data.pop('work_experiences', [])
        professional_qualifications_data = validated_data.pop('professional_qualifications', [])
        association_positions_data = validated_data.pop('association_positions', [])

        application = StaffApplication.objects.create(**validated_data)

        # 只有在有實際數據時才創建關聯記錄
        for family_member_data in family_members_data:
            if any(family_member_data.values()):  # 檢查是否有任何非空值
                ApplicationFamilyMember.objects.create(application=application, **family_member_data)

        for education_data in educations_data:
            if any(education_data.values()):  # 檢查是否有任何非空值
                ApplicationEducation.objects.create(application=application, **education_data)

        for work_experience_data in work_experiences_data:
            if any(work_experience_data.values()):  # 檢查是否有任何非空值
                ApplicationWorkExperience.objects.create(application=application, **work_experience_data)

        for professional_qualification_data in professional_qualifications_data:
            if any(professional_qualification_data.values()):  # 檢查是否有任何非空值
                ApplicationProfessionalQualification.objects.create(application=application, **professional_qualification_data)

        for association_position_data in association_positions_data:
            if any(association_position_data.values()):  # 檢查是否有任何非空值
                ApplicationAssociationPosition.objects.create(application=application, **association_position_data)

        return application