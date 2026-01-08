import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Box, Grid, CircularProgress, Alert, Typography, Paper } from '@mui/material';
import Header from '../components/Header';
// import SearchBar from '../components/SearchBar'; // SearchBar will be moved to FilterSection
import StaffListSection from '../components/StaffListSection';
import StaffDetailSection from '../components/StaffDetailSection';
import FilterSection from '../components/FilterSection';
import '../styles/Dashboard.css'; // Ensure CSS is imported
import fieldLabels from '../components/fieldLabels'; // Import fieldLabels

// 新增 StatisticsSection 組件
const StatisticsSection = ({ stats }) => {
  const bi = (key, fallback) => {
    const lbl = fieldLabels[key];
    if (lbl) return `${lbl.zh} ${lbl.en}`;
    return fallback || key;
  };
  if (!stats) return null;
  return (
    // Already has p: 2, which is padding. We can increase if needed or ensure consistency.
    <Paper elevation={3} sx={{ p: 2, mb: 2 }}> 
      <Typography variant="h6" gutterBottom sx={{ color: 'primary.main' }}>
        {bi('statistics_section_title', '統計數據 (基於目前篩選結果) Statistics')}
      </Typography>
      <Grid container spacing={1}>
        <Grid item xs={12} sm={6} md={4}>
          <Typography>{bi('total_staff_count', '總人數 Total Staff')}: {stats.totalStaff}</Typography>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Typography>{bi('phd_count', '博士人數 PhD Count')}: {stats.phdCount}</Typography>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Typography>{bi('master_count', '碩士人數 Master Count')}: {stats.masterCount}</Typography>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Typography>{bi('overseas_study_count', '留學人數 Overseas Study Count')}: {stats.overseasStudyCount}</Typography>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Typography>{bi('foreign_national_count', '外籍員工人數 Foreign National Count')}: {stats.foreignNationalCount}</Typography>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Typography>{bi('male_count', '男性人數 Male Count')}: {stats.maleCount}</Typography>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Typography>{bi('female_count', '女性人數 Female Count')}: {stats.femaleCount}</Typography>
        </Grid>
      </Grid>
    </Paper>
  );
};

