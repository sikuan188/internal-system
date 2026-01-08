import React, { useState } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  Button, 
  Alert, 
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  Divider,
  Chip,
  Container,
  Grid
} from '@mui/material';
import { 
  CloudUpload as CloudUploadIcon,
  Photo as PhotoIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  ArrowBack as ArrowBackIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';

function BatchPhotoUpload() {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResults, setUploadResults] = useState(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setUploadStatus('');
    setUploadResults(null);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const files = event.dataTransfer.files;
    if (files.length > 0) {
      setSelectedFile(files[0]);
      setUploadStatus('');
      setUploadResults(null);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus('請先選擇一個ZIP檔案');
      return;
    }

    if (!selectedFile.name.toLowerCase().endsWith('.zip')) {
      setUploadStatus('請選擇ZIP格式的檔案');
      return;
    }

    setIsUploading(true);
    setUploadStatus('');
    setUploadResults(null);

    try {
      const formData = new FormData();
      formData.append('zip_file', selectedFile);
      formData.append('upload_type', 'zip');

      const token = localStorage.getItem('token');
      const headers = token ? { 'Authorization': `Token ${token}` } : {};

      const response = await fetch('/api/staff/batch-photo-upload/', {
        method: 'POST',
        headers: headers,
        body: formData
      });

      const result = await response.json();

      if (response.ok && result.status === 'success') {
        setUploadResults(result);
        setUploadStatus(`成功上傳 ${result.success_count} 張照片！`);
        // 清除選擇的文件
        setSelectedFile(null);
        // 重置文件輸入
        const fileInput = document.getElementById('zip-file-input');
        if (fileInput) fileInput.value = '';
      } else {
        setUploadStatus(`上傳失敗: ${result.message}`);
      }
    } catch (error) {
      console.error('批量照片上傳錯誤:', error);
      setUploadStatus('上傳過程中發生錯誤，請稍後重試');
    } finally {
      setIsUploading(false);
    }
  };

  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };

  return (
    <Box>
      {/* Header 移到Container外面，實現全寬展開 */}
      <Header userType={'admin'} userName={null} />
      
      <Container maxWidth="lg">
        <Box sx={{ mt: 3 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          {/* 頁面標題和返回按鈕 */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Box display="flex" alignItems="center">
              <PhotoIcon sx={{ mr: 2, fontSize: 32, color: 'primary.main' }} />
              <Typography variant="h4" component="h1" color="primary.main">
                批量上傳員工照片 Batch Photo Upload
              </Typography>
            </Box>
            <Button 
              variant="outlined" 
              startIcon={<ArrowBackIcon />}
              onClick={handleBackToDashboard}
              sx={{ minWidth: '120px' }}
            >
              返回主頁 Back to Dashboard
            </Button>
          </Box>

          {/* 使用說明 */}
          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              📋 使用說明 Instructions
            </Typography>
            <Typography component="div">
              <strong>1. 準備照片文件：</strong>
              <br />• 將所有員工照片放在一個ZIP檔案中
              <br />• 照片文件名必須是員工編號 (例如：TEMP-1.jpg, STAFF-001.png)
              <br />• 支援格式：JPG、JPEG、PNG、GIF
              <br />
              <br />
              <strong>2. 上傳方式：</strong>
              <br />• 點擊「選擇ZIP檔案」按鈕，或
              <br />• 直接拖放ZIP檔案到下方區域
              <br />
              <br />
              <strong>3. 注意事項：</strong>
              <br />• 如果員工已有照片，新照片會覆蓋舊照片
              <br />• 找不到對應員工編號的照片會被跳過
              <br />• 上傳完成後會顯示詳細的結果報告
            </Typography>
          </Alert>

          {/* 文件上傳區域 */}
          <Paper 
            elevation={1} 
            sx={{ 
              p: 4, 
              mb: 3, 
              border: '2px dashed #ccc',
              borderColor: selectedFile ? 'primary.main' : '#ccc',
              backgroundColor: selectedFile ? 'action.hover' : 'background.paper',
              cursor: 'pointer',
              '&:hover': {
                borderColor: 'primary.main',
                backgroundColor: 'action.hover'
              }
            }}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onClick={() => document.getElementById('zip-file-input').click()}
          >
            <Box textAlign="center">
              <CloudUploadIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                {selectedFile ? `已選擇: ${selectedFile.name}` : '點擊選擇或拖放ZIP檔案'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                拖放ZIP檔案到此區域，或點擊選擇檔案
              </Typography>
              {selectedFile && (
                <Chip 
                  label={`文件大小: ${(selectedFile.size / 1024 / 1024).toFixed(2)} MB`}
                  color="primary" 
                  sx={{ mt: 2 }}
                />
              )}
            </Box>
          </Paper>

          {/* 隱藏的文件輸入 */}
          <input
            id="zip-file-input"
            type="file"
            accept=".zip"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />

          {/* 操作按鈕 */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item>
              <Button
                variant="contained"
                color="primary"
                size="large"
                startIcon={<CloudUploadIcon />}
                onClick={handleUpload}
                disabled={!selectedFile || isUploading}
              >
                {isUploading ? '上傳中...' : '開始上傳 Start Upload'}
              </Button>
            </Grid>
          </Grid>

          {/* 上傳進度條 */}
          {isUploading && (
            <Box sx={{ mb: 3 }}>
              <LinearProgress />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                正在處理ZIP檔案並上傳照片，請稍候...
              </Typography>
            </Box>
          )}

          {/* 上傳狀態消息 */}
          {uploadStatus && (
            <Alert 
              severity={uploadResults && uploadResults.status === 'success' ? 'success' : 'error'} 
              sx={{ mb: 3 }}
            >
              {uploadStatus}
            </Alert>
          )}

          {/* 上傳結果詳情 */}
          {uploadResults && (
            <Paper elevation={2} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom color="primary.main">
                📊 上傳結果 Upload Results
              </Typography>
              
              <Grid container spacing={3} sx={{ mb: 2 }}>
                <Grid item xs={12} sm={4}>
                  <Box display="flex" alignItems="center">
                    <CheckCircleIcon sx={{ color: 'success.main', mr: 1 }} />
                    <Typography variant="h6" color="success.main">
                      成功: {uploadResults.success_count} 張
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12} sm={4}>
                  <Box display="flex" alignItems="center">
                    <ErrorIcon sx={{ color: 'error.main', mr: 1 }} />
                    <Typography variant="h6" color="error.main">
                      失敗: {uploadResults.error_count} 張
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12} sm={4}>
                  <Typography variant="h6" color="text.primary">
                    總計: {uploadResults.success_count + uploadResults.error_count} 張
                  </Typography>
                </Grid>
              </Grid>

              {/* 錯誤詳情 */}
              {uploadResults.errors && uploadResults.errors.length > 0 && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" gutterBottom color="error.main">
                    ❌ 錯誤詳情 Error Details
                  </Typography>
                  <List>
                    {uploadResults.errors.map((error, index) => (
                      <ListItem key={index}>
                        <ListItemText primary={error} />
                      </ListItem>
                    ))}
                    {uploadResults.error_count > uploadResults.errors.length && (
                      <ListItem>
                        <ListItemText 
                          primary={`... 還有 ${uploadResults.error_count - uploadResults.errors.length} 個錯誤未顯示`}
                          secondary="查看後端日誌獲取完整錯誤信息"
                        />
                      </ListItem>
                    )}
                  </List>
                </>
              )}
            </Paper>
          )}

          {/* 版權頁腳 */}
          <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 4 }}>
            Copyright © Pui Ching Middle School (Coloane Campus) 2025. All Rights Reserved.
          </Typography>
        </Paper>
        </Box>
      </Container>
    </Box>
  );
}

export default BatchPhotoUpload;