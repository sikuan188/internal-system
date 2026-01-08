import React from 'react';
import {
  // Box, // REMOVED
  Paper,
  Typography,
  Grid,
  // List, // REMOVED
  ListItem,
  ListItemText,
  IconButton,
  Tooltip,
  Card,
  CardContent,
  Avatar,
  Box
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import PersonIcon from '@mui/icons-material/Person';
import fieldLabels from './fieldLabels';
import {
  schoolInfoFields,
  personalInfoFields,
  emergencyContactFields,
  familyMemberFields,
  educationBackgroundFields,
  workExperienceFields,
  professionalQualificationFields,
  associationPositionFields,
  employmentRecordFields
} from './StaffDetailFields';

// 1. Define HighlightedText component here or import if defined elsewhere
const HighlightedText = ({ text, highlight }) => {
  if (!highlight || typeof text !== 'string') {
    return <span>{text}</span>;
  }
  const parts = text.split(new RegExp(`(${highlight})`, 'gi'));
  return (
    <>
      {parts.map((part, i) => 
        part.toLowerCase() === highlight.toLowerCase() ? (
          <span key={i} style={{ backgroundColor: 'yellow' }}>{part}</span>
        ) : (
          part
        )
      )}
    </>
  );
};

// Ensure this is the ONLY definition of DetailItem
const DetailItem = ({ labelKey, value, searchTerm, fullWidth = false, isGender = false, isBoolean = false }) => { // <-- Add searchTerm
  const labelObj = fieldLabels[labelKey];
  const label = labelObj ? `${labelObj.zh || labelKey} ${labelObj.en || ''}` : labelKey;

  let displayValue = value;
  if (value === null || value === undefined || value === '') {
    displayValue = '暫無資料 No Data';
  } else if (isGender && value) {
    const genderMap = {
      'm': '男 Male',
      'f': '女 Female',
      'male': '男 Male',
      'female': '女 Female'
    };
    displayValue = genderMap[value.toString().toLowerCase()] || value;
  } else if (isBoolean) { 
    if (value === true) {
      displayValue = '是 Yes';
    } else if (value === false) {
      displayValue = '否 No';
    } else {
      displayValue = '未知 Unknown'; 
    }
  }

  // Apply highlighting if searchTerm is provided and displayValue is a string
  const contentToDisplay = (typeof displayValue === 'string' && searchTerm) 
    ? <HighlightedText text={displayValue} highlight={searchTerm} />  // <--- 確保 searchTerm 在這裡被使用
    : displayValue;

  return (
    <Grid item xs={12} sm={fullWidth ? 12 : 6} md={fullWidth ? 12 : 4}>
      <Typography variant="subtitle2" sx={{ color: 'text.secondary' }}>
        {label}
      </Typography>
      <Typography variant="body1">{contentToDisplay}</Typography> {/* <-- Use contentToDisplay */}
    </Grid>
  );
};

const SectionTitle = ({ titleKey }) => {
  const titleObj = fieldLabels[titleKey];
  const title = titleObj ? `${titleObj.zh || titleKey} ${titleObj.en || ''}` : titleKey;
  return (
    <Typography variant="h6" gutterBottom sx={{ mt: 2, color: 'primary.main' }}>
      {title}
    </Typography>
  );
};

// renderListItems 函數不需要直接修改，因為 DetailItem 已經處理了語言

const StaffDetailSection = ({ staff, onClose, searchTerm }) => { // 確認 searchTerm 有傳入
  if (!staff) {
    return null;
  }

  // Helper function to render non-array data sections
  const renderSectionItems = (data, fields, titleKey) => {
    if (!data) return null;
    // Check if all fields in this section are empty or undefined
    const hasData = fields.some(field => data[field.key] !== undefined && data[field.key] !== '' && data[field.key] !== null);

    if (!hasData) {
      // Optionally, you can render nothing or a message indicating no data for this section
      // For now, let's render nothing if no data for any field in the section
      return null;
    }

    return (
      <>
        <SectionTitle titleKey={titleKey} />
        <Card sx={{ mb: 2, p: 2, boxShadow: 1 }}>
          <CardContent>
            <Grid container spacing={2}>
              {fields.map(field => (
                <DetailItem
                  key={field.key}
                  labelKey={field.labelKey || field.key}
                  value={data[field.key]}
                  searchTerm={searchTerm} // <-- Pass searchTerm
                  isGender={field.isGender || false}
                  isBoolean={field.isBoolean || false} 
                  fullWidth={field.fullWidth || false}
                />
              ))}
            </Grid>
          </CardContent>
        </Card>
      </>
    );
  };

  // 渲染數組數據的函數也需要傳遞 language 或在內部使用 useLanguage
  const renderArrayData = (dataArray, fields, titleKey) => {
    const sectionTitleObj = fieldLabels[titleKey] || { zh: titleKey, en: '' };
    const sectionTitle = `${sectionTitleObj.zh || titleKey} ${sectionTitleObj.en || ''}`; // This is the correct title for the section

    if (!dataArray || dataArray.length === 0) {
      return (
        <ListItem>
          <ListItemText primary={`${sectionTitle}: 暫無資料 No Data`} />
        </ListItem>
      );
    }
    return (
      <>
        <SectionTitle titleKey={titleKey} />
        {dataArray.map((item, index) => (
          <Card key={index} sx={{ mb: 2, p: 2, boxShadow: 1 }}> 
            <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'medium' }}>
              {`${sectionTitle} ${index + 1}`}
            </Typography>
            <Grid container spacing={2}>
              {fields.map(field => (
                <DetailItem 
                  key={field.key} 
                  labelKey={field.labelKey || field.key} 
                  value={item[field.key]} 
                  searchTerm={searchTerm} // <-- Pass searchTerm
                  isGender={field.isGender || false}
                  isBoolean={field.isBoolean || false} 
                />
              ))}
            </Grid>
          </Card>
        ))}
      </>
    );
  };

  return (
    // The Paper component itself will handle the scrolling within the bounds set by its parent Grid item in Dashboard.js
    <Paper 
      sx={{
        p: 2, 
        maxHeight: '200vh', // Allow roughly twice the previous height before internal scrolling
        overflowY: 'auto', // Enable vertical scrolling for content within Paper when overflowing
        boxSizing: 'border-box' // Ensure padding doesn't add to height
      }}
    >
      <Grid container justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Typography variant="h5" component="div" sx={{ color: 'primary.main', fontWeight: 'bold' }}>
          {(staff.name_chinese && staff.name_chinese !== '/' && staff.name_chinese.trim()) 
            ? staff.name_chinese 
            : (staff.name_foreign || `${fieldLabels.staff_detail_title?.zh || '員工詳細資料'} ${fieldLabels.staff_detail_title?.en || 'Staff Details'}`)}
        </Typography>
        <Tooltip title={`${fieldLabels.closeDetails?.zh || '關閉詳細資料'} ${fieldLabels.closeDetails?.en || 'Close Details'}`}>
          <IconButton onClick={onClose} size="large">
            <CloseIcon />
          </IconButton>
        </Tooltip>
      </Grid>

      {/* 員工照片顯示區域 */}
      <Box display="flex" justifyContent="center" mb={3}>
        <Avatar
          src={staff.profile_picture ? (
            staff.profile_picture.startsWith('http') 
              ? `${staff.profile_picture}${staff.profile_picture.includes('?') ? '&' : '?'}t=${Date.now()}` 
              : `${staff.profile_picture}${staff.profile_picture.includes('?') ? '&' : '?'}t=${Date.now()}`
          ) : null}
          sx={{ 
            width: 150, 
            height: 150, 
            bgcolor: staff.profile_picture ? 'transparent' : 'primary.main',
            border: '3px solid',
            borderColor: 'primary.main'
          }}
        >
          {!staff.profile_picture && <PersonIcon sx={{ fontSize: 80 }} />}
        </Avatar>
      </Box>
      
      {renderSectionItems(staff, schoolInfoFields, 'section_title_school')}
      {renderSectionItems(staff, personalInfoFields, 'section_title_personal')}
      {staff.emergency_contact_name && renderSectionItems(staff, emergencyContactFields, 'section_title_emergency_contact')}
      {renderArrayData(staff.employment_records, employmentRecordFields, 'section_title_employment_record')}
      {renderArrayData(staff.education_backgrounds, educationBackgroundFields, 'section_title_education')}
      {renderArrayData(staff.family_members, familyMemberFields, 'section_title_family')}
      {renderArrayData(staff.work_experiences, workExperienceFields, 'section_title_experience')}
      {renderArrayData(staff.professional_qualifications, professionalQualificationFields, 'section_title_qualifications')}
      {renderArrayData(staff.association_positions, associationPositionFields, 'section_title_association_duties')}

      <Typography variant="caption" display="block" sx={{ mt: 3, textAlign: 'center', color: 'text.secondary' }}>
        {`${fieldLabels.staff_detail_disclaimer?.zh || '以上資料僅供參考，如有疑問請聯絡校務處職員。'} ${fieldLabels.staff_detail_disclaimer?.en || 'Information is for reference only. Please contact the Academic Affairs Office if you have questions.'}`}
      </Typography>
    </Paper>
  );
};

export default StaffDetailSection;
