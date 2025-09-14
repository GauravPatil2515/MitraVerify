import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  LinearProgress,
  Avatar,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip,
  Tab,
  Tabs,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material';
import {
  TrendingUp,
  VerifiedUser,
  Warning,
  School,
  History,
  Share,
  Refresh,
  CheckCircle,
  Cancel,
  HelpOutline,
  TrendingDown,
  Assessment,
  Security,
  Timeline,
  Article,
  Image as ImageIcon,
  Link as LinkIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import apiService from '../services/api';
import { useQuery } from 'react-query';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`dashboard-tabpanel-${index}`}
      aria-labelledby={`dashboard-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const DashboardPage = () => {
  const { user, userStats, statsLoading } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  
  // Fetch verification history
  const { data: historyData, isLoading: historyLoading, refetch: refetchHistory } = useQuery(
    'verificationHistory',
    () => apiService.getHistory(1, null),
    {
      enabled: !!user,
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  );

  // Fetch education modules progress
  const { data: educationData, isLoading: educationLoading } = useQuery(
    'educationModules',
    () => apiService.getEducationModules(),
    {
      enabled: !!user,
    }
  );

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const getCredibilityColor = (score) => {
    if (score > 0.7) return 'success';
    if (score > 0.4) return 'warning';
    return 'error';
  };

  const getCredibilityLabel = (score) => {
    if (score > 0.7) return 'Likely True';
    if (score > 0.4) return 'Uncertain';
    return 'Likely False';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (statsLoading || historyLoading || educationLoading) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  const stats = userStats || {
    total_verifications: 0,
    true_content: 0,
    false_content: 0,
    uncertain_content: 0,
    completed_modules: 0,
    recent_activity: 0,
    literacy_score: 0,
    accuracy_rate: 0,
    user_level: 'Beginner'
  };

  const recentVerifications = historyData?.history?.slice(0, 5) || [];
  const educationModules = educationData?.modules || [];
  const userProgress = educationData?.user_progress || {};

  return (
    <Container maxWidth="xl">
      <Box py={4}>
        {/* Header Section */}
        <Box mb={4}>
          <Grid container alignItems="center" spacing={2}>
            <Grid item>
              <Avatar sx={{ bgcolor: 'primary.main', width: 64, height: 64 }}>
                <VerifiedUser fontSize="large" />
              </Avatar>
            </Grid>
            <Grid item xs>
              <Typography variant="h4" gutterBottom>
                Welcome back, {user?.username}!
              </Typography>
              <Typography variant="body1" color="textSecondary">
                Your MitraVerify Dashboard - Fighting misinformation together
              </Typography>
            </Grid>
            <Grid item>
              <Chip
                icon={<Assessment />}
                label={`Literacy Score: ${stats.literacy_score}/100`}
                color={stats.literacy_score > 70 ? 'success' : stats.literacy_score > 40 ? 'warning' : 'error'}
                variant="outlined"
                size="large"
              />
            </Grid>
          </Grid>
        </Box>

        {/* Stats Cards */}
        <Grid container spacing={3} mb={4}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Assessment color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6">Total Verifications</Typography>
                </Box>
                <Typography variant="h3" color="primary">
                  {stats.total_verifications}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Content pieces analyzed
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <CheckCircle color="success" sx={{ mr: 1 }} />
                  <Typography variant="h6">Accuracy Rate</Typography>
                </Box>
                <Typography variant="h3" color="success.main">
                  {stats.accuracy_rate}%
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Verification accuracy
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <School color="info" sx={{ mr: 1 }} />
                  <Typography variant="h6">Learning Progress</Typography>
                </Box>
                <Typography variant="h3" color="info.main">
                  {stats.completed_modules}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Modules completed
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <TrendingUp color="warning" sx={{ mr: 1 }} />
                  <Typography variant="h6">User Level</Typography>
                </Box>
                <Typography variant="h3" color="warning.main">
                  {stats.user_level}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Digital literacy level
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Content Analysis Chart */}
        <Grid container spacing={3} mb={4}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Content Analysis Breakdown
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={4}>
                    <Box textAlign="center" p={2}>
                      <CheckCircle color="success" sx={{ fontSize: 48, mb: 1 }} />
                      <Typography variant="h4" color="success.main">
                        {stats.true_content}
                      </Typography>
                      <Typography variant="body2">Verified True</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Box textAlign="center" p={2}>
                      <HelpOutline color="warning" sx={{ fontSize: 48, mb: 1 }} />
                      <Typography variant="h4" color="warning.main">
                        {stats.uncertain_content}
                      </Typography>
                      <Typography variant="body2">Uncertain</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Box textAlign="center" p={2}>
                      <Cancel color="error" sx={{ fontSize: 48, mb: 1 }} />
                      <Typography variant="h4" color="error.main">
                        {stats.false_content}
                      </Typography>
                      <Typography variant="body2">False/Misleading</Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Activity
                </Typography>
                <Box display="flex" alignItems="center" mb={2}>
                  <Timeline color="primary" sx={{ mr: 1 }} />
                  <Typography variant="body1">
                    {stats.recent_activity} verifications in last 30 days
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={Math.min((stats.recent_activity / 50) * 100, 100)}
                  sx={{ mb: 2 }}
                />
                <Typography variant="body2" color="textSecondary">
                  Keep up the great work!
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Tabs Section */}
        <Card>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={handleTabChange}>
              <Tab label="Recent Verifications" icon={<History />} />
              <Tab label="Learning Progress" icon={<School />} />
              <Tab label="Quick Actions" icon={<Security />} />
            </Tabs>
          </Box>

          {/* Recent Verifications Tab */}
          <TabPanel value={tabValue} index={0}>
            {recentVerifications.length > 0 ? (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Content</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Result</TableCell>
                      <TableCell>Confidence</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {recentVerifications.map((verification) => (
                      <TableRow key={verification.id}>
                        <TableCell>
                          <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                            {verification.original_content}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            icon={
                              verification.content_type === 'text' ? <Article /> :
                              verification.content_type === 'image' ? <ImageIcon /> :
                              <LinkIcon />
                            }
                            label={verification.content_type}
                            size="small"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={getCredibilityLabel(verification.analysis_summary?.credibility_score || 0)}
                            color={getCredibilityColor(verification.analysis_summary?.credibility_score || 0)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {Math.round((verification.confidence_score || 0) * 100)}%
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {formatDate(verification.timestamp)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Tooltip title="Share verification">
                            <IconButton size="small">
                              <Share />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Alert severity="info">
                No verifications yet. Start by verifying some content to see your history here!
              </Alert>
            )}
            <Box mt={2}>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={() => refetchHistory()}
              >
                Refresh History
              </Button>
            </Box>
          </TabPanel>

          {/* Learning Progress Tab */}
          <TabPanel value={tabValue} index={1}>
            <Grid container spacing={3}>
              {educationModules.slice(0, 6).map((module, index) => {
                const progress = userProgress[module.id] || { status: 'not_started', score: 0 };
                return (
                  <Grid item xs={12} md={6} key={module.id}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          {module.title || `Module ${index + 1}: Digital Literacy`}
                        </Typography>
                        <Typography variant="body2" color="textSecondary" mb={2}>
                          {module.description || 'Learn to identify misinformation and verify content'}
                        </Typography>
                        <Box display="flex" alignItems="center" mb={2}>
                          <LinearProgress
                            variant="determinate"
                            value={progress.status === 'completed' ? 100 : progress.status === 'in_progress' ? 50 : 0}
                            sx={{ flexGrow: 1, mr: 2 }}
                          />
                          <Typography variant="body2">
                            {progress.status === 'completed' ? '100%' : progress.status === 'in_progress' ? '50%' : '0%'}
                          </Typography>
                        </Box>
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Chip
                            label={progress.status === 'completed' ? 'Completed' : progress.status === 'in_progress' ? 'In Progress' : 'Not Started'}
                            color={progress.status === 'completed' ? 'success' : progress.status === 'in_progress' ? 'warning' : 'default'}
                            size="small"
                          />
                          <Typography variant="body2">
                            Score: {Math.round(progress.score || 0)}/100
                          </Typography>
                        </Box>
                      </CardContent>
                      <CardActions>
                        <Button
                          size="small"
                          variant="contained"
                          onClick={() => window.location.href = '/learn'}
                        >
                          {progress.status === 'completed' ? 'Review' : progress.status === 'in_progress' ? 'Continue' : 'Start'}
                        </Button>
                      </CardActions>
                    </Card>
                  </Grid>
                );
              })}
            </Grid>
          </TabPanel>

          {/* Quick Actions Tab */}
          <TabPanel value={tabValue} index={2}>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={4}>
                <Card>
                  <CardContent>
                    <Box textAlign="center">
                      <Security color="primary" sx={{ fontSize: 48, mb: 2 }} />
                      <Typography variant="h6" gutterBottom>
                        Verify Text Content
                      </Typography>
                      <Typography variant="body2" color="textSecondary" mb={2}>
                        Analyze text messages, articles, and social media posts
                      </Typography>
                      <Button
                        variant="contained"
                        fullWidth
                        onClick={() => window.location.href = '/verify'}
                      >
                        Start Verification
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={4}>
                <Card>
                  <CardContent>
                    <Box textAlign="center">
                      <School color="success" sx={{ fontSize: 48, mb: 2 }} />
                      <Typography variant="h6" gutterBottom>
                        Learning Modules
                      </Typography>
                      <Typography variant="body2" color="textSecondary" mb={2}>
                        Improve your digital literacy and fact-checking skills
                      </Typography>
                      <Button
                        variant="contained"
                        color="success"
                        fullWidth
                        onClick={() => window.location.href = '/learn'}
                      >
                        Continue Learning
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={4}>
                <Card>
                  <CardContent>
                    <Box textAlign="center">
                      <History color="info" sx={{ fontSize: 48, mb: 2 }} />
                      <Typography variant="h6" gutterBottom>
                        View Full History
                      </Typography>
                      <Typography variant="body2" color="textSecondary" mb={2}>
                        See all your past verifications and analysis
                      </Typography>
                      <Button
                        variant="contained"
                        color="info"
                        fullWidth
                        onClick={() => window.location.href = '/history'}
                      >
                        View History
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>
        </Card>
      </Box>
    </Container>
  );
};

export default DashboardPage;
