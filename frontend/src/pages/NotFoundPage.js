import React from 'react';
import { Container, Typography, Box, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const NotFoundPage = () => {
  const navigate = useNavigate();

  return (
    <Container>
      <Box py={8} textAlign="center">
        <Typography variant="h2" gutterBottom>404</Typography>
        <Typography variant="h5" gutterBottom>Page Not Found</Typography>
        <Typography variant="body1" paragraph>
          The page you're looking for doesn't exist.
        </Typography>
        <Button variant="contained" onClick={() => navigate('/')}>
          Go Home
        </Button>
      </Box>
    </Container>
  );
};

export default NotFoundPage;
