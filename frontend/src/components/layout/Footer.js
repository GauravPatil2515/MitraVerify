import React from 'react';
import { Box, Container, Typography, Link, Grid } from '@mui/material';

const Footer = () => {
  return (
    <Box 
      component="footer" 
      sx={{ 
        backgroundColor: 'primary.main', 
        color: 'white', 
        py: 3, 
        mt: 'auto' 
      }}
    >
      <Container maxWidth="lg">
        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Typography variant="h6" gutterBottom>
              MitraVerify
            </Typography>
            <Typography variant="body2">
              AI-powered misinformation detection platform for a more informed India.
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="h6" gutterBottom>
              Quick Links
            </Typography>
            <Link href="/about" color="inherit" underline="hover">
              About
            </Link>
            <br />
            <Link href="/privacy" color="inherit" underline="hover">
              Privacy Policy
            </Link>
            <br />
            <Link href="/terms" color="inherit" underline="hover">
              Terms of Service
            </Link>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="h6" gutterBottom>
              Contact
            </Typography>
            <Typography variant="body2">
              Email: support@mitraverify.com
            </Typography>
            <Typography variant="body2">
              Built for Google Cloud Hackathon 2024
            </Typography>
          </Grid>
        </Grid>
        <Box mt={3} textAlign="center">
          <Typography variant="body2">
            © 2024 MitraVerify. All rights reserved.
          </Typography>
        </Box>
      </Container>
    </Box>
  );
};

export default Footer;
