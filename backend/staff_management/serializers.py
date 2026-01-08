from rest_framework import serializers
from .models import (
    StaffProfile, FamilyMember, EducationBackground, WorkExperience, # 更正: Education -> EducationBackground
    ProfessionalQualification, AssociationPosition, EmploymentRecord
)

class FamilyMemberSerializer(serializers.ModelSerializer):
    # 讓所有字段可選以支持靈活提交
    name = serializers.CharField(required=False, allow_blank=True)
    relationship = serializers.CharField(required=False, allow_blank=True)
    birth_date = serializers.DateField(required=False, allow_null=True)
    age = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = FamilyMember
        fields = '__all__'
        read_only_fields = ('staff',)

class EducationBackgroundSerializer(serializers.ModelSerializer): # 更正: EducationSerializer -> EducationBackgroundSerializer
    # 明確指定布尔值字段的序列化方式
    is_phd = serializers.BooleanField()
    is_master = serializers.BooleanField()
    is_overseas_study = serializers.BooleanField()
    
    class Meta:
        model = EducationBackground # 更正: Education -> EducationBackground
        # 確保 'is_phd'、'is_master' 和 'is_overseas_study' 包含在此處
        fields = ['study_period', 'school_name', 'education_level', 'degree_name', 'certificate_date', 'is_phd', 'is_master', 'is_overseas_study'] 
        read_only_fields = ('staff',)

class WorkExperienceSerializer(serializers.ModelSerializer):
    # 讓工作經驗字段可選
    employment_period = serializers.CharField(required=False, allow_blank=True)
    organization = serializers.CharField(required=False, allow_blank=True)
    position = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = WorkExperience
        fields = '__all__'
        read_only_fields = ('staff',)

class ProfessionalQualificationSerializer(serializers.ModelSerializer):
    # 讓專業資格字段可選
    qualification_name = serializers.CharField(required=False, allow_blank=True)
    issuing_organization = serializers.CharField(required=False, allow_blank=True)
    issue_date = serializers.DateField(required=False, allow_null=True)
    
    class Meta:
        model = ProfessionalQualification
        fields = '__all__'
        read_only_fields = ('staff',)

class AssociationPositionSerializer(serializers.ModelSerializer):
    # 讓社團職務字段可選
    association_name = serializers.CharField(required=False, allow_blank=True)
    position = serializers.CharField(required=False, allow_blank=True) 
    start_year = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = AssociationPosition
        fields = '__all__'
        read_only_fields = ('staff',)

class EmploymentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmploymentRecord
        fields = '__all__'
        read_only_fields = ('staff_profile',)

