import React from 'react';
import { Box, Typography } from '@mui/material';

const Footer = () => {
  return (
    <Box
      component="footer"
      sx={{
        mt: 'auto',
        py: 2,
        px: 2,
        backgroundColor: '#f5f5f5',
        borderTop: '1px solid #e0e0e0',
        textAlign: 'center'
      }}
    >
      <Typography variant="body2" color="text.secondary">
        Copyright © Pui Ching Middle School (Coloane Campus) 2025. All Rights Reserved.
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mt: 1, fontSize: '0.75rem' }}>
        培正中學（路環校區） | Pui Ching Middle School (Coloane Campus)
      </Typography>
    </Box>
  );
};

export default Footer;