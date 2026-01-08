import React from 'react';
import { Box, Typography } from '@mui/material';
import StaffCard from './StaffCard';
import fieldLabels from './fieldLabels';

const StaffListSection = ({ staffList, onStaffCardClick, searchTerm }) => {
  const bi = (key, fallback) => {
    const lbl = fieldLabels[key];
    if (lbl) return `${lbl.zh} ${lbl.en}`;
    return fallback || key;
  };
  return (
    // This outer Box should fill the space given by its parent Paper in Dashboard.js
    <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}> 
      <Typography variant="h6" sx={{ color: 'primary.main', mb: 1, flexShrink: 0 }}> {/* Prevent title from shrinking */}
        {bi('staff_list', '員工列表 Staff List')}
      </Typography>
      {/* This Box will contain the scrollable list of StaffCards */}
      <Box 
        sx={{ 
          overflowY: 'auto', 
          flexGrow: 1,
          maxHeight: '80vh', // Allow roughly up to ~10 staff cards before scrolling
          pr: 1 // Add right padding so the scrollbar doesn't cover card content
        }}
      > 
        {staffList && staffList.length > 0 ? (
          staffList.map((staff) => (
            <StaffCard 
              key={staff.staff_id}
              staff={staff}
              searchTerm={searchTerm}
              onClick={() => onStaffCardClick(staff)}
            />
          ))
        ) : (
          <Typography sx={{ textAlign: 'center', mt: 2 }}>
            {bi('no_staff_found', '沒有找到員工信息，請嘗試搜索或調整篩選條件。 No staff found.')}
          </Typography>
        )}
      </Box>
    </Box>
  );
}

export default StaffListSection;

// highlightText function removed as it's unused
