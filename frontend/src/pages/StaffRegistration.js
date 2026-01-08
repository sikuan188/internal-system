import React, { useState } from 'react';
import {
  Box, Button, TextField, Typography, Paper, Grid, Divider,
  Checkbox, FormControlLabel, Select, MenuItem, InputLabel, FormControl
} from '@mui/material';
// import { useLanguage } from '../contexts/LanguageContext'; 
// import fieldLabels from '../utils/fieldLabels';
// import LanguageSwitcher from '../components/LanguageSwitcher'; // <--- 如果使用方案二，請註釋或刪除此行
import '../styles/StaffRegistration.css'; // 引入新的 CSS 文件

// Helper function to get CSRF token from cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const StaffRegistration = () => {
  // 移除不需要的語言相關邏輯

  const initialFormData = {
    // Personal Information (from StaffApplication model)
    name_chinese: '',
    name_foreign: '',
    gender: '', // M/F
    marital_status: '',
    birth_place: '',
    birth_date: '', // YYYY-MM-DD
    origin: '',
    id_type: '',
    id_number: '',
    id_expiry_date: '', // YYYY-MM-DD
    bank_account_number: '',
    social_security_number: '',
    home_phone: '',
    mobile_phone: '',
    address: '',
    email: '',
    alumni_class: '',
    alumni_class_year: '',
    alumni_class_duration: '',
    teacher_certificate_number: '',
    teaching_staff_rank: '',
    teaching_staff_rank_effective_date: '', // YYYY-MM-DD
    emergency_contact_name: '',
    emergency_contact_phone: '',
    emergency_contact_relationship: '',

    // Family Members (from ApplicationFamilyMember model)
    family_members: [
      { name: '', relationship: '', birth_date: '', age: '', education_level: '', institution: '', alumni_class: '' }, // Added age, education_level, institution, alumni_class
    ],

    // Education Background (from ApplicationEducation model)
    educations: [
      { study_period: '', school_name: '', education_level: '', degree_name: '', certificate_date: '', is_phd: false, is_master: false, is_overseas_study: false },
    ],

    // Work Experience (from ApplicationWorkExperience model)
    work_experiences: [
      { employment_period: '', organization: '', position: '', salary: '' },
    ],

    // Professional Qualifications (from ApplicationProfessionalQualification model)
    professional_qualifications: [
      { qualification_name: '', issuing_organization: '', issue_date: '' },
    ],

    // Social Duties (from ApplicationAssociationPosition model)
    association_positions: [
      { association_name: '', position: '', start_year: '', end_year: '' },
    ],
  };

  const [formData, setFormData] = useState(initialFormData);

  const handleChange = (sectionOrField, indexOrValue, fieldOrValue, valueIfNested) => {
    setFormData(prevData => {
      const newData = { ...prevData };

      if (typeof indexOrValue === 'number') { // Handling array sections (family_members, educations, etc.)
        const section = sectionOrField;
        const index = indexOrValue;
        const field = fieldOrValue;
        const value = valueIfNested;

        if (Array.isArray(newData[section])) {
          newData[section] = [...newData[section]];
          if (!newData[section][index]) newData[section][index] = {};
          newData[section][index][field] = value;
        }
      } else { // Handling direct fields in formData (personal info)
        const field = sectionOrField;
        const value = indexOrValue;
        newData[field] = value;
      }
      return newData;
    });
  };
  
  // const handleCheckboxChange = (section, index, field, checked) => {
  //   handleChange(section, index, field, checked);
  // }; // Removed unused function

  const addItem = (section) => {
    setFormData(prevData => ({
      ...prevData,
      [section]: [...prevData[section], {}] 
    }));
  };

  const removeItem = (section, index) => {
    setFormData(prevData => ({
      ...prevData,
      [section]: prevData[section].filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    console.log('Form data to be submitted:', formData);
    // Log using fieldLabels for alert message
    const alertMessages = {
      success: '註冊申請已提交，請等待管理員審核。 Registration application submitted. Please wait for administrator approval.',
      failure_prefix: '提交失敗: Submission failed: '
    };

    try {
      const csrftoken = getCookie('csrftoken'); // Get CSRF token
      // Ensure your backend API endpoint for application submission is correct
      const response = await fetch('/api/application/submit/', { // Corrected API endpoint
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken, // Add CSRF token to headers
        },
        body: JSON.stringify(formData)
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`Submission failed: ${response.status} ${JSON.stringify(errorData)}`);
      }
      const result = await response.json();
      console.log('Submission successful:', result);
      alert(alertMessages.success);
      setFormData(initialFormData); // Reset form after successful submission
    } catch (error) {
      console.error('Error submitting form:', error);
      alert(`${alertMessages.failure_prefix}${error.message}`);
    }
  };

  // Helper to render text fields for a section (can be expanded for other types)
  const renderFormField = (config) => {
    const { section, fieldName, labelKey, type = 'text', itemIndex = null, options = [], optionsKey, required = false } = config; // 新增 required 參數
    
    // 直接獲取中英雙語標籤
    const getLabel = (key) => {
      const labels = {
        // 個人資料字段
        name_chinese: '員工姓名(中文) Staff Name (Chinese)',
        name_foreign: '員工姓名(外文) Staff Name (Foreign)',
        gender: '性別 Gender',
        marital_status: '婚姻狀況 Marital Status',
        birth_place: '出生地點 Place of Birth',
        birth_date: '出生日期 Date of Birth',
        origin: '籍貫 Origin',
        id_type: '證件類別 ID Type',
        id_number: '證件號碼 ID Number',
        id_expiry_date: '證件有效期 ID Expiry Date',
        // 個人學歷標記
        is_foreign_national: '是否外籍人士 Foreign National',
        is_master: '是否碩士學位 Is Master Degree',
        bank_account_number: '大豐銀行澳門幣戶口賬號 Bank Account',
        social_security_number: '社保號碼 Social Security Number',
        home_phone: '住宅電話 Home Phone',
        mobile_phone: '手提電話 Mobile Phone',
        address: '住址 Address',
        email: '電郵 Email',
        alumni_class: '級社(校友適用) Alumni Class',
        alumni_class_year: '級社年級(校友適用) Alumni Class Year',
        alumni_class_duration: '級社年數(校友適用) Alumni Class Duration',
        teacher_certificate_number: '教師證號碼 Teacher Certificate Number',
        teaching_staff_rank: '教學人員職級 Teaching Staff Rank',
        teaching_staff_rank_effective_date: '教學人員職級生效日期 Effective Date',
        // 緊急聯絡資料
        emergency_contact_name: '緊急聯絡人姓名 Emergency Contact Name',
        emergency_contact_phone: '緊急聯絡人電話 Emergency Contact Phone',
        emergency_contact_relationship: '與緊急聯絡人之關係 Relationship',
        // 家庭成員字段
        family_member_name: '姓名 Name',
        family_member_relationship: '關係 Relationship',
        family_member_birth_date: '出生日期 Date of Birth',
        family_member_age: '年齡 Age',
        family_member_education_level: '學歷程度 Education Level',
        family_member_institution: '教育機構/任職機構 Institution/Employer',
        family_member_alumni_class: '級社(校友適用) Alumni Association',
        // 學歷字段  
        education_study_period: '就讀年份 Study Period',
        education_school_name: '就讀學校 School Name',
        education_education_level: '教育程度 Education Level',
        education_degree_name: '專科學位名稱 Degree Name',
        education_certificate_date: '獲得證書日期 Certificate Date',
        education_is_phd_applicant: '是否博士學位(PhD) Is PhD Degree',
        education_is_master_applicant: '是否碩士學位(Master) Is Master Degree',
        education_is_overseas_study_applicant: '是否留學 Is Overseas Study',
        // 工作經驗字段
        work_experience_employment_period: '任職年份 Employment Period',
        work_experience_organization: '任職機構 Organization',
        work_experience_position: '任職職位 Position',
        work_experience_salary: '薪金 Salary',
        // 專業資格字段
        professional_qualification_qualification_name: '專業資格名稱 Qualification Name',
        professional_qualification_issuing_organization: '頒發機構 Issuing Organization',
        professional_qualification_issue_date: '頒授日期 Issue Date',
        // 社團職務字段
        association_position_association_name: '社團名稱 Association Name',
        association_position_position: '職位 Position',
        association_position_start_year: '開始年期 Start Year',
        association_position_end_year: '結束年期 End Year'
      };
      return labels[key] || key;
    };
    
    const label = getLabel(labelKey);

    const value = itemIndex !== null 
      ? (formData[section]?.[itemIndex]?.[fieldName] || (type === 'checkbox' ? false : '')) 
      : (formData[fieldName] || (type === 'checkbox' ? false : ''));

    const onChange = (e) => {
      const val = type === 'checkbox' ? e.target.checked : e.target.value;
      if (itemIndex !== null) {
        handleChange(section, itemIndex, fieldName, val);
      } else {
        handleChange(fieldName, val); // For top-level fields like personalInfo
      }
    };
    
    if (type === 'checkbox') {
      return (
        <Grid item xs={12} sm={12}> {/* Changed sm from 6 to 12 */}
          <FormControlLabel
            control={<Checkbox checked={Boolean(value)} onChange={onChange} name={fieldName} />}
            label={label}
          />
        </Grid>
      );
    }

    if (type === 'select') {
      // 定義性別選項的中英雙語
      const getGenderOptions = () => [
        { value: 'M', label: '男 Male' },
        { value: 'F', label: '女 Female' }
      ];
      
      const selectOptions = optionsKey === 'gender_options' ? getGenderOptions() : options;
      
      return (
        <Grid item xs={12} sm={12}> {/* Changed sm from 6 to 12 */}
          <FormControl fullWidth margin="normal">
            <InputLabel>{label}</InputLabel>
            <Select name={fieldName} value={value} label={label} onChange={onChange}>
              {selectOptions.map(option => (
                <MenuItem key={option.value} value={option.value}>
                  {typeof option.label === 'string' ? option.label : option.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
      );
    }

      return (
        <Grid item xs={12} sm={12} key={fieldName}>
          <TextField
            fullWidth
            required={required}  // 添加 required 屬性
            label={label}
            name={fieldName}
            value={value}
            onChange={onChange}
            margin="normal"
            type={type === 'date' || type === 'textarea' ? type : 'text'}
            multiline={type === 'textarea'}
            rows={type === 'textarea' ? 3 : 1}
            InputLabelProps={type === 'date' ? { shrink: true } : {}}
          />
        </Grid>
      );
  };

  return (
    <Box className="staff-registration-container"> {/* 使用 CSS class */} 
      <Paper elevation={3} className="staff-registration-paper"> {/* 使用 CSS class */}
        <Typography variant="h4" gutterBottom className="staff-registration-title"> {/* 使用 CSS class */}
          員工入職申請 Staff Registration Application
        </Typography>
        
        <form onSubmit={handleSubmit}>
          {/* Personal Information Section */}
          <Box mb={3}>
            <Typography variant="h6" gutterBottom className="staff-registration-section-title">個人資料 Personal Information</Typography>
            <Grid container spacing={2} className="staff-registration-form-grid"> {/* 使用 CSS class */}
              {renderFormField({ fieldName: 'name_chinese', labelKey: 'name_chinese' })}
              {renderFormField({ fieldName: 'name_foreign', labelKey: 'name_foreign' })}
              {renderFormField({ fieldName: 'gender', labelKey: 'gender', type: 'select', optionsKey: 'gender_options' })}
              {renderFormField({ fieldName: 'marital_status', labelKey: 'marital_status' })}
              {renderFormField({ fieldName: 'birth_place', labelKey: 'birth_place' })}
              {renderFormField({ fieldName: 'birth_date', labelKey: 'birth_date', type: 'date' })}
              {renderFormField({ fieldName: 'origin', labelKey: 'origin' })}
              {renderFormField({ fieldName: 'id_type', labelKey: 'id_type' })}
              {renderFormField({ fieldName: 'id_number', labelKey: 'id_number' })}
              {renderFormField({ fieldName: 'id_expiry_date', labelKey: 'id_expiry_date', type: 'date' })}
              {renderFormField({ fieldName: 'bank_account_number', labelKey: 'bank_account_number' })}
              {renderFormField({ fieldName: 'social_security_number', labelKey: 'social_security_number' })}
              {renderFormField({ fieldName: 'home_phone', labelKey: 'home_phone' })}
              {renderFormField({ fieldName: 'mobile_phone', labelKey: 'mobile_phone', required: true })}
              {renderFormField({ fieldName: 'address', labelKey: 'address', type: 'textarea' })}
              {renderFormField({ fieldName: 'email', labelKey: 'email', type: 'email' })}
              {renderFormField({ fieldName: 'alumni_class', labelKey: 'alumni_class' })}
              {renderFormField({ fieldName: 'alumni_class_year', labelKey: 'alumni_class_year' })}
              {renderFormField({ fieldName: 'alumni_class_duration', labelKey: 'alumni_class_duration' })}
              {renderFormField({ fieldName: 'teacher_certificate_number', labelKey: 'teacher_certificate_number' })}
              {renderFormField({ fieldName: 'teaching_staff_rank', labelKey: 'teaching_staff_rank' })}
              {renderFormField({ fieldName: 'teaching_staff_rank_effective_date', labelKey: 'teaching_staff_rank_effective_date', type: 'date' })}
              {renderFormField({ fieldName: 'emergency_contact_name', labelKey: 'emergency_contact_name' })}
              {renderFormField({ fieldName: 'emergency_contact_phone', labelKey: 'emergency_contact_phone' })}
              {renderFormField({ fieldName: 'emergency_contact_relationship', labelKey: 'emergency_contact_relationship' })}
            </Grid>
          </Box>
          <Divider sx={{ my: 2 }} />

          {/* Family Members Section */}
          <Box mb={3}>
            <Typography variant="h6" gutterBottom className="staff-registration-section-title">家庭成員 Family Members</Typography>
            {formData.family_members.map((member, index) => (
              <Paper key={index} sx={{ p: 2, mb: 2, border: '1px solid #eee' }} className="staff-registration-paper"> {/* 可選: 也為內部 Paper 應用樣式 */}
                <Grid container spacing={2} className="staff-registration-form-grid">
                  {renderFormField({ section: 'family_members', itemIndex: index, fieldName: 'name', labelKey: 'family_member_name' })}
                  {renderFormField({ section: 'family_members', itemIndex: index, fieldName: 'relationship', labelKey: 'family_member_relationship' })}
                  {renderFormField({ section: 'family_members', itemIndex: index, fieldName: 'birth_date', labelKey: 'family_member_birth_date', type: 'date' })}
                  {renderFormField({ section: 'family_members', itemIndex: index, fieldName: 'age', labelKey: 'family_member_age', type: 'number' })}
                  {renderFormField({ section: 'family_members', itemIndex: index, fieldName: 'education_level', labelKey: 'family_member_education_level' })}
                  {renderFormField({ section: 'family_members', itemIndex: index, fieldName: 'institution', labelKey: 'family_member_institution' })}
                  {renderFormField({ section: 'family_members', itemIndex: index, fieldName: 'alumni_class', labelKey: 'family_member_alumni_class' })}
                </Grid>
                <Button onClick={() => removeItem('family_members', index)} color="error" sx={{ mt: 1 }}>移除此成員 Remove This Member</Button>
              </Paper>
            ))}
            <Button onClick={() => addItem('family_members')} variant="outlined">添加家庭成員 Add Family Member</Button>
          </Box>
          <Divider sx={{ my: 2 }} />

          {/* Education Background Section */}
          <Box mb={3}>
            <Typography variant="h6" gutterBottom className="staff-registration-section-title">學歷狀況 (中學及以上) Education Background (Secondary School and Above)</Typography>
            {formData.educations.map((edu, index) => (
              <Paper key={index} sx={{ p: 2, mb: 2, border: '1px solid #eee' }} className="staff-registration-paper">
                <Grid container spacing={2} className="staff-registration-form-grid">
                  {renderFormField({ section: 'educations', itemIndex: index, fieldName: 'study_period', labelKey: 'education_study_period' })}
                  {renderFormField({ section: 'educations', itemIndex: index, fieldName: 'school_name', labelKey: 'education_school_name' })}
                  {renderFormField({ section: 'educations', itemIndex: index, fieldName: 'education_level', labelKey: 'education_education_level' })}
                  {renderFormField({ section: 'educations', itemIndex: index, fieldName: 'degree_name', labelKey: 'education_degree_name' })}
                  {renderFormField({ section: 'educations', itemIndex: index, fieldName: 'certificate_date', labelKey: 'education_certificate_date', type: 'date' })}
                  {renderFormField({ section: 'educations', itemIndex: index, fieldName: 'is_phd', labelKey: 'education_is_phd_applicant', type: 'checkbox' })}
                  {renderFormField({ section: 'educations', itemIndex: index, fieldName: 'is_master', labelKey: 'education_is_master_applicant', type: 'checkbox' })}
                  {renderFormField({ section: 'educations', itemIndex: index, fieldName: 'is_overseas_study', labelKey: 'education_is_overseas_study_applicant', type: 'checkbox' })}
                </Grid>
                <Button onClick={() => removeItem('educations', index)} color="error" sx={{ mt: 1 }}>移除此學歷 Remove This Education Record</Button>
              </Paper>
            ))}
            <Button onClick={() => addItem('educations')} variant="outlined">添加學歷 Add Education Record</Button>
          </Box>
          <Divider sx={{ my: 2 }} />
          
          {/* Work Experience Section */}
          <Box mb={3}>
            <Typography variant="h6" gutterBottom className="staff-registration-section-title">工作經驗 Work Experience</Typography>
            {formData.work_experiences.map((exp, index) => (
              <Paper key={index} sx={{ p: 2, mb: 2, border: '1px solid #eee' }} className="staff-registration-paper">
                <Grid container spacing={2} className="staff-registration-form-grid">
                  {renderFormField({ section: 'work_experiences', itemIndex: index, fieldName: 'employment_period', labelKey: 'work_experience_employment_period' })}
                  {renderFormField({ section: 'work_experiences', itemIndex: index, fieldName: 'organization', labelKey: 'work_experience_organization' })}
                  {renderFormField({ section: 'work_experiences', itemIndex: index, fieldName: 'position', labelKey: 'work_experience_position' })}
                  {renderFormField({ section: 'work_experiences', itemIndex: index, fieldName: 'salary', labelKey: 'work_experience_salary' })}
                </Grid>
                <Button onClick={() => removeItem('work_experiences', index)} color="error" sx={{ mt: 1 }}>移除此經驗 Remove This Experience</Button>
              </Paper>
            ))}
            <Button onClick={() => addItem('work_experiences')} variant="outlined">添加工作經驗 Add Work Experience</Button>
          </Box>
          <Divider sx={{ my: 2 }} />

          {/* Professional Qualifications Section */}
          <Box mb={3}>
            <Typography variant="h6" gutterBottom className="staff-registration-section-title">專業資格證明 Professional Qualifications</Typography>
            {formData.professional_qualifications.map((qual, index) => (
              <Paper key={index} sx={{ p: 2, mb: 2, border: '1px solid #eee' }} className="staff-registration-paper">
                <Grid container spacing={2} className="staff-registration-form-grid">
                  {renderFormField({ section: 'professional_qualifications', itemIndex: index, fieldName: 'qualification_name', labelKey: 'professional_qualification_qualification_name' })}
                  {renderFormField({ section: 'professional_qualifications', itemIndex: index, fieldName: 'issuing_organization', labelKey: 'professional_qualification_issuing_organization' })}
                  {renderFormField({ section: 'professional_qualifications', itemIndex: index, fieldName: 'issue_date', labelKey: 'professional_qualification_issue_date', type: 'date' })}
                </Grid>
                <Button onClick={() => removeItem('professional_qualifications', index)} color="error" sx={{ mt: 1 }}>移除此資格 Remove This Qualification</Button>
              </Paper>
            ))}
            <Button onClick={() => addItem('professional_qualifications')} variant="outlined">添加專業資格 Add Professional Qualification</Button>
          </Box>
          <Divider sx={{ my: 2 }} />

          {/* Social Duties Section */}
          <Box mb={3}>
            <Typography variant="h6" gutterBottom className="staff-registration-section-title">社團職務 Association Duties</Typography>
            {formData.association_positions.map((duty, index) => (
              <Paper key={index} sx={{ p: 2, mb: 2, border: '1px solid #eee' }} className="staff-registration-paper">
                <Grid container spacing={2} className="staff-registration-form-grid">
                  {renderFormField({ section: 'association_positions', itemIndex: index, fieldName: 'association_name', labelKey: 'association_position_association_name' })}
                  {renderFormField({ section: 'association_positions', itemIndex: index, fieldName: 'position', labelKey: 'association_position_position' })}
                  {renderFormField({ section: 'association_positions', itemIndex: index, fieldName: 'start_year', labelKey: 'association_position_start_year' })}
                  {renderFormField({ section: 'association_positions', itemIndex: index, fieldName: 'end_year', labelKey: 'association_position_end_year' })}
                </Grid>
                <Button onClick={() => removeItem('association_positions', index)} color="error" sx={{ mt: 1 }}>移除此職務 Remove This Duty</Button>
              </Paper>
            ))}
            <Button onClick={() => addItem('association_positions')} variant="outlined">添加社團職務 Add Association Duty</Button>
          </Box>
          <Divider sx={{ my: 2 }} />

          <Button type="submit" variant="contained" color="primary" fullWidth className="staff-registration-button">
            提交申請 Submit Application
          </Button>
        </form>
      </Paper>
      
      {/* 版權頁腳 */}
      <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 3, mb: 2 }}>
        <div style={{ textAlign: 'center', color: '#757575', fontSize: '0.9em' }}>
          Copyright © Pui Ching Middle School (Coloane Campus) 2025. All Rights Reserved.
        </div>
      </Typography>
    </Box>
  );
};

export default StaffRegistration;