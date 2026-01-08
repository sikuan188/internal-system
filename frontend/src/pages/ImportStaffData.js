import React, { useState } from 'react';
import axios from 'axios';
import { 
  Button, 
  Typography, 
  Container, 
  Paper, 
  Box, 
  Alert, 
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  Divider,
  Card,
  CardContent,
  Input,
  FormLabel,
  Chip,
  Grid
} from '@mui/material';
import { 
  CloudUpload as CloudUploadIcon,
  Download as DownloadIcon,
  ArrowBack as ArrowBackIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';

function ImportStaffData() {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null); // 確保這個 state 被定義

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setUploadStatus('');
    setUploadResult(null); // 清除舊結果
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus('請選擇一個文件');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    function getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    setIsLoading(true);
    setUploadStatus('上傳並導入中...');
    setUploadResult(null); // 清除舊結果

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('/api/staff/import/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'X-CSRFToken': csrftoken,
          ...(token ? { 'Authorization': `Token ${token}` } : {})
        },
      });
      
      // 處理成功和警告狀態
      setUploadStatus(response.data.message);
      if (response.data.details && response.data.error_count > 0) {
        // 部分成功的情況，也要顯示錯誤詳情
        setUploadResult({
          errors: response.data.details.split('\n').filter(line => line.trim()),
          imported_count: response.data.imported_count || 0,
          error_count: response.data.error_count || 0
        });
      } else {
        setUploadResult(null);
      }
      console.log('Import successful:', response.data);
    } catch (error) {
      console.error('Error uploading file:', error.response ? error.response.data : error.message);
      
      // 設置錯誤狀態訊息
      const errorMessage = error.response?.data?.message || error.message;
      setUploadStatus(`導入失敗: ${errorMessage}`);
      
      // 設置錯誤詳情
      if (error.response?.data?.details) {
        const errorDetails = error.response.data.details.split('\n').filter(line => line.trim());
        setUploadResult({
          errors: errorDetails,
          imported_count: error.response.data.imported_count || 0,
          error_count: error.response.data.error_count || errorDetails.length
        });
      } else {
        setUploadResult({
          errors: [errorMessage],
          imported_count: 0,
          error_count: 1
        });
      }
    } finally {
      setIsLoading(false);
      setSelectedFile(null); 
    }
  }; // <--- 確保 handleUpload 的結束大括號在這裡

  const handleDownloadTemplate = () => {
    window.location.href = '/import_data_format_sample_utf8_bom.csv';
  };

  const handleDownloadExcelTemplate = () => {
    // Create Excel template download
    const csvData = '/import_data_format_sample_utf8_bom.csv';
    const link = document.createElement('a');
    link.href = csvData;
    link.download = 'staff_import_template.csv';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Box>
      {/* Header 移到Container外面，實現全寬展開 */}
      <Header userType={'admin'} userName={null} />
      
      <Container maxWidth="lg">
        <Box sx={{ mt: 3 }}>
          {/* 頁面標題和返回按鈕 */}
          <Paper elevation={3} sx={{ p: 4, mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h4" component="h1" gutterBottom sx={{ color: 'primary.main' }}>
                📥 導入員工資料 Import Staff Data
              </Typography>
              <Button 
                variant="outlined" 
                startIcon={<ArrowBackIcon />}
                onClick={() => navigate('/dashboard')}
                sx={{ minWidth: '120px' }}
              >
                返回主頁 Back to Dashboard
              </Button>
            </Box>
        
        {/* 說明區域 */}
        <Typography variant="h6" gutterBottom sx={{ color: 'primary.main' }}>
          📋 操作說明
        </Typography>
        <Typography variant="body1" paragraph>
          請上傳 CSV 格式的員工資料檔案。檔案的 Header 必須符合規定的格式。
          系統支援新增和更新員工資料，請確保資料準確性。
        </Typography>
        
        {/* 模板下載區域 */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom sx={{ color: 'success.main' }}>
            📋 模板下載 Template Download
          </Typography>
          <Grid container spacing={2}>
            <Grid item>
              <Button 
                variant="contained" 
                startIcon={<DownloadIcon />}
                onClick={handleDownloadTemplate}
                sx={{ minWidth: '200px' }}
              >
                下載CSV樣板 Download CSV Template
              </Button>
            </Grid>
            <Grid item>
              <Button 
                variant="contained" 
                color="success"
                startIcon={<DownloadIcon />}
                onClick={handleDownloadExcelTemplate}
                sx={{ minWidth: '200px', display: 'none' }}
              >
                下載 Excel 樣板
              </Button>
            </Grid>
          </Grid>
        </Box>

        <Divider sx={{ mb: 3 }} />

        {/* 文件選擇區域 */}
        <Box sx={{ mb: 3 }}>
          <FormLabel component="legend" sx={{ fontWeight: 'bold', mb: 2 }}>
            📎 選擇檔案 Select File
          </FormLabel>
          <Input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            sx={{ 
              width: '100%',
              maxWidth: '400px',
              p: 1,
              border: '2px dashed',
              borderColor: selectedFile ? 'success.main' : 'grey.300',
              borderRadius: 2,
              bgcolor: selectedFile ? 'success.light' : 'grey.50'
            }}
          />
          {selectedFile && (
            <Chip 
              icon={<CheckCircleIcon />}
              label={selectedFile.name}
              color="success"
              variant="outlined"
              sx={{ mt: 1 }}
            />
          )}
        </Box>
        
        {/* 上傳按鈕 */}
        <Button 
          variant="contained"
          size="large"
          startIcon={<CloudUploadIcon />}
          onClick={handleUpload} 
          disabled={!selectedFile || isLoading}
          sx={{ 
            minWidth: '200px',
            bgcolor: 'warning.main',
            '&:hover': { bgcolor: 'warning.dark' }
          }}
        >
          {isLoading ? '正在導入...' : '🚀 上傳並導入 Upload & Import'}
        </Button>

        {/* 進度條 */}
        {isLoading && (
          <Box sx={{ mt: 2 }}>
            <LinearProgress />
          </Box>
        )}
        
        {/* 結果顯示區域 */}
        {uploadStatus && (
          <Alert 
            severity={uploadStatus.includes('失敗') || uploadStatus.includes('錯誤') ? 'error' : 'success'}
            icon={uploadStatus.includes('失敗') ? <ErrorIcon /> : <CheckCircleIcon />}
            sx={{ mt: 2, mb: 2 }}
          >
            <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
              導入狀態：{uploadStatus}
            </Typography>
          </Alert>
        )}

        {/* 錯誤詳情和統計 */}
        {uploadResult && (uploadResult.errors || uploadResult.error_count > 0) && (
          <Card sx={{ mt: 2, mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" color="error" gutterBottom>
                  ❌ 錯誤詳情 Error Details
                </Typography>
                {(uploadResult.imported_count !== undefined || uploadResult.error_count !== undefined) && (
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <Chip 
                      label={`成功 Success: ${uploadResult.imported_count || 0}`}
                      color="success"
                      size="small"
                    />
                    <Chip 
                      label={`失敗 Failed: ${uploadResult.error_count || 0}`}
                      color="error" 
                      size="small"
                    />
                  </Box>
                )}
              </Box>
              
              {uploadResult.errors && uploadResult.errors.length > 0 && (
                <List dense sx={{ bgcolor: 'error.light', borderRadius: 1, p: 1 }}>
                  {uploadResult.errors.map((err, index) => (
                    <ListItem key={index} sx={{ py: 0.5 }}>
                      <ListItemText 
                        primary={err}
                        primaryTypographyProps={{
                          variant: 'body2',
                          color: 'error.dark',
                          fontFamily: 'monospace'
                        }}
                      />
                    </ListItem>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        )}
        </Paper>

        {/* 格式說明區域 */}
        <Paper elevation={2} sx={{ p: 3, mt: 3 }}>
          <Typography variant="h6" gutterBottom sx={{ color: 'info.main' }}>
            📝 CSV 檔案格式說明 File Format Guide
          </Typography>
          <Typography variant="body1" paragraph>
            <strong>✅ 使用標準英文 Header 格式</strong>，兼容所有平台。
          </Typography>
          
          <Card variant="outlined" sx={{ bgcolor: 'grey.50', mb: 2 }}>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
                📋 Header 格式範例：
              </Typography>
              <Box component="pre" sx={{ 
                fontSize: '0.875rem', 
                overflow: 'auto',
                bgcolor: 'grey.100',
                p: 2,
                borderRadius: 1,
                fontFamily: 'monospace'
              }}>
staff_id,staff_name,employment_type,name_chinese,name_foreign,gender,
is_foreign_national,is_master,is_phd,is_overseas_study,is_active...
              </Box>
              <Box sx={{ mt: 2 }}>
                <Chip label="✅ 支援 Windows" color="success" size="small" sx={{ mr: 1 }} />
                <Chip label="✅ 支援 Mac" color="success" size="small" sx={{ mr: 1 }} />
                <Chip label="✅ 支援 Linux" color="success" size="small" />
              </Box>
            </CardContent>
          </Card>
          
          <Typography variant="body1" paragraph>
            <strong>🔧 系統自動處理：</strong>支援 CSV 格式，自動識別欄位類型。
          </Typography>
          <Typography variant="body1" paragraph>
            布林值欄位請使用 <code style={{ bgcolor: '#f5f5f5', padding: '2px 4px', borderRadius: '4px' }}>True/False</code> 或 <code style={{ bgcolor: '#f5f5f5', padding: '2px 4px', borderRadius: '4px' }}>1/0</code>。
          </Typography>
        </Paper>
        
        {/* 版權頁腳 */}
        <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 4, mb: 2 }}>
          Copyright © Pui Ching Middle School (Coloane Campus) 2025. All Rights Reserved.
        </Typography>
        </Box>
      </Container>
    </Box>
  );
}

export default ImportStaffData;