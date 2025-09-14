import React, { useState, useRef } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Grid,
  Paper,
  Chip,
  Alert,
  CircularProgress,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Avatar,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Rating,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab
} from '@mui/material';
import {
  Security,
  Send,
  CheckCircle,
  Warning,
  Error,
  Info,
  ExpandMore,
  Share,
  BookmarkAdd,
  Feedback,
  Photo as ImageIcon,
  Link as LinkIcon,
  Article,
  ContentCopy,
  CloudUpload,
  Analytics as Analysis,
  Psychology,
  Gavel,
  Source,
  Timeline,
  TrendingUp,
  School
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import apiService from '../services/api';
import { useMutation } from 'react-query';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`verify-tabpanel-${index}`}
      aria-labelledby={`verify-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 0 }}>{children}</Box>}
    </div>
  );
}

const VerifyPage = () => {
  const { user } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  const [textContent, setTextContent] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [urlContent, setUrlContent] = useState('');
  const [verifying, setVerifying] = useState(false);
  const [verificationResult, setVerificationResult] = useState(null);
  const [language, setLanguage] = useState('auto');
  const [feedbackOpen, setFeedbackOpen] = useState(false);
  const [userRating, setUserRating] = useState(0);
  const [userComment, setUserComment] = useState('');
  const fileInputRef = useRef(null);

  const verifyMutation = useMutation(
    (data) => apiService.verifyContent(data),
    {
      onSuccess: (result) => {
        setVerificationResult(result);
        setVerifying(false);
      },
      onError: (error) => {
        console.error('Verification failed:', error);
        setVerifying(false);
        setVerificationResult({
          error: 'Verification failed. Please try again.',
          result: 'error'
        });
      },
    }
  );

  const analyzeImageMutation = useMutation(
    (imageFile) => apiService.analyzeImage(imageFile),
    {
      onSuccess: (result) => {
        setVerificationResult(result);
        setVerifying(false);
      },
      onError: (error) => {
        console.error('Image analysis failed:', error);
        setVerifying(false);
        setVerificationResult({
          error: 'Image analysis failed. Please try again.',
          result: 'error'
        });
      },
    }
  );

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    setVerificationResult(null);
    setTextContent('');
    setSelectedFile(null);
    setUrlContent('');
  };

  const handleTextVerification = () => {
    if (!textContent.trim()) return;
    
    setVerifying(true);
    setVerificationResult(null);
    
    verifyMutation.mutate({
      content: textContent,
      content_type: 'text',
      language: language === 'auto' ? 'auto-detect' : language
    });
  };

  const handleImageVerification = () => {
    if (!selectedFile) return;
    
    setVerifying(true);
    setVerificationResult(null);
    
    analyzeImageMutation.mutate(selectedFile);
  };

  const handleUrlVerification = () => {
    if (!urlContent.trim()) return;
    
    setVerifying(true);
    setVerificationResult(null);
    
    verifyMutation.mutate({
      content: urlContent,
      content_type: 'url',
      language: language === 'auto' ? 'auto-detect' : language
    });
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const getResultColor = (result) => {
    switch (result) {
      case 'verified': return 'success';
      case 'likely_true': return 'success';
      case 'uncertain': return 'warning';
      case 'likely_false': return 'error';
      case 'false': return 'error';
      case 'error': return 'error';
      default: return 'info';
    }
  };

  const getResultIcon = (result) => {
    switch (result) {
      case 'verified':
      case 'likely_true':
        return <CheckCircle />;
      case 'uncertain':
        return <Warning />;
      case 'likely_false':
      case 'false':
        return <Error />;
      default:
        return <Info />;
    }
  };

  const getResultText = (result) => {
    switch (result) {
      case 'verified': return 'Verified True';
      case 'likely_true': return 'Likely True';
      case 'uncertain': return 'Uncertain';
      case 'likely_false': return 'Likely False';
      case 'false': return 'False/Misleading';
      default: return 'Analysis Complete';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    // You could add a toast notification here
  };

  const handleShare = () => {
    if (navigator.share && verificationResult) {
      navigator.share({
        title: 'MitraVerify Analysis Result',
        text: `Content verified with ${Math.round((verificationResult.confidence_score || 0) * 100)}% confidence`,
        url: window.location.href,
      });
    }
  };

  const submitFeedback = () => {
    // In a real app, you'd submit this to your API
    console.log('Feedback submitted:', { rating: userRating, comment: userComment });
    setFeedbackOpen(false);
    setUserRating(0);
    setUserComment('');
  };

  const sampleTexts = [
    "Breaking: Government announces new policy that will shock everyone!",
    "Scientists discover miracle cure that doctors don't want you to know about",
    "The Reserve Bank of India announced new monetary policy measures to control inflation",
    "WhatsApp will start charging users from next month - Share to save your account"
  ];

  return (
    <Container maxWidth="lg">
      <Box py={4}>
        {/* Header */}
        <Box mb={4} textAlign="center">
          <Typography variant="h3" gutterBottom>
            Content Verification Center
          </Typography>
          <Typography variant="h6" color="textSecondary" gutterBottom>
            Analyze text, images, and URLs for misinformation using AI-powered tools
          </Typography>
          <Box display="flex" justifyContent="center" gap={2} mt={2}>
            <Chip icon={<Security />} label="AI-Powered Analysis" color="primary" />
            <Chip icon={<Analysis />} label="Real-time Results" color="secondary" />
            <Chip icon={<School />} label="Educational Insights" color="success" />
          </Box>
        </Box>

        {/* Verification Tabs */}
        <Card sx={{ mb: 4 }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={handleTabChange} centered>
              <Tab icon={<Article />} label="Text Content" />
              <Tab icon={<ImageIcon />} label="Images" />
              <Tab icon={<LinkIcon />} label="URLs & Links" />
            </Tabs>
          </Box>

          {/* Text Verification Tab */}
          <TabPanel value={tabValue} index={0}>
            <CardContent>
              <Grid container spacing={3}>
                <Grid item xs={12} md={8}>
                  <TextField
                    fullWidth
                    multiline
                    rows={8}
                    label="Enter text content to verify"
                    placeholder="Paste the text message, article, or social media post you want to verify..."
                    value={textContent}
                    onChange={(e) => setTextContent(e.target.value)}
                    variant="outlined"
                    sx={{ mb: 2 }}
                  />
                  
                  <Box display="flex" gap={2} alignItems="center" mb={2}>
                    <FormControl sx={{ minWidth: 120 }}>
                      <InputLabel>Language</InputLabel>
                      <Select
                        value={language}
                        onChange={(e) => setLanguage(e.target.value)}
                        label="Language"
                      >
                        <MenuItem value="auto">Auto-detect</MenuItem>
                        <MenuItem value="en">English</MenuItem>
                        <MenuItem value="hi">Hindi</MenuItem>
                        <MenuItem value="bn">Bengali</MenuItem>
                        <MenuItem value="ta">Tamil</MenuItem>
                        <MenuItem value="te">Telugu</MenuItem>
                      </Select>
                    </FormControl>
                    
                    <Button
                      variant="contained"
                      size="large"
                      startIcon={<Security />}
                      onClick={handleTextVerification}
                      disabled={!textContent.trim() || verifying}
                      sx={{ ml: 'auto' }}
                    >
                      {verifying ? 'Analyzing...' : 'Verify Content'}
                    </Button>
                  </Box>

                  {verifying && (
                    <Box mb={2}>
                      <LinearProgress />
                      <Typography variant="body2" textAlign="center" mt={1}>
                        Analyzing content using AI models...
                      </Typography>
                    </Box>
                  )}
                </Grid>

                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                    <Typography variant="h6" gutterBottom>
                      Try Sample Texts
                    </Typography>
                    <Typography variant="body2" color="textSecondary" mb={2}>
                      Click on any sample to test our verification system:
                    </Typography>
                    {sampleTexts.map((sample, index) => (
                      <Button
                        key={index}
                        variant="outlined"
                        fullWidth
                        sx={{ mb: 1, textAlign: 'left', justifyContent: 'flex-start' }}
                        onClick={() => setTextContent(sample)}
                      >
                        <Typography variant="body2" noWrap>
                          {sample.substring(0, 50)}...
                        </Typography>
                      </Button>
                    ))}
                  </Paper>
                </Grid>
              </Grid>
            </CardContent>
          </TabPanel>

          {/* Image Verification Tab */}
          <TabPanel value={tabValue} index={1}>
            <CardContent>
              <Grid container spacing={3}>
                <Grid item xs={12} md={8}>
                  <Paper
                    sx={{
                      p: 4,
                      textAlign: 'center',
                      border: '2px dashed',
                      borderColor: 'grey.300',
                      cursor: 'pointer',
                      '&:hover': { borderColor: 'primary.main' }
                    }}
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <CloudUpload sx={{ fontSize: 48, color: 'grey.500', mb: 2 }} />
                    <Typography variant="h6" gutterBottom>
                      Upload Image for Analysis
                    </Typography>
                    <Typography variant="body2" color="textSecondary" mb={2}>
                      Drag and drop an image here, or click to select a file
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Supported formats: JPG, PNG, GIF, WebP (Max 10MB)
                    </Typography>
                    
                    <input
                      type="file"
                      ref={fileInputRef}
                      style={{ display: 'none' }}
                      accept="image/*"
                      onChange={handleFileSelect}
                    />
                  </Paper>

                  {selectedFile && (
                    <Box mt={2}>
                      <Alert severity="info" sx={{ mb: 2 }}>
                        <Typography variant="body2">
                          Selected: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                        </Typography>
                      </Alert>
                      
                      <Button
                        variant="contained"
                        size="large"
                        startIcon={<Analysis />}
                        onClick={handleImageVerification}
                        disabled={verifying}
                        fullWidth
                      >
                        {verifying ? 'Analyzing Image...' : 'Analyze Image'}
                      </Button>
                    </Box>
                  )}

                  {verifying && (
                    <Box mt={2}>
                      <LinearProgress />
                      <Typography variant="body2" textAlign="center" mt={1}>
                        Analyzing image for manipulation, extracting text, checking metadata...
                      </Typography>
                    </Box>
                  )}
                </Grid>

                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                    <Typography variant="h6" gutterBottom>
                      Image Analysis Features
                    </Typography>
                    <List dense>
                      <ListItem>
                        <ListItemIcon>
                          <Security color="primary" />
                        </ListItemIcon>
                        <ListItemText 
                          primary="Manipulation Detection"
                          secondary="Identify edited or doctored images"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon>
                          <Article color="primary" />
                        </ListItemIcon>
                        <ListItemText 
                          primary="Text Extraction"
                          secondary="Extract and verify text within images"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon>
                          <Source color="primary" />
                        </ListItemIcon>
                        <ListItemText 
                          primary="Reverse Search"
                          secondary="Find original sources and contexts"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon>
                          <Info color="primary" />
                        </ListItemIcon>
                        <ListItemText 
                          primary="Metadata Analysis"
                          secondary="Check creation date, location, device"
                        />
                      </ListItem>
                    </List>
                  </Paper>
                </Grid>
              </Grid>
            </CardContent>
          </TabPanel>

          {/* URL Verification Tab */}
          <TabPanel value={tabValue} index={2}>
            <CardContent>
              <Grid container spacing={3}>
                <Grid item xs={12} md={8}>
                  <TextField
                    fullWidth
                    label="Enter URL to verify"
                    placeholder="https://example.com/article-to-verify"
                    value={urlContent}
                    onChange={(e) => setUrlContent(e.target.value)}
                    variant="outlined"
                    sx={{ mb: 2 }}
                  />
                  
                  <Button
                    variant="contained"
                    size="large"
                    startIcon={<Security />}
                    onClick={handleUrlVerification}
                    disabled={!urlContent.trim() || verifying}
                    fullWidth
                  >
                    {verifying ? 'Analyzing URL...' : 'Verify URL'}
                  </Button>

                  {verifying && (
                    <Box mt={2}>
                      <LinearProgress />
                      <Typography variant="body2" textAlign="center" mt={1}>
                        Fetching content, analyzing domain reputation, checking sources...
                      </Typography>
                    </Box>
                  )}
                </Grid>

                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                    <Typography variant="h6" gutterBottom>
                      URL Analysis Features
                    </Typography>
                    <List dense>
                      <ListItem>
                        <ListItemIcon>
                          <Source color="primary" />
                        </ListItemIcon>
                        <ListItemText 
                          primary="Domain Reputation"
                          secondary="Check credibility of the website"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon>
                          <Article color="primary" />
                        </ListItemIcon>
                        <ListItemText 
                          primary="Content Analysis"
                          secondary="Analyze the article or page content"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon>
                          <Timeline color="primary" />
                        </ListItemIcon>
                        <ListItemText 
                          primary="Source Tracking"
                          secondary="Trace original sources and references"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon>
                          <Security color="primary" />
                        </ListItemIcon>
                        <ListItemText 
                          primary="Safety Check"
                          secondary="Identify malicious or phishing sites"
                        />
                      </ListItem>
                    </List>
                  </Paper>
                </Grid>
              </Grid>
            </CardContent>
          </TabPanel>
        </Card>

        {/* Verification Results */}
        {verificationResult && !verificationResult.error && (
          <Card sx={{ mb: 4 }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={3}>
                <Avatar
                  sx={{
                    bgcolor: `${getResultColor(verificationResult.result)}.main`,
                    mr: 2,
                    width: 56,
                    height: 56
                  }}
                >
                  {getResultIcon(verificationResult.result)}
                </Avatar>
                <Box>
                  <Typography variant="h4" gutterBottom>
                    {getResultText(verificationResult.result)}
                  </Typography>
                  <Box display="flex" alignItems="center" gap={2}>
                    <Typography variant="h6" color="textSecondary">
                      Confidence: {Math.round((verificationResult.confidence_score || 0) * 100)}%
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={(verificationResult.confidence_score || 0) * 100}
                      color={getConfidenceColor(verificationResult.confidence_score || 0)}
                      sx={{ width: 200, height: 8, borderRadius: 4 }}
                    />
                  </Box>
                </Box>
                <Box ml="auto" display="flex" gap={1}>
                  <Tooltip title="Copy Results">
                    <IconButton onClick={() => copyToClipboard(JSON.stringify(verificationResult, null, 2))}>
                      <ContentCopy />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Share">
                    <IconButton onClick={handleShare}>
                      <Share />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Provide Feedback">
                    <IconButton onClick={() => setFeedbackOpen(true)}>
                      <Feedback />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>

              {/* Detailed Analysis */}
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Accordion defaultExpanded>
                    <AccordionSummary expandIcon={<ExpandMore />}>
                      <Typography variant="h6">Detailed Analysis</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <List>
                        {verificationResult.analysis_details?.main_indicators?.map((indicator, index) => (
                          <ListItem key={index}>
                            <ListItemIcon>
                              <Info color="primary" />
                            </ListItemIcon>
                            <ListItemText primary={indicator} />
                          </ListItem>
                        )) || (
                          <ListItem>
                            <ListItemText primary="Analysis completed successfully" />
                          </ListItem>
                        )}
                      </List>
                    </AccordionDetails>
                  </Accordion>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMore />}>
                      <Typography variant="h6">Educational Insights</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Alert severity="info" sx={{ mb: 2 }}>
                        <Typography variant="body2">
                          {verificationResult.educational_tip || 
                           "Always verify information from multiple credible sources before sharing."}
                        </Typography>
                      </Alert>
                      <Typography variant="body2" color="textSecondary">
                        This analysis can help you develop better fact-checking skills. 
                        Consider taking our learning modules to improve your digital literacy.
                      </Typography>
                    </AccordionDetails>
                  </Accordion>
                </Grid>

                {verificationResult.extracted_text && (
                  <Grid item xs={12}>
                    <Accordion>
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Typography variant="h6">Extracted Text</Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                          <Typography variant="body2">
                            {verificationResult.extracted_text}
                          </Typography>
                        </Paper>
                      </AccordionDetails>
                    </Accordion>
                  </Grid>
                )}

                {verificationResult.sources && verificationResult.sources.length > 0 && (
                  <Grid item xs={12}>
                    <Accordion>
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Typography variant="h6">Related Sources</Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <List>
                          {verificationResult.sources.map((source, index) => (
                            <ListItem key={index}>
                              <ListItemIcon>
                                <Source />
                              </ListItemIcon>
                              <ListItemText 
                                primary={source.title || source.url}
                                secondary={source.description || source.url}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </AccordionDetails>
                    </Accordion>
                  </Grid>
                )}
              </Grid>

              {/* Processing Time */}
              <Box mt={3} textAlign="center">
                <Typography variant="caption" color="textSecondary">
                  Analysis completed in {verificationResult.processing_time || 0.5} seconds • 
                  Verification ID: {verificationResult.verification_id || 'N/A'}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        )}

        {/* Error Display */}
        {verificationResult?.error && (
          <Alert severity="error" sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              Verification Failed
            </Typography>
            <Typography>
              {verificationResult.error}
            </Typography>
          </Alert>
        )}

        {/* Tips Section */}
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Verification Tips
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Box textAlign="center">
                  <Psychology color="primary" sx={{ fontSize: 48, mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Think Critically
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Question emotional appeals and sensational claims. 
                    Ask yourself: "Does this seem too good/bad to be true?"
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box textAlign="center">
                  <Source color="success" sx={{ fontSize: 48, mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Check Sources
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Verify the credibility of sources. Look for author information, 
                    publication date, and references to original research.
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box textAlign="center">
                  <TrendingUp color="warning" sx={{ fontSize: 48, mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Cross-Reference
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Check multiple reliable sources. If only one source reports it, 
                    be skeptical until confirmed elsewhere.
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Feedback Dialog */}
        <Dialog open={feedbackOpen} onClose={() => setFeedbackOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Provide Feedback</DialogTitle>
          <DialogContent>
            <Typography variant="body1" gutterBottom>
              How accurate do you think this analysis was?
            </Typography>
            <Box display="flex" alignItems="center" mb={3}>
              <Typography variant="body2" sx={{ mr: 2 }}>
                Rating:
              </Typography>
              <Rating
                value={userRating}
                onChange={(event, newValue) => setUserRating(newValue)}
              />
            </Box>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Additional Comments (optional)"
              value={userComment}
              onChange={(e) => setUserComment(e.target.value)}
              placeholder="Tell us how we can improve our analysis..."
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setFeedbackOpen(false)}>Cancel</Button>
            <Button onClick={submitFeedback} variant="contained">
              Submit Feedback
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
};

export default VerifyPage;
