import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes, useNavigate } from 'react-router-dom';
import { Container, Box, Typography, TextField, Button, Link as MuiLink } from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import Dashboard from './pages/Dashboard';
import StaffRegistration from './pages/StaffRegistration';
import ImportStaffData from './pages/ImportStaffData';
import BatchPhotoUpload from './pages/BatchPhotoUpload';
import ProtectedRoute from './ProtectedRoute';
import SSLNotification from './components/SSLNotification';
import axios from 'axios';
import { LanguageProvider } from './components/LanguageContext';

const theme = createTheme({
  palette: {
    primary: {
      main: '#003366',
    },
    secondary: {
      main: '#FFD700',
    },
    error: {
      main: '#FF0000',
    },
  },
  typography: {
    fontFamily: 'Arial, sans-serif',
    h4: {
      fontWeight: 600,
    },
  },
});

function LoginPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  // const [loggedIn, setLoggedIn] = useState(false); // loggedIn 狀態在 LoginPage 中未使用，可以考慮移除或根據需要保留

  const handleLogin = async () => {
    try {
        const response = await axios.post('/api/api-token-auth/', {
            username: username,
            password: password,
        });
        localStorage.setItem('token', response.data.token);
        // setLoggedIn(true); // loggedIn 狀態在 LoginPage 中未使用
        navigate('/dashboard');
    } catch (error) {
      setError(error.message);
    }
  };

  const handleForgotPassword = () => {
    alert('請聯絡 IT Support 尋求協助。'); // Or use a more sophisticated modal/dialog
  };

  return (
      <Container component="main" maxWidth="xs">
        <Box
          sx={{
            marginTop: 8,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            p: 4,
            borderRadius: 2,
            boxShadow: '0px 4px 20px rgba(0, 0, 0, 0.1)',
            backgroundColor: 'white',
          }}
        >
          <img src="/pcmsco_logo.jpeg" alt="Pui Ching Logo" style={{ width: '100px', marginBottom: '20px' }} />
          <Typography component="h1" variant="h4" sx={{ mb: 3, color: 'primary.main' }}>
            培正教職員系統 PCMS HR Login
          </Typography>
          {error && (
            <Typography color="error" variant="body2" sx={{ mb: 2 }}>
              {error}
            </Typography>
          )}
          <TextField
            margin="normal"
            required
            fullWidth
            id="username"
            label="用戶名 Username"
            name="username"
            autoComplete="username"
            autoFocus
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            name="password"
            label="密碼 Password"
            type="password"
            id="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2, py: 1.5, fontSize: '1.1rem' }}
            onClick={handleLogin}
          >
            登錄 Login
          </Button>
          <MuiLink component="button" variant="body2" onClick={handleForgotPassword} sx={{ color: 'primary.main', cursor: 'pointer' }}>
            忘記密碼？ Forgot Password?
          </MuiLink>
        </Box>
        <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 5 }}>
          <div style={{ textAlign: 'center', marginTop: '20px', color: '#757575', fontSize: '0.9em' }}>
            Copyright © Pui Ching Middle School (Coloane Campus) {new Date().getFullYear()}. All Rights Reserved.
          </div>
        </Typography>
      </Container>
  );
}

function App() {
  return (
    <LanguageProvider>
      <ThemeProvider theme={theme}>
        <Router>
          <SSLNotification />
          <Routes>
            <Route path="/" element={<LoginPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/staff-registration" element={<StaffRegistration />} />
            <Route path="/import-staff-data" element={<ImportStaffData />} />
            <Route path="/batch-photo-upload" element={<BatchPhotoUpload />} />
            <Route element={<ProtectedRoute />}>
              <Route path="/dashboard" element={<Dashboard />} />
            </Route>
          </Routes>
        </Router>
      </ThemeProvider>
    </LanguageProvider>
  );
}

export default App;
