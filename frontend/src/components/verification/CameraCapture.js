import React from 'react';
import { Box, Button, Typography } from '@mui/material';
import PhotoCameraIcon from '@mui/icons-material/PhotoCamera';

const CameraCapture = ({ onCapture }) => {
  return (
    <Box textAlign="center" p={2}>
      <PhotoCameraIcon sx={{ fontSize: 48, color: 'grey.500', mb: 2 }} />
      <Typography variant="body2" gutterBottom>
        Camera capture coming soon...
      </Typography>
      <Button 
        variant="outlined" 
        startIcon={<PhotoCameraIcon />}
        onClick={() => onCapture && onCapture()}
      >
        Open Camera
      </Button>
    </Box>
  );
};

export default CameraCapture;
