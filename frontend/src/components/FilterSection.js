import React from 'react'; // Removed unused useContext
import { Box, FormControl, FormLabel, Checkbox, Slider, Typography, TextField, IconButton, Grid, Paper, FormControlLabel, Button, Select, MenuItem, InputLabel } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import GetAppIcon from '@mui/icons-material/GetApp'; // Phase 3: Excel匯出圖標
import SortIcon from '@mui/icons-material/Sort'; // Phase 3: 排序圖標

const FilterSection = ({ filters, setFilters, searchTerm, setSearchTerm }) => {

  const handleGenderChange = (event) => {
    const { name, checked } = event.target;
    if (checked) {
      // 如果勾選了這個選項，設置為對應的性別
      setFilters({...filters, gender: name});
    } else {
      // 如果取消勾選，清除性別篩選
      setFilters({...filters, gender: null});
    }
  };

  const handleCheckboxChange = (event) => {
    setFilters({...filters, [event.target.name]: event.target.checked });
  };

  const handleSeniorityChange = (event, newValue) => {
    setFilters({...filters, seniority: newValue });
  };

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };

  // Phase 3: Excel匯出功能
  const handleExportExcel = async () => {
    try {
      // 構建查詢參數，基於當前篩選條件
      const params = new URLSearchParams();
      
      if (filters.gender) {
        params.append('gender', filters.gender === 'male' ? 'M' : 'F');
      }
      
      if (filters.is_foreign_national) {
        params.append('is_foreign_national', 'true');
      }
      
      const token = localStorage.getItem('token');
      const headers = token ? { 'Authorization': `Token ${token}` } : {};
      
      // 發送請求到後端
      const response = await fetch(`/api/staff/export/excel/?${params.toString()}`, {
        method: 'GET',
        headers: headers
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // 下載文件
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `員工資料_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error('Excel匯出失敗:', error);
      alert('Excel匯出失敗，請稍後重試');
    }
  };

  // Phase 3: 排序功能
  const handleSortChange = (event) => {
    setFilters({...filters, sortBy: event.target.value});
  };

  return (
    <Paper elevation={2} sx={{ p: 2, mb: 2 }} className="filter-section-container">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" sx={{ color: 'primary.main' }}>
          篩選條件 Filter Conditions
        </Typography>
        {/* Phase 3: Excel匯出按鈕 - 暫時隱藏 */}
        <Button
          variant="contained"
          color="success"
          startIcon={<GetAppIcon />}
          onClick={handleExportExcel}
          size="small"
          sx={{ display: 'none' }} // 隱藏按鈕但保留程式碼
        >
          匯出Excel Export Excel
        </Button>
      </Box>
      <Box mb={2} className="search-bar-in-filter">
        <TextField 
          fullWidth 
          variant="outlined" 
          label="搜索員工 Search Staff (例如：姓名、部門 e.g., Name, Department)" 
          value={searchTerm}
          onChange={handleSearchChange}
          InputProps={{
            endAdornment: (
              <IconButton>
                <SearchIcon />
              </IconButton>
            )
          }}
        />
      </Box>
      <Grid container spacing={1.5} alignItems="flex-start"> {/* Reduced spacing for compact layout */}
        {/* Gender Filter - 垂直布局 */}
        <Grid item xs={12}>
          <Box>
            <FormLabel component="legend" sx={{ display: 'block', mb: 1, fontSize: '0.875rem', fontWeight: 500 }}>
              性別 Gender:
            </FormLabel>
            <FormControl component="fieldset">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                <FormControlLabel
                  control={<Checkbox name="male" value="male" checked={filters.gender === 'male'} onChange={handleGenderChange} />}
                  label="男 Male"
                  sx={{ margin: 0, '& .MuiFormControlLabel-label': { fontSize: '0.875rem' } }}
                />
                <FormControlLabel
                  control={<Checkbox name="female" value="female" checked={filters.gender === 'female'} onChange={handleGenderChange} />}
                  label="女 Female"
                  sx={{ margin: 0, '& .MuiFormControlLabel-label': { fontSize: '0.875rem' } }}
                />
              </Box>
            </FormControl>
          </Box>
        </Grid>

        {/* Seniority Filter - 紧凑布局 */}
        <Grid item xs={12}>
          <Box>
            <FormLabel component="legend" sx={{ 
              display: 'block',
              mb: 1,
              fontSize: '0.875rem',
              fontWeight: 500
            }}>
              年資 Years: {filters.seniority ? `${filters.seniority[0]}-${filters.seniority[1]}年` : '0-30年'}
            </FormLabel>
            <Box sx={{ px: 1 }}>
              <Slider
                value={filters.seniority || [0, 30]}
                onChange={handleSeniorityChange}
                valueLabelDisplay="auto"
                min={0}
                max={50}
                valueLabelFormat={(value) => `${value}年`}
                marks={[
                  { value: 0, label: '0' },
                  { value: 25, label: '25' },
                  { value: 50, label: '50年' }
                ]}
                sx={{ 
                  width: '100%',
                  '& .MuiSlider-mark': { fontSize: '0.6rem' },
                  '& .MuiSlider-markLabel': { fontSize: '0.6rem' },
                  '& .MuiSlider-thumb': {
                    '&:hover, &.Mui-focusVisible': {
                      boxShadow: '0px 0px 0px 8px rgba(25, 118, 210, 0.16)',
                    },
                  },
                  '& .MuiSlider-valueLabel': {
                    fontSize: '0.7rem',
                  }
                }}
              />
            </Box>
          </Box>
        </Grid>

        {/* Boolean Checkboxes - 強制2x2排列 */}
        <Grid item xs={12}>
          <Box>
            <FormLabel component="legend" sx={{ 
              display: 'block',
              mb: 1,
              fontSize: '0.875rem',
              fontWeight: 500
            }}>
              篩選選項 Filter Options:
            </FormLabel>
            <Grid container spacing={1} sx={{ maxWidth: '100%' }}>
              <Grid item xs={6} sm={6} md={6}>
                <FormControlLabel
                  control={<Checkbox checked={filters.is_phd} onChange={handleCheckboxChange} name="is_phd" />}
                  label="博士學位 PhD"
                  sx={{ 
                    margin: 0, 
                    width: '100%',
                    '& .MuiFormControlLabel-label': { 
                      fontSize: '0.875rem',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis'
                    } 
                  }}
                />
              </Grid>
              <Grid item xs={6} sm={6} md={6}>
                <FormControlLabel
                  control={<Checkbox checked={filters.is_master} onChange={handleCheckboxChange} name="is_master" />}
                  label="碩士學位 Master"
                  sx={{ 
                    margin: 0, 
                    width: '100%',
                    '& .MuiFormControlLabel-label': { 
                      fontSize: '0.875rem',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis'
                    } 
                  }}
                />
              </Grid>
              <Grid item xs={6} sm={6} md={6}>
                <FormControlLabel
                  control={<Checkbox checked={filters.is_overseas_study} onChange={handleCheckboxChange} name="is_overseas_study" />}
                  label="留學經驗 Overseas"
                  sx={{ 
                    margin: 0, 
                    width: '100%',
                    '& .MuiFormControlLabel-label': { 
                      fontSize: '0.875rem',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis'
                    } 
                  }}
                />
              </Grid>
              <Grid item xs={6} sm={6} md={6}>
                <FormControlLabel
                  control={<Checkbox checked={filters.is_foreign_national} onChange={handleCheckboxChange} name="is_foreign_national" />}
                  label="外籍員工 Foreign"
                  sx={{ 
                    margin: 0, 
                    width: '100%',
                    '& .MuiFormControlLabel-label': { 
                      fontSize: '0.875rem',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis'
                    } 
                  }}
                />
              </Grid>
            </Grid>
          </Box>
        </Grid>
        
        {/* Phase 3: 排序選項 - 单独一行 */}
        <Grid item xs={12}>
          <FormControl size="small" fullWidth>
            <InputLabel sx={{ fontSize: '0.875rem' }}>排序方式 Sort By</InputLabel>
            <Select
              value={filters.sortBy || ''}
              onChange={handleSortChange}
              label="排序方式 Sort By"
              startAdornment={<SortIcon sx={{ mr: 1, color: 'text.secondary', fontSize: '1rem' }} />}
              sx={{ fontSize: '0.875rem' }}
            >
              <MenuItem value="" sx={{ fontSize: '0.875rem' }}>預設排序 Default</MenuItem>
              <MenuItem value="name_asc" sx={{ fontSize: '0.875rem' }}>姓名 (A-Z) Name (A-Z)</MenuItem>
              <MenuItem value="name_desc" sx={{ fontSize: '0.875rem' }}>姓名 (Z-A) Name (Z-A)</MenuItem>
              <MenuItem value="entry_date_asc" sx={{ fontSize: '0.875rem' }}>入職日期 (舊→新) Entry Date (Old→New)</MenuItem>
              <MenuItem value="entry_date_desc" sx={{ fontSize: '0.875rem' }}>入職日期 (新→舊) Entry Date (New→Old)</MenuItem>
              <MenuItem value="staff_id_asc" sx={{ fontSize: '0.875rem' }}>員工編號 (升序) Staff ID (Asc)</MenuItem>
              <MenuItem value="staff_id_desc" sx={{ fontSize: '0.875rem' }}>員工編號 (降序) Staff ID (Desc)</MenuItem>
            </Select>
          </FormControl>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default FilterSection;