const Dashboard = () => {
  const [staffList, setStaffList] = useState([]);
  const [selectedStaff, setSelectedStaff] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    gender: null,
    is_phd: false,
    is_master: false,
    is_overseas_study: false,
    is_foreign_national: false,
    seniority: [0, 30], // Adjusted default seniority range
    sortBy: '' // 新增排序方式狀態
  });
  const [statistics, setStatistics] = useState(null);

  // 增強的性別識別函數 - 支持多種性別表示方式的排列組合
  const identifyGender = (genderValue) => {
    if (!genderValue) return null;
    
    // 轉換為字符串並去除前後空格，統一處理
    const value = genderValue.toString().trim();
    
    // 男性模式匹配 - 支持：男, Male/male/MALE, M/m, 以及各種中英文混合組合
    const malePatterns = /^(男|male|m|男\s*male|男\s*m|male\s*男|m\s*男|男\s*MALE|MALE\s*男)$/i;
    
    // 女性模式匹配 - 支持：女, Female/female/FEMALE, F/f, 以及各種中英文混合組合  
    const femalePatterns = /^(女|female|f|女\s*female|女\s*f|female\s*女|f\s*女|女\s*FEMALE|FEMALE\s*女)$/i;
    
    if (malePatterns.test(value)) return 'male';
    if (femalePatterns.test(value)) return 'female';
    
    return null; // 無法識別的性別格式
  };

  // 測試性別識別函數 (開發階段使用)
  React.useEffect(() => {
    // 測試各種性別格式
    const testCases = [
      '男', 'Male', 'male', 'MALE', 'M', 'm',
      '女', 'Female', 'female', 'FEMALE', 'F', 'f'
    ];
    
    console.log('性別識別測試結果:');
    testCases.forEach(testCase => {
      const result = identifyGender(testCase);
      console.log(`"${testCase}" -> ${result}`);
    });
  }, []); // 只在組件載入時執行一次

  const fetchStaffList = useCallback(async (termToSearch) => {
    setIsLoading(true);
    setError(null);
    let url = '/api/staff/profiles/';
    const params = new URLSearchParams();
    // Fetching logic will now primarily be driven by useEffect based on searchTerm and filters
    // So, termToSearch might not be directly passed here if search is part of filters
    if (termToSearch) { // Keep this if backend supports direct search query param
        params.append('search', termToSearch);
    }
    const queryString = params.toString();
    if (queryString) {
      url += `?${queryString}`;
    }
    try {
      const token = localStorage.getItem('token');
      const staffResponse = await fetch(url, {
        headers: token ? { 'Authorization': `Token ${token}` } : {}
      });
      if (!staffResponse.ok) {
        let errorData = null;
        try { errorData = await staffResponse.json(); } catch (e) { /* ignore */ }
        throw new Error(`HTTP error! status: ${staffResponse.status}, message: ${errorData ? JSON.stringify(errorData) : staffResponse.statusText}`);
      }
      const staffDataFromAPI = await staffResponse.json();
      setStaffList(staffDataFromAPI);
    } catch (err) {
      setError(err.message || "獲取數據失敗，請稍後再試");
      setStaffList([]);
    } finally {
      setIsLoading(false);
    }
  }, []); // Removed searchTerm from dependencies as it's handled by FilterSection now

  useEffect(() => {
    // Initial fetch or fetch when global search term changes (if any outside FilterSection)
    // For now, assuming FilterSection handles its own search term and triggers re-filter
    fetchStaffList(); 
  }, [fetchStaffList]);

  const handleStaffSelect = (staff) => {
    setSelectedStaff(prev => prev && prev.staff_id === staff.staff_id ? null : staff);
  };

  const handleCloseStaffDetail = () => {
    setSelectedStaff(null);
  };

  // handleSearchChange and handleSearchSubmit will be managed by FilterSection
  // const handleSearchChange = (event) => {
  //   setSearchTerm(event.target.value);
  // };

  // const handleSearchSubmit = () => {
  //   fetchStaffList(searchTerm);
  // };

  const applyFilters = useCallback((listToFilter, currentSearchTerm, currentFilters) => {
    let processedList = listToFilter;

    // Apply search term first if provided from FilterSection
    if (currentSearchTerm) {
      processedList = processedList.filter(staff => {
        const term = currentSearchTerm.toLowerCase();
        const deepSearch = (obj) => {
          if (obj === null || obj === undefined) return false;
          if (Array.isArray(obj)) return obj.some(item => deepSearch(item));
          if (typeof obj === 'object') return Object.values(obj).some(value => deepSearch(value));
          if (typeof obj === 'string') return obj.toLowerCase().includes(term);
          if (typeof obj === 'number' || typeof obj === 'boolean') return obj.toString().toLowerCase().includes(term);
          return false;
        };
        return deepSearch(staff);
      });
    }
    
    // Apply other filters
    processedList = processedList.filter(staff => {
      if (currentFilters.gender) {
        const identifiedGender = identifyGender(staff.gender);
        if (identifiedGender !== currentFilters.gender) {
          return false;
        }
      }
      // 年資篩選 - 改進處理邏輯
      if (currentFilters.seniority && currentFilters.seniority.length === 2) {
        let years = 0;
        if (staff.school_seniority_description) {
          const match = staff.school_seniority_description.match(/(\d+)年(\d+)個月/);
          if (match) {
            years = parseInt(match[1]) + parseInt(match[2]) / 12;
          }
        }
        // 如果年資不在指定範圍內，過濾掉
        if (years < currentFilters.seniority[0] || years > currentFilters.seniority[1]) return false;
      }
      // 學歷篩選 - 使用全局標記而非學歷記錄標記
      if (currentFilters.is_phd && !staff.is_phd) return false;
      if (currentFilters.is_master && !staff.is_master) return false;
      if (currentFilters.is_overseas_study && !staff.is_overseas_study) return false;
      if (currentFilters.is_foreign_national && !staff.is_foreign_national) return false;
      return true;
    });

    // Apply sorting
    if (currentFilters.sortBy) {
      processedList = [...processedList].sort((a, b) => {
        switch (currentFilters.sortBy) {
          case 'name_asc':
            // 使用正確的姓名欄位進行排序
            const nameA = (a.name_chinese && a.name_chinese !== '/' && a.name_chinese.trim()) 
              ? a.name_chinese 
              : (a.name_foreign || a.staff_name || '');
            const nameB = (b.name_chinese && b.name_chinese !== '/' && b.name_chinese.trim()) 
              ? b.name_chinese 
              : (b.name_foreign || b.staff_name || '');
            return nameA.localeCompare(nameB, 'zh-Hant-TW');
          case 'name_desc':
            const nameA_desc = (a.name_chinese && a.name_chinese !== '/' && a.name_chinese.trim()) 
              ? a.name_chinese 
              : (a.name_foreign || a.staff_name || '');
            const nameB_desc = (b.name_chinese && b.name_chinese !== '/' && b.name_chinese.trim()) 
              ? b.name_chinese 
              : (b.name_foreign || b.staff_name || '');
            return nameB_desc.localeCompare(nameA_desc, 'zh-Hant-TW');
          case 'entry_date_asc':
            return new Date(a.entry_date || 0) - new Date(b.entry_date || 0);
          case 'entry_date_desc':
            return new Date(b.entry_date || 0) - new Date(a.entry_date || 0);
          case 'staff_id_asc':
            return (a.staff_id || '').localeCompare(b.staff_id || '');
          case 'staff_id_desc':
            return (b.staff_id || '').localeCompare(a.staff_id || '');
          default:
            return 0;
        }
      });
    }

    return processedList;
  }, []);

  const filteredStaffList = useMemo(() => {
    return applyFilters(staffList, searchTerm, filters);
  }, [staffList, searchTerm, filters, applyFilters]);

  useEffect(() => {
    if (filteredStaffList) { // Check if filteredStaffList is not null/undefined
      const stats = {
        totalStaff: filteredStaffList.length,
        phdCount: filteredStaffList.filter(staff => staff.is_phd).length,
        masterCount: filteredStaffList.filter(staff => staff.is_master).length,
        overseasStudyCount: filteredStaffList.filter(staff => staff.is_overseas_study).length,
        foreignNationalCount: filteredStaffList.filter(staff => staff.is_foreign_national).length,
        maleCount: filteredStaffList.filter(staff => {
          const identifiedGender = identifyGender(staff.gender);
          return identifiedGender === 'male';
        }).length,
        femaleCount: filteredStaffList.filter(staff => {
          const identifiedGender = identifyGender(staff.gender);
          return identifiedGender === 'female';
        }).length,
      };
      setStatistics(stats);
    } else {
      setStatistics({
        totalStaff: 0, phdCount: 0, masterCount: 0, overseasStudyCount: 0,
        foreignNationalCount: 0, maleCount: 0, femaleCount: 0,
      });
    }
  }, [filteredStaffList]);

  if (isLoading && staffList.length === 0) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}><CircularProgress /></Box>;
  }
  // Removed early return for error to ensure layout is rendered for FilterSection
  // if (error) {
  //   return <Box sx={{ p: 2 }}><Alert severity="error">{error}</Alert></Box>;
  // }

  return (
    <Box className="dashboard-container">
      {/* 傳遞 userType prop 給 Header 組件 */}
      {/* TODO: 將 'admin' 替換為從用戶登錄狀態或數據中獲取的真實 userType */}
      <Header userType={'admin'} userName={null} /> 
      <Box className="dashboard-content">
        <Grid container spacing={2} className="dashboard-grid-container">
          {/* Left Column: Filters, Statistics, Staff List */}
          <Grid item xs={12} md={selectedStaff ? 4 : 12} className="left-column">
            {/* FilterSection's internal Paper already has p: 2 */}
            <FilterSection 
              filters={filters} 
              setFilters={setFilters} 
              searchTerm={searchTerm} 
              setSearchTerm={setSearchTerm} 
            />
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            {/* StatisticsSection's internal Paper already has p: 2 */}
            <StatisticsSection stats={statistics} />
            {/* Paper for StaffListSection, ensure it also has consistent padding */}
            <Paper elevation={3} sx={{ p: 2, mt: 2, flexGrow: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}> 
              <StaffListSection 
                staffList={filteredStaffList} 
                onStaffCardClick={handleStaffSelect} 
                searchTerm={searchTerm} 
              />
            </Paper>
          </Grid>

          {/* Right Column: Staff Details (conditionally rendered) */}
          {selectedStaff && (
            <Grid item xs={12} md={8} className="right-column">
              {/* StaffDetailSection might also benefit from consistent padding if it uses Paper or similar */}
              <StaffDetailSection 
                staff={selectedStaff} 
                onClose={handleCloseStaffDetail} 
                searchTerm={searchTerm}
              />
            </Grid>
          )}
        </Grid>
      </Box>

      {/* 頁腳 */}
      <Box sx={{ mt: 4, py: 2, textAlign: 'center', borderTop: 1, borderColor: 'divider' }}>
        <Typography variant="body2" color="text.secondary">
          Copyright © Pui Ching Middle School (Coloane Campus) 2025. All Rights Reserved.
        </Typography>
      </Box>
    </Box>
  );
};

export default Dashboard;
