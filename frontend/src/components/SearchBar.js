import React from 'react';
import { TextField, IconButton, InputAdornment, Box } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

function SearchBar({ searchTerm, onSearchChange, onSearchSubmit }) {
  return (
    <Box sx={{ p: 2, display: 'flex', alignItems: 'center', backgroundColor: 'background.paper', borderBottom: '1px solid #ccc' }}>
      <TextField
        fullWidth
        variant="outlined"
        label="搜索員工 Search Staff (例如：姓名、部門 e.g., Name, Department)"
        value={searchTerm}
        onChange={onSearchChange}
        sx={{ mr: 1 }}
        InputProps={{
          endAdornment: (
            <InputAdornment position="end">
              <IconButton type="submit" aria-label="search" onClick={onSearchSubmit} edge="end">
                <SearchIcon />
              </IconButton>
            </InputAdornment>
          ),
        }}
        onKeyPress={(event) => {
          if (event.key === 'Enter') {
            onSearchSubmit();
          }
        }}
      />
    </Box>
  );
}

export default SearchBar;