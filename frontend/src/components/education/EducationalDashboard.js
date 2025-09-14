import React from 'react';
import { Container, Typography, Box, Grid, Card, CardContent } from '@mui/material';

const EducationalDashboard = () => {
  return (
    <Container>
      <Box py={4}>
        <Typography variant="h4" gutterBottom>
          Digital Literacy Education
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Module 1: Identifying Fake News
                </Typography>
                <Typography variant="body2">
                  Learn to spot misinformation patterns and verify news sources.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Module 2: Social Media Verification
                </Typography>
                <Typography variant="body2">
                  Understand how to verify content on social media platforms.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default EducationalDashboard;
