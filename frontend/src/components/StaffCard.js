import React from 'react';
import { Card, CardContent, Typography, Grid, Avatar, Box } from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import fieldLabels from './fieldLabels';

// Helper function to highlight text
const HighlightedText = ({ text, highlight }) => {
  if (!highlight || text === null || text === undefined) {
    return String(text === null || text === undefined ? '' : text);
  }
  const textString = String(text);
  const parts = textString.split(new RegExp(`(${highlight.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi'));
  return (
    <>
      {parts.map((part, i) =>
        part.toLowerCase() === highlight.toLowerCase() ? (
          <mark key={i}>{part}</mark>
        ) : (
          part
        )
      )}
    </>
  );
};

function StaffCard({ staff, onClick, searchTerm }) {
  const bi = (key, fallback) => {
    const lbl = fieldLabels[key];
    if (lbl) return `${lbl.zh} ${lbl.en}`;
    return fallback || key;
  };

  const displayValue = (value) => {
    const originalValue = value !== null && value !== undefined ? value : '暫無資料 N/A';
    if (searchTerm && (typeof originalValue === 'string' || typeof originalValue === 'number')) {
        return <HighlightedText text={String(originalValue)} highlight={searchTerm} />;
    }
    if (typeof originalValue === 'boolean') {
      return originalValue ? '是 Yes' : '否 No';
    }
    return originalValue;
  };

  const getGenderLabel = (genderValue) => {
    let label;
    if (genderValue === 'M' || genderValue === 'male') label = '男 Male';
    else if (genderValue === 'F' || genderValue === 'female') label = '女 Female';
    else label = genderValue !== null && genderValue !== undefined ? genderValue : '暫無資料 N/A';
    
    if (searchTerm && (typeof label === 'string' || typeof label === 'number')) {
        return <HighlightedText text={String(label)} highlight={searchTerm} />;
    }
    return label;
  };

  // 處理員工照片顯示並添加時間戳防緩存
  const getStaffPhoto = () => {
    if (staff.profile_picture) {
      // 如果是完整URL，直接使用
      if (staff.profile_picture.startsWith('http')) {
        // 添加時間戳防止緩存問題
        const separator = staff.profile_picture.includes('?') ? '&' : '?';
        return `${staff.profile_picture}${separator}t=${Date.now()}`;
      }
      // 使用nginx代理的媒體文件路徑，添加時間戳防緩存
      const separator = staff.profile_picture.includes('?') ? '&' : '?';
      return `${staff.profile_picture}${separator}t=${Date.now()}`;
    }
    return null;
  };

  const staffPhoto = getStaffPhoto();

  return (
    <Card sx={{ mb: 2, cursor: 'pointer' }} onClick={onClick}>
      <CardContent>
        <Grid container spacing={2}>
          {/* 員工照片區域 */}
          <Grid item xs={12} sm={3} md={2} display="flex" justifyContent="center">
            <Avatar
              src={staffPhoto}
              sx={{ 
                width: 80, 
                height: 80, 
                bgcolor: staffPhoto ? 'transparent' : 'primary.main'
              }}
            >
              {!staffPhoto && <PersonIcon sx={{ fontSize: 40 }} />}
            </Avatar>
          </Grid>
          
          {/* 員工信息區域 */}
          <Grid item xs={12} sm={9} md={10}>
            <Box mb={1}>
              <Typography variant="h6">
                {bi('staff_id', '員工編號 Staff ID')}: {displayValue(staff.staff_id)}
              </Typography>
              <Typography variant="h5" color="primary">
                {displayValue(
                  (staff.name_chinese && staff.name_chinese !== '/' && staff.name_chinese.trim()) 
                    ? staff.name_chinese 
                    : (staff.name_english || staff.name_foreign || 'N/A')
                )}
              </Typography>
            </Box>
            
              <Grid container spacing={1}>
                <Grid item xs={6}>
                  <Typography variant="body2">
                    {bi('gender', '性別 Gender')}: {getGenderLabel(staff.gender)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2">
                    {bi('employment_type', '受聘形式 Employment')}: {displayValue(staff.employment_type)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2">
                    {bi('position_grade', '職稱/年級 Position')}: {displayValue(staff.position_grade)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2">
                    {bi('years_of_service', '年資 Years of Service')}: {displayValue(staff.school_seniority_description)}
                  </Typography>
                </Grid>
              </Grid>
            </Grid>
          </Grid>
      </CardContent>
    </Card>
  );
}

export default StaffCard;
