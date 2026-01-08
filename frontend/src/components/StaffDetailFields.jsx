// ./frontend/src/components/StaffDetailFields.jsx

// 校方資料字段 (Matches StaffProfile model fields for school info)
export const schoolInfoFields = [
  { key: 'staff_id', labelKey: 'staff_id' },
  { key: 'staff_name', labelKey: 'staff_name' }, // This is StaffProfile.staff_name
  { key: 'employment_type', labelKey: 'employment_type' },
  { key: 'employment_type_remark', labelKey: 'employment_type_remark' },
  { key: 'dsej_registration_status', labelKey: 'dsej_registration_status' },
  { key: 'dsej_registration_rank', labelKey: 'dsej_registration_rank' },
  { key: 'entry_date', labelKey: 'entry_date' },
  { key: 'departure_date', labelKey: 'departure_date' },
  { key: 'retirement_date', labelKey: 'retirement_date' },
  { key: 'position_grade', labelKey: 'position_grade' },
  { key: 'teaching_staff_salary_grade', labelKey: 'teaching_staff_salary_grade' },
  { key: 'basic_salary_points', labelKey: 'basic_salary_points' },
  { key: 'adjusted_salary_points', labelKey: 'adjusted_salary_points' },
  { key: 'provident_fund_type', labelKey: 'provident_fund_type' },
  { key: 'remark', labelKey: 'remark' }, 
  { key: 'contract_number', labelKey: 'contract_number' },
  { key: 'is_active', labelKey: 'is_active', isBoolean: true }, // 標記為布爾值以便特殊顯示
  { key: 'school_seniority_description', labelKey: 'school_seniority_description' },
];

// 個人資料字段 (Matches StaffProfile model fields for personal info)
export const personalInfoFields = [
  { key: 'name_chinese', labelKey: 'name_chinese' },
  { key: 'name_foreign', labelKey: 'name_foreign' },
  { key: 'gender', labelKey: 'gender', isGender: true }, // Add isGender for special rendering
  { key: 'marital_status', labelKey: 'marital_status' },
  { key: 'birth_place', labelKey: 'birth_place' },
  { key: 'birth_date', labelKey: 'birth_date' },
  { key: 'origin', labelKey: 'origin' },
  { key: 'id_type', labelKey: 'id_type' },
  { key: 'id_number', labelKey: 'id_number' },
  { key: 'id_expiry_date', labelKey: 'id_expiry_date' },
  // { key: 'is_foreign_national', labelKey: 'is_foreign_national' }, // New, Boolean  <- REMOVE THIS LINE
  { key: 'bank_account_number', labelKey: 'bank_account_number' },
  { key: 'social_security_number', labelKey: 'social_security_number' },
  { key: 'home_phone', labelKey: 'home_phone' },
  { key: 'mobile_phone', labelKey: 'mobile_phone' },
  { key: 'address', labelKey: 'address', fullWidth: true },
  { key: 'email', labelKey: 'email' },
  { key: 'alumni_class', labelKey: 'alumni_class' },
  { key: 'alumni_class_year', labelKey: 'alumni_class_year' },
  { key: 'alumni_class_duration', labelKey: 'alumni_class_duration' },
  { key: 'teacher_certificate_number', labelKey: 'teacher_certificate_number' },
  { key: 'teaching_staff_rank', labelKey: 'teaching_staff_rank' },
  { key: 'teaching_staff_rank_effective_date', labelKey: 'teaching_staff_rank_effective_date' },
  { key: 'is_foreign_national', labelKey: 'is_foreign_national', isBoolean: true },
  { key: 'is_master', labelKey: 'is_master', isBoolean: true },
  { key: 'is_phd', labelKey: 'is_phd', isBoolean: true },
  { key: 'is_overseas_study', labelKey: 'is_overseas_study', isBoolean: true },
];

// 緊急聯絡人資料 (Matches StaffProfile fields for emergency contact)
export const emergencyContactFields = [
  { key: 'emergency_contact_name', labelKey: 'emergency_contact_name' },
  { key: 'emergency_contact_phone', labelKey: 'emergency_contact_phone' },
  { key: 'emergency_contact_relationship', labelKey: 'emergency_contact_relationship' },
];

