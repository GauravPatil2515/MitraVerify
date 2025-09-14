import React from 'react';
import { Card, CardContent, Typography, Chip } from '@mui/material';

const ResultCard = ({ result }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'verified': return 'success';
      case 'false': return 'error';
      case 'questionable': return 'warning';
      default: return 'default';
    }
  };

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Verification Result
        </Typography>
        <Chip 
          label={result?.status || 'Unknown'} 
          color={getStatusColor(result?.status)}
          sx={{ mb: 1 }}
        />
        <Typography variant="body2">
          {result?.explanation || 'No explanation available'}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default ResultCard;
