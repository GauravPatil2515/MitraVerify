import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const ResultsDisplay = () => {
  return (
    <Container>
      <Box py={4}>
        <Typography variant="h4" gutterBottom>
          Verification Results
        </Typography>
        <Typography variant="body1">
          Results display coming soon...
        </Typography>
      </Box>
    </Container>
  );
};

export default ResultsDisplay;
