const fieldLabels = {
  // 系統標題 System Title
  system_title: { zh: '培正中學員工管理系統', en: 'PCMS HR System' },
  
  // 校方資料 (School Information)
  section_title_school: { zh: '校方資料', en: 'School Information' },
  staff_id: { zh: '員工編號', en: 'Staff ID' },
  staff_name: { zh: '員工姓名 (校方)', en: 'Staff Name (School)' }, // staff_name in StaffProfile model
  employment_type: { zh: '受聘形式', en: 'Employment Type' },
  employment_type_remark: { zh: '受聘形式備註', en: 'Employment Type Remark' },
  dsej_registration_status: { zh: '教青局登記資料', en: 'DSEJ Registration' }, // model: dsej_registration_status
  dsej_registration_rank: { zh: '教青局登記職級', en: 'DSEJ Rank' },
  entry_date: { zh: '入職日期', en: 'Entry Date' }, // model: entry_date
  departure_date: { zh: '離職日期', en: 'Departure Date' }, // model: departure_date
  retirement_date: { zh: '退休日期', en: 'Retirement Date' },
  position_grade: { zh: '職稱/任教年級', en: 'Position/Grade' }, // model: position_grade
  teaching_staff_salary_grade: { zh: '教學人員薪級', en: 'Teaching Staff Salary Grade' }, // model: teaching_staff_salary_grade
  basic_salary_points: { zh: '薪級基本點數', en: 'Salary Scale Basic Points' },
  adjusted_salary_points: { zh: '調整增薪點數', en: 'Adjusted Increment Points' }, // model: adjusted_salary_points
  provident_fund_type: { zh: '公積金類別', en: 'Provident Fund Category' }, // model: provident_fund_type
  remark: { zh: '備註 (校方資料)', en: 'Remarks (School Data)' }, // model: remark (StaffProfile's own remark)
  contract_number: { zh: '合約編號', en: 'Contract Number' }, // model: contract_number
  is_active: { zh: '在職狀態', en: 'Active Status' },
  school_seniority_description: { zh: '在校年資', en: 'School Seniority' }, // New backend field

  // 個人資料 (Personal Information)
  section_title_personal: { zh: '個人資料', en: 'Personal Information' },
  name_chinese: { zh: '員工姓名(中文)', en: 'Staff Name (Chinese)' }, // model: name_chinese
  name_foreign: { zh: '員工姓名(外文)', en: 'Staff Name (Foreign)' }, // model: name_foreign
  gender: { zh: '性別', en: 'Gender' },
  marital_status: { zh: '婚姻狀況', en: 'Marital Status' },
  birth_place: { zh: '出生地點', en: 'Place of Birth' }, // model: birth_place
  birth_date: { zh: '出生日期', en: 'Date of Birth' }, // model: birth_date
  origin: { zh: '籍貫', en: 'Origin' }, // model: origin
  id_type: { zh: '證件類別', en: 'ID Type' }, // model: id_type
  id_number: { zh: '證件號碼', en: 'ID Number' }, // model: id_number
  id_expiry_date: { zh: '證件有效期', en: 'ID Expiry Date' }, // model: id_expiry_date
  is_foreign_national: { zh: '是否外籍', en: 'Is Foreign National' }, // New backend field
  is_master: { zh: '是否碩士學位', en: 'Is Master Degree' }, // 全局教育標記
  is_phd: { zh: '是否博士學位', en: 'Is PhD Degree' }, // 全局教育標記
  is_overseas_study: { zh: '是否留學', en: 'Is Overseas Study' }, // 全局教育標記
  bank_account_number: { zh: '大豐銀行澳門幣戶口賬號', en: 'Bank Account' }, // model: bank_account_number
  social_security_number: { zh: '社保號碼', en: 'Social Security Number' },
  home_phone: { zh: '住宅電話', en: 'Home Phone' }, // model: home_phone
  mobile_phone: { zh: '手提電話', en: 'Mobile Phone' },
  address: { zh: '住址', en: 'Address' },
  email: { zh: '電郵', en: 'Email' },
  alumni_class: { zh: '級社(校友適用)', en: 'Alumni Class' }, // model: alumni_class
  alumni_class_year: { zh: '級社年級(校友適用)', en: 'Alumni Class Year' }, // model: alumni_class_year
  alumni_class_duration: { zh: '級社年數(校友適用)', en: 'Alumni Class Duration' }, // model: alumni_class_duration
  teacher_certificate_number: { zh: '教師證號碼', en: 'Teacher Certificate Number' },
  teaching_staff_rank: { zh: '教學人員職級', en: 'Teaching Staff Rank' },
  teaching_staff_rank_effective_date: { zh: '教學人員職級生效日期', en: 'Effective Date' },
  section_title_emergency_contact: { zh: '緊急聯絡資料', en: 'Emergency Contact' },
  emergency_contact_name: { zh: '緊急聯絡人姓名', en: 'Emergency Contact Name' },
  emergency_contact_phone: { zh: '緊急聯絡人電話', en: 'Emergency Contact Phone' },
  emergency_contact_relationship: { zh: '與緊急聯絡人之關係', en: 'Relationship' },

  // 家庭成員 (Family Members) - Prefix with 'family_member_' for clarity if needed, or use generic if context is clear in UI
  section_title_family: { zh: '家庭成員', en: 'Family Members' },
  family_member_name: { zh: '姓名', en: 'Name' }, // model: FamilyMember.name
  family_member_relationship: { zh: '關係', en: 'Relationship' }, // model: FamilyMember.relationship
  family_member_birth_date: { zh: '出生日期', en: 'Date of Birth' }, // model: FamilyMember.birth_date
  // Note: age is usually calculated, not stored. If you have 'age' field in FamilyMember model, add it.
  // family_member_age: { zh: '年齡', en: 'Age' },
  family_member_education_level: { zh: '學歷程度', en: 'Education Level' }, // model: FamilyMember.education_level
  family_member_institution: { zh: '教育機構/任職機構', en: 'Institution/Employer' }, // model: FamilyMember.institution
  family_member_alumni_class: { zh: '級社(校友適用)', en: 'Alumni Association (For Alumni)' }, // model: FamilyMember.alumni_class

  // 學歷狀況 (Education Background)
  section_title_education: { zh: '學歷狀況', en: 'Education Background' },
  education_study_period: { zh: '就讀年份', en: 'Study Period' }, // model: EducationBackground.study_period
  education_school_name: { zh: '就讀學校', en: 'School Name' }, // model: EducationBackground.school_name
  education_education_level: { zh: '教育程度', en: 'Education Level' }, // model: EducationBackground.education_level
  education_degree_name: { zh: '專科學位名稱', en: 'Degree Name' }, // model: EducationBackground.degree_name
  education_certificate_date: { zh: '獲得證書日期', en: 'Certificate Date' }, // model: EducationBackground.certificate_date
  education_is_phd: { zh: '是否博士', en: 'Is PhD' }, // New backend field (EducationBackground.is_phd)
  education_is_master: { zh: '是否碩士', en: 'Is Master' }, // 具體學歷標記
  education_is_overseas_study: { zh: '是否留學', en: 'Is Overseas Study' }, // New backend field (EducationBackground.is_overseas_study)

  // 工作經驗 (Work Experience)
  section_title_experience: { zh: '工作經驗', en: 'Work Experience' },
  work_experience_employment_period: { zh: '任職年份', en: 'Employment Period' }, // model: WorkExperience.employment_period
  work_experience_organization: { zh: '任職機構', en: 'Organization' }, // model: WorkExperience.organization
  work_experience_position: { zh: '任職職位', en: 'Position' }, // model: WorkExperience.position
  work_experience_salary: { zh: '薪金', en: 'Salary' }, // model: WorkExperience.salary

  // 專業資格 (Professional Qualifications)
  section_title_qualifications: { zh: '專業資格', en: 'Professional Qualifications' },
  professional_qualification_qualification_name: { zh: '專業資格名稱', en: 'Qualification Name' }, // model: ProfessionalQualification.qualification_name
  professional_qualification_issuing_organization: { zh: '頒發機構', en: 'Issuing Organization' }, // model: ProfessionalQualification.issuing_organization
  professional_qualification_issue_date: { zh: '頒授日期', en: 'Issue Date' }, // model: ProfessionalQualification.issue_date

  // 社團職務 (Association Positions/Duties)
  section_title_association_duties: { zh: '社團職務', en: 'Association Duties' },
  association_position_association_name: { zh: '社團名稱', en: 'Association Name' }, // model: AssociationPosition.association_name
  association_position_position: { zh: '職位', en: 'Position' }, // model: AssociationPosition.position
  association_position_start_year: { zh: '開始年期', en: 'Start Year' }, // model: AssociationPosition.start_year
  association_position_end_year: { zh: '結束年期', en: 'End Year' }, // model: AssociationPosition.end_year

  // Employment Records (this is a section, not individual fields usually displayed directly in StaffDetail, but good to have labels if needed)
  section_title_employment_record: { zh: '聘用記錄', en: 'Employment Records' },
  // Fields for EmploymentRecord model (e.g., er_entry_date, er_departure_date, er_position, etc. if you display them)
  // For now, assuming EmploymentRecord details are not shown directly field by field in the main staff detail view, but as a list of records.

  // 登錄頁面 Login Page
  login_title: { zh: '培正教職員系統登入', en: 'PCMS HR Login' },
  username_label: { zh: '用戶名', en: 'Username' },
  password_label: { zh: '密碼', en: 'Password' },
  login_button: { zh: '登入', en: 'Login' },
  forgot_password: { zh: '忘記密碼？', en: 'Forgot Password?' },

  // 通用按鈕 General Buttons
  name: { zh: '名稱', en: 'Name' },
  type: { zh: '類型', en: 'Type' },
  description: { zh: '描述', en: 'Description' },
  notes: { zh: '備註', en: 'Notes' },
  status: { zh: '狀態', en: 'Status' },
  effective_date: { zh: '生效日期', en: 'Effective Date' },
  expiry_date: { zh: '失效日期', en: 'Expiry Date' },
  created_at: { zh: '創建時間', en: 'Created At' },
  updated_at: { zh: '更新時間', en: 'Updated At' },
  action: { zh: '操作', en: 'Action' },
  details: { zh: '詳情', en: 'Details' },
  edit: { zh: '編輯', en: 'Edit' },
  delete: { zh: '刪除', en: 'Delete' },
  add_new: { zh: '新增', en: 'Add New' },
  save: { zh: '保存', en: 'Save' },
  cancel: { zh: '取消', en: 'Cancel' },
  confirm: { zh: '確認', en: 'Confirm' },
  success: { zh: '成功', en: 'Success' },
  error: { zh: '錯誤', en: 'Error' },
  warning: { zh: '警告', en: 'Warning' },
  info: { zh: '提示', en: 'Info' },
  no_data: { zh: '暫無資料', en: 'No Data Available' }, // Changed from 暫無數據
  loading: { zh: '加載中...', en: 'Loading...' },
  // remarks: { zh: '備註', en: 'Remarks' }, // Already have specific remarks like remark (school data)
  male: { zh: '男', en: 'Male' },
  female: { zh: '女', en: 'Female' },
  other: { zh: '其他', en: 'Other' },
  filter_section_title: { zh: '篩選條件', en: 'Filter Conditions' },
  statistics_section_title: { zh: '統計數據（基於目前篩選結果）', en: 'Statistics (Based on Current Filters)' },
  total_staff_count: { zh: '總人數', en: 'Total Staff' },
  phd_count: { zh: '博士人數', en: 'PhD Count' },
  master_count: { zh: '碩士人數', en: 'Master Count' },
  overseas_study_count: { zh: '留學人數', en: 'Overseas Study Count' },
  foreign_national_count: { zh: '外籍員工人數', en: 'Foreign National Count' },
  male_count: { zh: '男性人數', en: 'Male Count' },
  female_count: { zh: '女性人數', en: 'Female Count' },
  department: { zh: '部門', en: 'Department' },
  position: { zh: '職位', en: 'Position' },
  // employment_type: { zh: '受聘形式', en: 'Employment Type' }, // Already exists
  all: { zh: '全部', en: 'All' },
  yes: { zh: '是', en: 'Yes' },
  no: { zh: '否', en: 'No' },
  unknown: { zh: '未知', en: 'Unknown' },
  is_phd_label: { zh: '博士學位', en: 'PhD Degree' },
  is_overseas_study_label: { zh: '留學經驗', en: 'Overseas Study' },
  // is_foreign_national_label: { zh: '外籍員工', en: 'Foreign National' }, // <--- 刪除或註釋掉這一行，如果下面的定義更合適
  years_of_service: { zh: '年資', en: 'Years of Service' },
  apply_filters: { zh: '應用篩選', en: 'Apply Filters' },

  // Options for DSEJ Registration
  dsej_registration: { zh: '教青局登記資料', en: 'DSEJ Registration' }, // Label for the filter itself (already used)
  dsej_full_time: { zh: '全職', en: 'Full-time' },
  dsej_part_time: { zh: '兼職', en: 'Part-time' },
  dsej_na: { zh: '不適用', en: 'N/A' }, // Can also reuse 'not_applicable' if preferred

  // Options for Employment Type (ensure these keys are unique and descriptive)
  emp_type_ft_teacher_cert: { zh: '全職教學人員(教師證)', en: 'Full-time Teaching Staff (Teacher Cert)' },
  emp_type_pt_teacher_cert: { zh: '兼職教學人員(教師證)', en: 'Part-time Teaching Staff (Teacher Cert)' },
  emp_type_ft_staff_cert: { zh: '全職職員(職員證)', en: 'Full-time Staff (Staff Cert)' },
  emp_type_pt_staff_cert: { zh: '兼職職員(職員證)', en: 'Part-time Staff (Staff Cert)' },
  emp_type_pt_staff: { zh: '兼職職員', en: 'Part-time Staff' },
  emp_type_ft_school_worker_cert: { zh: '全職校工(職員證)', en: 'Full-time School Worker (Staff Cert)' },
  emp_type_pt_school_worker: { zh: '兼職校工', en: 'Part-time School Worker' },
  emp_type_pt_intern_cert: { zh: '兼職實習生(職員證)', en: 'Part-time Intern (Staff Cert)' },
  emp_type_st_intern: { zh: '短期實習生', en: 'Short-term Intern' },
  emp_type_sub_teacher: { zh: '代課老師', en: 'Substitute Teacher' },
  emp_type_coop_unit: { zh: '合作單位(請註明公司名)', en: 'Cooperative Unit (Specify Company)' },
  emp_type_reg_ext_tutor: { zh: '正課餘暇導師', en: 'Regular Extracurricular Tutor' },
  emp_type_cocurr_tutor: { zh: '聯課活動導師', en: 'Co-curricular Activity Tutor' },
  emp_type_vol_cocurr_tutor: { zh: '義務聯課活動導師', en: 'Volunteer Co-curricular Activity Tutor' },
  emp_type_pt_library_staff: { zh: '圖書館兼職人員', en: 'Part-time Library Staff' },

  statistics_visualization_area: { zh: '統計可視化區', en: 'Statistics Visualization Area' },
  education_distribution: { zh: '學歷分布', en: 'Education Distribution' },
  seniority_distribution: { zh: '年資分布', en: 'Seniority Distribution' },
  gender_ratio: { zh: '性別比例', en: 'Gender Ratio' },
  total_staff: { zh: '員工總數', en: 'Total Staff' },
  phd: { zh: '博士', en: 'PhD' },
  master: { zh: '碩士', en: 'Master' },
  years_0_4: { zh: '0-4年', en: '0-4 Years' }, // Add all year ranges
  years_5_9: { zh: '5-9年', en: '5-9 Years' },
  // ... other year ranges for statistics and filters
  search_staff_placeholder: { zh: '搜索員工（例如：姓名、部門）', en: 'Search staff (e.g., name, department)' },
  search_button_label: { zh: '搜索', en: 'Search' },
  staff_list: { zh: '員工列表', en: 'Staff List' },
  no_staff_found: { zh: '沒有找到員工信息，請嘗試搜索或調整篩選條件。', en: 'No staff information found, please try searching or adjusting filters.' },
  not_applicable: { zh: '不適用', en: 'N/A' },
  staff_detail_title: { zh: '員工詳細資料', en: 'Staff Details' }, // Added for the main title of the detail section
  closeDetails: { zh: '關閉詳細資料', en: 'Close Details' }, // Added for the close button tooltip
  staff_detail_disclaimer: { zh: '以上資料僅供參考，如有任何疑問，請與校務處職員聯絡。', en: 'Information is for reference only. Please contact the Academic Affairs Office if you have questions.' },
  header_greeting: { zh: '您好', en: 'Hello' },
  new_staff_approval: { zh: '新員工審批', en: 'New Staff Approval' },
  batch_upload_staff: { zh: '批量上傳員工資料', en: 'Batch Upload Staff Data' },
  logout: { zh: '登出', en: 'Logout' },
  // Labels for StaffDetailSection if not already covered by existing fieldKeys
  school_information_title: { zh: '校方資料', en: 'School Information' },
  personal_information_title: { zh: '個人資料', en: 'Personal Information' },
  staff_registration_title: { zh: '員工入職申請', en: 'Staff Registration Application' },
  // Personal Information Section (many are already there, ensure all used ones are present)
  // section_title_personal: { zh: '個人資料', en: 'Personal Information' }, // Already exists
  // name_chinese: { zh: '員工姓名(中文)', en: 'Staff Name (Chinese)' }, // Already exists
  // ... and so on for all fields in personal info ...
  is_foreign_national_label: { zh: '是否外籍人士', en: 'Foreign National' }, // 保留這個，如果它更符合您的 UI 標籤

  // Family Members Section
  // section_title_family: { zh: '家庭成員', en: 'Family Members' }, // Already exists
  // family_member_name: { zh: '姓名', en: 'Name' }, // Already exists
  // ... and so on for all fields in family members ...
  family_member_age: { zh: '年齡', en: 'Age' }, // Add if not present
  remove_item_button: { zh: '移除此成員', en: 'Remove This Member' },
  add_family_member_button: { zh: '添加家庭成員', en: 'Add Family Member' },

  // Education Background Section
  section_title_education_applicant: { zh: '學歷狀況 (中學及以上)', en: 'Education Background (Secondary School and Above)' }, // Differentiate from dashboard's education section if needed
  // education_study_period: { zh: '就讀年份', en: 'Year of Study' }, // Already exists
  // ... and so on for all fields in education ...
  education_is_phd_applicant: { zh: '是否博士學位(PhD)', en: 'Is PhD Degree' },
  education_is_overseas_study_applicant: { zh: '是否留學', en: 'Is Overseas Study' },
  remove_item_button_education: { zh: '移除此學歷', en: 'Remove This Education Record' },
  add_education_button: { zh: '添加學歷', en: 'Add Education Record' },

  // Work Experience Section
  // section_title_experience: { zh: '工作經驗', en: 'Work Experience' }, // Already exists
  // ... and so on for all fields in work experience ...
  remove_item_button_experience: { zh: '移除此經驗', en: 'Remove This Experience' },
  add_experience_button: { zh: '添加工作經驗', en: 'Add Work Experience' },

  // Professional Qualifications Section
  section_title_qualifications_applicant: { zh: '專業資格證明', en: 'Professional Qualifications' }, // Differentiate if needed
  // ... and so on for all fields in qualifications ...
  remove_item_button_qualification: { zh: '移除此資格', en: 'Remove This Qualification' },
  add_qualification_button: { zh: '添加專業資格', en: 'Add Professional Qualification' },

  // Social Duties Section
  section_title_association_duties_applicant: { zh: '社團職務', en: 'Association Duties' }, // Differentiate if needed
  // ... and so on for all fields in association duties ...
  remove_item_button_duty: { zh: '移除此職務', en: 'Remove This Duty' },
  add_duty_button: { zh: '添加社團職務', en: 'Add Association Duty' },

  // Submit Button
  submit_button: { zh: '提交資料', en: 'Submit Data' },

  // Alert Messages
  staff_registration_success: { zh: '註冊申請已提交，請等待管理員審核。', en: 'Registration application submitted. Please wait for administrator approval.' },
  staff_registration_failure_prefix: { zh: '提交失敗: ', en: 'Submission failed: ' },

  // Gender Options for Select
  gender_options: [
    { value: 'M', label: { zh: '男', en: 'Male' } },
    { value: 'F', label: { zh: '女', en: 'Female' } }
  ],
  // ... existing code ...
};

export default fieldLabels;