class StaffProfileSerializer(serializers.ModelSerializer):
    family_members = FamilyMemberSerializer(many=True, required=False)
    education_backgrounds = EducationBackgroundSerializer(many=True, required=False)
    work_experiences = WorkExperienceSerializer(many=True, required=False)
    professional_qualifications = ProfessionalQualificationSerializer(many=True, required=False)
    association_positions = AssociationPositionSerializer(many=True, required=False)
    employment_records = EmploymentRecordSerializer(many=True, required=False)
    
    # 自定義員工照片欄位，確保返回正確的URL
    profile_picture = serializers.SerializerMethodField()
    
    # 明確指定布尔值字段的序列化方式
    is_foreign_national = serializers.BooleanField()
    is_master = serializers.BooleanField()
    is_phd = serializers.BooleanField()
    is_overseas_study = serializers.BooleanField()
    is_active = serializers.BooleanField()
    
    # 讓一些關鍵字段可選，支持分階段填寫
    mobile_phone = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    emergency_contact_name = serializers.CharField(required=False, allow_blank=True)
    emergency_contact_phone = serializers.CharField(required=False, allow_blank=True)
    emergency_contact_relationship = serializers.CharField(required=False, allow_blank=True)
    teaching_staff_rank_effective_date = serializers.DateField(required=False, allow_null=True)
    
    def get_profile_picture(self, obj):
        """返回員工照片的完整URL"""
        if obj.profile_picture:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None

    class Meta:
        model = StaffProfile
        fields = [
            'user_account', # 新增 (如果需要)
            'created_by_admin', # 新增 (如果需要)
            'staff_id', 
            'staff_name', 
            'employment_type', # 新增
            'employment_type_remark', # 新增
            'dsej_registration_status', # 新增
            'dsej_registration_rank', # 新增
            'entry_date', # 新增
            'departure_date', # 新增
            'retirement_date', # 新增
            'position_grade', # 新增
            'teaching_staff_salary_grade', # 新增
            'basic_salary_points', # 新增
            'adjusted_salary_points', # 新增
            'provident_fund_type', # 新增
            'remark', # 新增
            'contract_number', # 新增
            'is_active', # 新增
            'school_seniority_description', 
            'name_chinese', 
            'name_foreign', 
            'gender', 
            'marital_status', 
            'birth_place', 
            'birth_date', 
            'origin',
            'id_type', 
            'id_number', 
            'id_expiry_date', 
            'is_foreign_national', # 保留一個即可
            'is_master',  # 全局教育標記
            'is_phd',     # 全局教育標記
            'is_overseas_study',  # 全局教育標記
            'bank_account_number',
            'social_security_number', # 新增
            'home_phone', # 新增
            'mobile_phone', # 新增
            'address', # 新增
            'email', # 新增
            'profile_picture', # 新增員工照片欄位
            'alumni_class', # 新增
            'alumni_class_year', # 新增
            'alumni_class_duration', # 新增
            'teacher_certificate_number', # 新增
            'teaching_staff_rank', # 新增
            'teaching_staff_rank_effective_date', # 新增
            'emergency_contact_name', # 新增
            'emergency_contact_phone', # 新增
            'emergency_contact_relationship', # 新增
            'family_members',
            'education_backgrounds',
            'work_experiences', 
            'professional_qualifications',
            'association_positions',
            'employment_records'
        ]
        # 或者，如果您想包含所有模型字段以及關聯字段，可以使用 '__all__' 但這通常不推薦用於生產環境，因為它可能會暴露過多數據。
        # 如果使用 '__all__'，您需要確保所有關聯字段都已正確設置並且您希望它們全部被序列化。
        # fields = '__all__'
        read_only_fields = ('staff_profile',)

    def create(self, validated_data):
        family_members_data = validated_data.pop('family_members', [])
        education_backgrounds_data = validated_data.pop('education_backgrounds', []) # 更正: education_records -> education_backgrounds
        work_experiences_data = validated_data.pop('work_experiences', [])
        professional_qualifications_data = validated_data.pop('professional_qualifications', [])
        association_positions_data = validated_data.pop('association_positions', [])
        employment_records_data = validated_data.pop('employment_records', [])

        staff_profile = StaffProfile.objects.create(**validated_data)

        # 只有在數據不為空且有有效內容時才創建關聯記錄
        for fm_data in family_members_data:
            if fm_data.get('name'):  # 只有姓名不為空才創建
                FamilyMember.objects.create(staff=staff_profile, **fm_data)
        for edu_data in education_backgrounds_data: # 更正: education_records_data -> education_backgrounds_data
            if edu_data.get('school_name'):  # 只有學校名稱不為空才創建
                EducationBackground.objects.create(staff=staff_profile, **edu_data) # 更正: Education -> EducationBackground
        for we_data in work_experiences_data:
            if we_data.get('organization'):  # 只有機構名稱不為空才創建
                WorkExperience.objects.create(staff=staff_profile, **we_data)
        for pq_data in professional_qualifications_data:
            if pq_data.get('qualification_name'):  # 只有資格名稱不為空才創建
                ProfessionalQualification.objects.create(staff=staff_profile, **pq_data)
        for ap_data in association_positions_data:
            if ap_data.get('association_name'):  # 只有社團名稱不為空才創建
                AssociationPosition.objects.create(staff=staff_profile, **ap_data)
        for er_data in employment_records_data:
            EmploymentRecord.objects.create(staff=staff_profile, **er_data)
            
        return staff_profile

    def update(self, instance, validated_data):
        # Pop nested data fields
        family_members_data = validated_data.pop('family_members', None)
        education_backgrounds_data = validated_data.pop('education_backgrounds', None) # 更正: education_records -> education_backgrounds
        work_experiences_data = validated_data.pop('work_experiences', None)
        professional_qualifications_data = validated_data.pop('professional_qualifications', None)
        association_positions_data = validated_data.pop('association_positions', None)
        employment_records_data = validated_data.pop('employment_records', None)

        # Update StaffProfile instance
        instance = super().update(instance, validated_data)

        # Handle updates for nested fields
        # For simplicity, this example replaces existing related objects.
        # A more robust implementation might update existing objects or handle deletions.

        if family_members_data is not None:
            instance.family_members.all().delete()
            for fm_data in family_members_data:
                if fm_data.get('name'):
                    FamilyMember.objects.create(staff=instance, **fm_data)
        
        if education_backgrounds_data is not None: # 更正: education_records_data -> education_backgrounds_data
            instance.education_backgrounds.all().delete() # 更正: education_records -> education_backgrounds
            for edu_data in education_backgrounds_data: # 更正: education_records_data -> education_backgrounds_data
                if edu_data.get('school_name'):
                    EducationBackground.objects.create(staff=instance, **edu_data) # 更正: Education -> EducationBackground

        if work_experiences_data is not None:
            instance.work_experiences.all().delete()
            for we_data in work_experiences_data:
                if we_data.get('organization'):
                    WorkExperience.objects.create(staff=instance, **we_data)

        if professional_qualifications_data is not None:
            instance.professional_qualifications.all().delete()
            for pq_data in professional_qualifications_data:
                if pq_data.get('qualification_name'):
                    ProfessionalQualification.objects.create(staff=instance, **pq_data)

        if association_positions_data is not None:
            instance.association_positions.all().delete()
            for ap_data in association_positions_data:
                if ap_data.get('association_name'):
                    AssociationPosition.objects.create(staff=instance, **ap_data)

        if employment_records_data is not None:
            instance.employment_records.all().delete()
            for er_data in employment_records_data:
                EmploymentRecord.objects.create(staff=instance, **er_data)

        return instance