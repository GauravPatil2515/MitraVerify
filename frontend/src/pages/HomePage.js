import React from 'react';
import { Container, Typography, Button, Box, Grid, Card, CardContent } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import VerifyIcon from '@mui/icons-material/VerifiedUser';
import SchoolIcon from '@mui/icons-material/School';
import SpeedIcon from '@mui/icons-material/Speed';

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="lg">
      {/* Hero Section */}
      <Box textAlign="center" py={8}>
        <Typography variant="h2" component="h1" gutterBottom color="primary">
          MitraVerify
        </Typography>
        <Typography variant="h5" color="textSecondary" gutterBottom>
          AI-Powered Misinformation Detection for India
        </Typography>
        <Typography variant="body1" color="textSecondary" paragraph sx={{ maxWidth: 600, mx: 'auto' }}>
          Combat misinformation with our advanced AI technology. Get instant verification 
          of news, images, and social media content in multiple Indian languages.
        </Typography>
        <Box mt={4}>
          <Button 
            variant="contained" 
            size="large" 
            onClick={() => navigate('/verify')}
            sx={{ mr: 2 }}
          >
            Start Verifying
          </Button>
          <Button 
            variant="outlined" 
            size="large" 
            onClick={() => navigate('/education')}
          >
            Learn More
          </Button>
        </Box>
      </Box>

      {/* Features Section */}
      <Box py={6}>
        <Typography variant="h4" textAlign="center" gutterBottom>
          Key Features
        </Typography>
        <Grid container spacing={4} mt={2}>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%', textAlign: 'center' }}>
              <CardContent>
                <VerifyIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Real-time Verification
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Get instant verification results for text, images, and URLs with our advanced AI models.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%', textAlign: 'center' }}>
              <CardContent>
                <SchoolIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Digital Literacy
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Learn to identify misinformation through our interactive educational modules.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%', textAlign: 'center' }}>
              <CardContent>
                <SpeedIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Multi-platform Access
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Access through web, WhatsApp bot, and browser extension for seamless verification.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default HomePage;
