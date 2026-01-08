import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material'; // 移除了 MuiLink
import { useNavigate } from 'react-router-dom';
import fieldLabels from './fieldLabels';

const Header = ({ userType, userName }) => {
  const navigate = useNavigate();

  const handleNavigateImport = () => {
    navigate('/import-staff-data'); // 確保這個路由與您在 App.js 中定義的一致
  };

  const handleNavigateBatchPhoto = () => {
    navigate('/batch-photo-upload'); // 導航到批量照片上傳頁面
  };

  // 根據角色判斷是否顯示批量上傳按鈕
  const shouldShowBatchUpload = (role) => {
    return role === 'admin' || role === 'hr_manager';
  };

  // 根據角色判斷是否顯示登出按鈕
  const shouldShowLogout = (role) => {
    return role !== 'registration';
  };

  const bi = (key, fallback) => {
    const lbl = fieldLabels[key];
    if (lbl) return `${lbl.zh || ''} ${lbl.en || ''}`.trim();
    return fallback || key;
  };

  return (
    <AppBar position="static">
      <Toolbar>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <img src="/pcmsco_logo.jpeg" alt="Logo" style={{ height: '40px', marginRight: '10px' }} />
            <Typography variant="h6" sx={{ color: 'white', mr: 2 }}>
              {`${fieldLabels.system_title?.zh || '培正中學員工管理系統'} ${fieldLabels.system_title?.en || 'PCMS HR System'}`}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {shouldShowBatchUpload(userType) && false && ( // 隱藏這兩個按鈕
              <>
                {/* <MuiLink href="#" sx={{ color: 'white', mr: 2, textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}>
                  新員工審批
                </MuiLink> */} 
                {/* 暫時註釋掉新員工審批，如果需要可以取消註釋並實現其導航 */}
                <Button 
                  color="inherit" 
                  onClick={handleNavigateImport} 
                  sx={{ mr: 2, textTransform: 'none' }} // textTransform: 'none' 保持文字原始大小寫
                >
                  {bi('batch_upload_staff', '批量上傳員工資料 Batch Upload Staff Data')}
                </Button>
                <Button 
                  color="inherit" 
                  onClick={handleNavigateBatchPhoto} 
                  sx={{ mr: 2, textTransform: 'none' }}
                >
                  批量上傳照片 Batch Photo Upload
                </Button>
              </>
            )}
            {shouldShowLogout(userType) && (
              <Button color="inherit" onClick={() => navigate('/login')}>
                {bi('logout', '登出 Logout')}
              </Button>
            )}
          </Box>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