// 家庭成員字段 (Matches FamilyMember model fields)
// Assuming backend FamilyMember model has: name, relationship, birth_date, education_level, institution, alumni_class
export const familyMemberFields = [
  { key: 'name', labelKey: 'family_member_name' }, // Use prefixed labelKey from fieldLabels.js
  { key: 'relationship', labelKey: 'family_member_relationship' },
  { key: 'birth_date', labelKey: 'family_member_birth_date' },
  // { key: 'age', labelKey: 'family_member_age' }, // Typically calculated, not stored directly
  { key: 'education_level', labelKey: 'family_member_education_level' },
  { key: 'institution', labelKey: 'family_member_institution' },
  { key: 'alumni_class', labelKey: 'family_member_alumni_class' },
];

// 學歷狀況字段 (Matches EducationBackground model fields)
export const educationBackgroundFields = [
  { key: 'study_period', labelKey: 'education_study_period' },
  { key: 'school_name', labelKey: 'education_school_name' },
  { key: 'education_level', labelKey: 'education_education_level' }, 
  { key: 'degree_name', labelKey: 'education_degree_name' },
  { key: 'certificate_date', labelKey: 'education_certificate_date' },
  { key: 'is_phd', labelKey: 'education_is_phd', isBoolean: true }, // 確保 isBoolean 標記
  { key: 'is_master', labelKey: 'education_is_master', isBoolean: true }, // 具體學歷標記
  { key: 'is_overseas_study', labelKey: 'education_is_overseas_study', isBoolean: true }, // 確保 isBoolean 標記
];

// 工作經驗字段 (Matches WorkExperience model fields)
export const workExperienceFields = [
  { key: 'employment_period', labelKey: 'work_experience_employment_period' },
  { key: 'organization', labelKey: 'work_experience_organization' },
  { key: 'position', labelKey: 'work_experience_position' },
  { key: 'salary', labelKey: 'work_experience_salary' },
];

// 專業資格字段 (Matches ProfessionalQualification model fields)
export const professionalQualificationFields = [
  { key: 'qualification_name', labelKey: 'professional_qualification_qualification_name' },
  { key: 'issuing_organization', labelKey: 'professional_qualification_issuing_organization' },
  { key: 'issue_date', labelKey: 'professional_qualification_issue_date' },
];

// 社團職務字段 (Matches AssociationPosition model fields)
export const associationPositionFields = [
  { key: 'association_name', labelKey: 'association_position_association_name' },
  { key: 'position', labelKey: 'association_position_position' },
  { key: 'start_year', labelKey: 'association_position_start_year' },
  { key: 'end_year', labelKey: 'association_position_end_year' },
];

// 聘用記錄字段 (Matches EmploymentRecord model fields - if you need to list them individually)
// Usually, employment records are a list of objects, and you might display a summary or key fields.
// If you need to display individual fields from an EmploymentRecord object, define them here.
// For now, this is a placeholder if you decide to show detailed fields of a single employment record.
export const employmentRecordFields = [
  // Example fields, adjust based on your EmploymentRecord model and what you want to show:
  // { key: 'record_entry_date', labelKey: 'employment_record_entry_date' },
  // { key: 'record_departure_date', labelKey: 'employment_record_departure_date' },
  // { key: 'record_position', labelKey: 'employment_record_position' },
  // { key: 'record_department', labelKey: 'employment_record_department' }, 
  // { key: 'record_salary', labelKey: 'employment_record_salary' },
  // { key: 'record_remark', labelKey: 'employment_record_remark' },
  // { key: 'is_valid_for_seniority', labelKey: 'employment_record_is_valid_for_seniority' },
  // For now, let's assume the renderArrayData in StaffDetailSection handles EmploymentRecord display adequately
  // by iterating through them and showing a title or key info. If specific fields are needed for each item in the list,
  // they should match the keys in the EmploymentRecord objects from the backend.
  // For example, if your EmploymentRecord objects have 'entry_date', 'departure_date', 'position_title':
  { key: 'entry_date', labelKey: 'entry_date' }, // Assuming EmploymentRecord has these fields
  { key: 'departure_date', labelKey: 'departure_date' },
  { key: 'position_title', labelKey: 'position_grade' }, // Example, adjust labelKey as needed
  { key: 'department', labelKey: 'department' }, // Example, add 'department' to fieldLabels if needed
  { key: 'remark', labelKey: 'remarks' } // Example, using generic 'remarks' label
];
