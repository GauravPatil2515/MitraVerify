import React from 'react';
import { Box, Typography, LinearProgress, Chip } from '@mui/material';

const ProgressTracker = () => {
  return (
    <Box p={3}>
      <Typography variant="h6" gutterBottom>
        Learning Progress
      </Typography>
      <Box mb={2}>
        <Typography variant="body2" gutterBottom>
          Digital Literacy Basics
        </Typography>
        <LinearProgress variant="determinate" value={75} />
        <Typography variant="caption" color="textSecondary">
          75% Complete
        </Typography>
      </Box>
      <Box mb={2}>
        <Chip label="Beginner" color="primary" size="small" />
        <Chip label="3 Modules Completed" color="success" size="small" sx={{ ml: 1 }} />
      </Box>
    </Box>
  );
};

export default ProgressTracker;
