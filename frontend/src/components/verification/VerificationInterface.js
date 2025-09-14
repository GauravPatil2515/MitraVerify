import React, { useState, useCallback, useRef } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Tabs,
  Tab,
  Card,
  CardContent,
  Chip,
  LinearProgress,
  Alert,
  Divider,
  IconButton,
  Tooltip,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Fab,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Search as SearchIcon,
  Image as ImageIcon,
  Link as LinkIcon,
  Upload as UploadIcon,
  Camera as CameraIcon,
  History as HistoryIcon,
  Share as ShareIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  ExpandMore as ExpandMoreIcon,
  ContentCopy as ContentCopyIcon,
  QrCode as QrCodeIcon,
  Mic as MicIcon,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { useMutation, useQuery } from 'react-query';
import { toast } from 'react-toastify';
import { motion, AnimatePresence } from 'framer-motion';
import { Helmet } from 'react-helmet-async';

import { useAuth } from '../../contexts/AuthContext';
import { useSettings } from '../../contexts/SettingsContext';
import LoadingSpinner from '../common/LoadingSpinner';
import ResultCard from './ResultCard';
import HistoryPanel from './HistoryPanel';
import ShareDialog from './ShareDialog';
import CameraCapture from './CameraCapture';
import apiService from '../../services/api';

// Tab panel component
function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`verification-tabpanel-${index}`}
      aria-labelledby={`verification-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

// Verification status icons
const StatusIcon = ({ status, size = 'medium' }) => {
  const iconProps = { fontSize: size };
  
  switch (status) {
    case 'verified':
      return <CheckCircleIcon {...iconProps} color="success" />;
    case 'questionable':
      return <WarningIcon {...iconProps} color="warning" />;
    case 'false':
      return <ErrorIcon {...iconProps} color="error" />;
    case 'insufficient_info':
      return <InfoIcon {...iconProps} color="info" />;
    default:
      return <InfoIcon {...iconProps} color="disabled" />;
  }
};

const VerificationInterface = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [textInput, setTextInput] = useState('');
  const [urlInput, setUrlInput] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [verificationResult, setVerificationResult] = useState(null);
  const [showHistory, setShowHistory] = useState(false);
  const [showShare, setShowShare] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  
  const fileInputRef = useRef(null);
  const { user } = useAuth();
  const { settings } = useSettings();

  // File upload configuration
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'],
      'text/*': ['.txt'],
      'application/pdf': ['.pdf'],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: false,
    onDrop: useCallback((acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0];
        setSelectedFile(file);
        setActiveTab(1); // Switch to image tab
        toast.success(`File "${file.name}" selected for verification`);
      }
    }, []),
    onDropRejected: (rejectedFiles) => {
      const rejection = rejectedFiles[0];
      if (rejection.file.size > 10 * 1024 * 1024) {
        toast.error('File size must be less than 10MB');
      } else {
        toast.error('File type not supported');
      }
    },
  });

  // Verification mutations
  const textVerificationMutation = useMutation(apiService.verifyContent, {
    onSuccess: (data) => {
      setVerificationResult(data);
      setIsAnalyzing(false);
      toast.success('Text verification completed');
    },
    onError: (error) => {
      setIsAnalyzing(false);
      toast.error(error.response?.data?.message || 'Text verification failed');
    },
  });

  const imageVerificationMutation = useMutation(apiService.verifyContent, {
    onSuccess: (data) => {
      setVerificationResult(data);
      setIsAnalyzing(false);
      toast.success('Image verification completed');
    },
    onError: (error) => {
      setIsAnalyzing(false);
      toast.error(error.response?.data?.message || 'Image verification failed');
    },
  });

  const urlVerificationMutation = useMutation(apiService.verifyContent, {
    onSuccess: (data) => {
      setVerificationResult(data);
      setIsAnalyzing(false);
      toast.success('URL verification completed');
    },
    onError: (error) => {
      setIsAnalyzing(false);
      toast.error(error.response?.data?.message || 'URL verification failed');
    },
  });

  // Get verification history
  const { data: verificationHistory, refetch: refetchHistory } = useQuery(
    ['verificationHistory', user?.id],
    () => apiService.getHistory(),
    {
      enabled: !!user,
      staleTime: 5 * 60 * 1000, // 5 minutes
    }
  );

  // Progress simulation for better UX
  const simulateProgress = () => {
    setAnalysisProgress(0);
    const interval = setInterval(() => {
      setAnalysisProgress((prev) => {
        if (prev >= 90) {
          clearInterval(interval);
          return 90; // Don't reach 100% until actual completion
        }
        return prev + Math.random() * 15;
      });
    }, 200);
    
    return () => clearInterval(interval);
  };

  // Handle text verification
  const handleTextVerification = async () => {
    if (!textInput.trim()) {
      toast.error('Please enter text to verify');
      return;
    }

    setIsAnalyzing(true);
    setVerificationResult(null);
    const cleanup = simulateProgress();

    try {
      await textVerificationMutation.mutateAsync({
        content: textInput.trim(),
        content_type: 'text',
      });
      setAnalysisProgress(100);
    } finally {
      cleanup();
    }
  };

  // Handle image verification
  const handleImageVerification = async () => {
    if (!selectedFile) {
      toast.error('Please select an image to verify');
      return;
    }

    setIsAnalyzing(true);
    setVerificationResult(null);
    const cleanup = simulateProgress();

    try {
      const formData = new FormData();
      formData.append('image', selectedFile);

      await imageVerificationMutation.mutateAsync(formData);
      setAnalysisProgress(100);
    } finally {
      cleanup();
    }
  };

  // Handle URL verification
  const handleUrlVerification = async () => {
    if (!urlInput.trim()) {
      toast.error('Please enter a URL to verify');
      return;
    }

    // Basic URL validation
    try {
      new URL(urlInput);
    } catch {
      toast.error('Please enter a valid URL');
      return;
    }

    setIsAnalyzing(true);
    setVerificationResult(null);
    const cleanup = simulateProgress();

    try {
      await urlVerificationMutation.mutateAsync({
        url: urlInput.trim(),
        content_type: 'url',
      });
      setAnalysisProgress(100);
    } finally {
      cleanup();
    }
  };

  // Handle camera capture
  const handleCameraCapture = (imageFile) => {
    setSelectedFile(imageFile);
    setShowCamera(false);
    setActiveTab(1); // Switch to image tab
    toast.success('Image captured successfully');
  };

  // Clear current verification
  const handleClearVerification = () => {
    setTextInput('');
    setUrlInput('');
    setSelectedFile(null);
    setVerificationResult(null);
    setIsAnalyzing(false);
    setAnalysisProgress(0);
  };

  // Tab change handler
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
    setVerificationResult(null); // Clear results when switching tabs
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'verified': return 'success';
      case 'questionable': return 'warning';
      case 'false': return 'error';
      case 'insufficient_info': return 'info';
      default: return 'default';
    }
  };

  return (
    <>
      <Helmet>
        <title>Verify Content - MitraVerify</title>
        <meta name="description" content="Verify news, images, and social media content instantly with AI-powered fact-checking technology." />
      </Helmet>

      <Container maxWidth="lg" sx={{ py: 4 }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* Header */}
          <Box sx={{ mb: 4, textAlign: 'center' }}>
            <Typography variant="h3" component="h1" gutterBottom>
              Content Verification
            </Typography>
            <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
              Verify the authenticity of text, images, and URLs using AI-powered analysis
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
              <Chip
                icon={<CheckCircleIcon />}
                label="AI-Powered Analysis"
                color="primary"
                variant="outlined"
              />
              <Chip
                icon={<SearchIcon />}
                label="Multi-Source Verification"
                color="primary"
                variant="outlined"
              />
              <Chip
                icon={<InfoIcon />}
                label="Detailed Insights"
                color="primary"
                variant="outlined"
              />
            </Box>
          </Box>

          <Grid container spacing={3}>
            {/* Main Verification Panel */}
            <Grid item xs={12} lg={8}>
              <Paper sx={{ p: 0, overflow: 'hidden' }}>
                {/* Tabs */}
                <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                  <Tabs value={activeTab} onChange={handleTabChange} variant="fullWidth">
                    <Tab icon={<SearchIcon />} label="Text" />
                    <Tab icon={<ImageIcon />} label="Image" />
                    <Tab icon={<LinkIcon />} label="URL" />
                  </Tabs>
                </Box>

                {/* Text Verification Tab */}
                <TabPanel value={activeTab} index={0}>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                    <TextField
                      fullWidth
                      multiline
                      rows={6}
                      placeholder="Paste text content here to verify its authenticity..."
                      value={textInput}
                      onChange={(e) => setTextInput(e.target.value)}
                      variant="outlined"
                      disabled={isAnalyzing}
                    />
                    
                    <Box sx={{ display: 'flex', gap: 2, justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body2" color="text.secondary">
                        {textInput.length}/10000 characters
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 2 }}>
                        <Button
                          variant="outlined"
                          onClick={() => setTextInput('')}
                          disabled={isAnalyzing || !textInput}
                        >
                          Clear
                        </Button>
                        <Button
                          variant="contained"
                          startIcon={<SearchIcon />}
                          onClick={handleTextVerification}
                          disabled={isAnalyzing || !textInput.trim()}
                          size="large"
                        >
                          Verify Text
                        </Button>
                      </Box>
                    </Box>
                  </Box>
                </TabPanel>

                {/* Image Verification Tab */}
                <TabPanel value={activeTab} index={1}>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                    {/* File Upload Area */}
                    <Box
                      {...getRootProps()}
                      sx={{
                        border: 2,
                        borderColor: isDragActive ? 'primary.main' : 'divider',
                        borderStyle: 'dashed',
                        borderRadius: 2,
                        p: 4,
                        textAlign: 'center',
                        cursor: 'pointer',
                        bgcolor: isDragActive ? 'action.hover' : 'transparent',
                        transition: 'all 0.2s ease',
                        '&:hover': {
                          borderColor: 'primary.main',
                          bgcolor: 'action.hover',
                        },
                      }}
                    >
                      <input {...getInputProps()} ref={fileInputRef} />
                      <UploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                      <Typography variant="h6" gutterBottom>
                        {isDragActive ? 'Drop the image here' : 'Drag & drop an image here'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        Supports PNG, JPG, JPEG, GIF, BMP, WebP (max 10MB)
                      </Typography>
                      <Button variant="outlined" disabled={isAnalyzing}>
                        Browse Files
                      </Button>
                    </Box>

                    {/* Alternative Upload Methods */}
                    <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
                      <Button
                        startIcon={<CameraIcon />}
                        onClick={() => setShowCamera(true)}
                        variant="outlined"
                        disabled={isAnalyzing}
                      >
                        Take Photo
                      </Button>
                      <Button
                        startIcon={<QrCodeIcon />}
                        variant="outlined"
                        disabled={isAnalyzing}
                      >
                        Scan QR Code
                      </Button>
                    </Box>

                    {/* Selected File Display */}
                    {selectedFile && (
                      <Card>
                        <CardContent>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <ImageIcon color="primary" />
                            <Box sx={{ flexGrow: 1 }}>
                              <Typography variant="subtitle1">{selectedFile.name}</Typography>
                              <Typography variant="body2" color="text.secondary">
                                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                              </Typography>
                            </Box>
                            <IconButton onClick={() => setSelectedFile(null)} disabled={isAnalyzing}>
                              <ErrorIcon />
                            </IconButton>
                          </Box>
                        </CardContent>
                      </Card>
                    )}

                    <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                      <Button
                        variant="outlined"
                        onClick={() => setSelectedFile(null)}
                        disabled={isAnalyzing || !selectedFile}
                      >
                        Clear
                      </Button>
                      <Button
                        variant="contained"
                        startIcon={<SearchIcon />}
                        onClick={handleImageVerification}
                        disabled={isAnalyzing || !selectedFile}
                        size="large"
                      >
                        Verify Image
                      </Button>
                    </Box>
                  </Box>
                </TabPanel>

                {/* URL Verification Tab */}
                <TabPanel value={activeTab} index={2}>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                    <TextField
                      fullWidth
                      placeholder="Enter URL to verify (e.g., https://example.com/news-article)"
                      value={urlInput}
                      onChange={(e) => setUrlInput(e.target.value)}
                      variant="outlined"
                      disabled={isAnalyzing}
                      InputProps={{
                        startAdornment: <LinkIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                      }}
                    />
                    
                    <Alert severity="info">
                      <Typography variant="body2">
                        URL verification checks the content, source credibility, and cross-references with fact-checking databases.
                      </Typography>
                    </Alert>

                    <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                      <Button
                        variant="outlined"
                        onClick={() => setUrlInput('')}
                        disabled={isAnalyzing || !urlInput}
                      >
                        Clear
                      </Button>
                      <Button
                        variant="contained"
                        startIcon={<SearchIcon />}
                        onClick={handleUrlVerification}
                        disabled={isAnalyzing || !urlInput.trim()}
                        size="large"
                      >
                        Verify URL
                      </Button>
                    </Box>
                  </Box>
                </TabPanel>

                {/* Analysis Progress */}
                <AnimatePresence>
                  {isAnalyzing && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                    >
                      <Box sx={{ p: 3, borderTop: 1, borderColor: 'divider' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                          <LoadingSpinner size={20} />
                          <Typography variant="h6">Analyzing Content...</Typography>
                        </Box>
                        <LinearProgress 
                          variant="determinate" 
                          value={analysisProgress} 
                          sx={{ mb: 1 }}
                        />
                        <Typography variant="body2" color="text.secondary">
                          {analysisProgress < 30 && 'Preprocessing content...'}
                          {analysisProgress >= 30 && analysisProgress < 60 && 'Running AI analysis...'}
                          {analysisProgress >= 60 && analysisProgress < 90 && 'Cross-referencing sources...'}
                          {analysisProgress >= 90 && 'Finalizing results...'}
                        </Typography>
                      </Box>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Verification Results */}
                {verificationResult && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                  >
                    <Box sx={{ p: 3, borderTop: 1, borderColor: 'divider' }}>
                      <ResultCard result={verificationResult} />
                    </Box>
                  </motion.div>
                )}
              </Paper>
            </Grid>

            {/* Sidebar */}
            <Grid item xs={12} lg={4}>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                {/* Quick Actions */}
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Quick Actions
                  </Typography>
                  <List>
                    <ListItem button onClick={() => setShowHistory(true)}>
                      <ListItemIcon>
                        <HistoryIcon />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Verification History" 
                        secondary={`${verificationHistory?.length || 0} items`}
                      />
                    </ListItem>
                    <ListItem button onClick={handleClearVerification}>
                      <ListItemIcon>
                        <RefreshIcon />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Clear All" 
                        secondary="Reset verification interface"
                      />
                    </ListItem>
                    {verificationResult && (
                      <ListItem button onClick={() => setShowShare(true)}>
                        <ListItemIcon>
                          <ShareIcon />
                        </ListItemIcon>
                        <ListItemText 
                          primary="Share Results" 
                          secondary="Share verification outcome"
                        />
                      </ListItem>
                    )}
                  </List>
                </Paper>

                {/* Tips and Guidelines */}
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Verification Tips
                  </Typography>
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="subtitle2">Text Verification</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="body2" color="text.secondary">
                        • Paste complete sentences or paragraphs for better analysis
                        • Include context and source information when possible
                        • Check for spelling and grammatical errors
                      </Typography>
                    </AccordionDetails>
                  </Accordion>
                  
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="subtitle2">Image Verification</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="body2" color="text.secondary">
                        • Use high-quality, unedited images
                        • Original photos work better than screenshots
                        • Include metadata when available
                      </Typography>
                    </AccordionDetails>
                  </Accordion>
                  
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="subtitle2">URL Verification</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="body2" color="text.secondary">
                        • Use complete URLs including https://
                        • Check the domain credibility
                        • Verify publication date and author
                      </Typography>
                    </AccordionDetails>
                  </Accordion>
                </Paper>

                {/* Recent Statistics */}
                {user && (
                  <Paper sx={{ p: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      Your Statistics
                    </Typography>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2">Total Verifications</Typography>
                        <Typography variant="h6" color="primary">
                          {verificationHistory?.length || 0}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2">This Week</Typography>
                        <Typography variant="h6" color="primary">
                          {/* Calculate this week's verifications */}
                          {verificationHistory?.filter(item => {
                            const itemDate = new Date(item.created_at);
                            const weekAgo = new Date();
                            weekAgo.setDate(weekAgo.getDate() - 7);
                            return itemDate >= weekAgo;
                          }).length || 0}
                        </Typography>
                      </Box>
                      <Divider />
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2">Accuracy Score</Typography>
                        <Typography variant="h6" color="success.main">
                          94%
                        </Typography>
                      </Box>
                    </Box>
                  </Paper>
                )}
              </Box>
            </Grid>
          </Grid>
        </motion.div>

        {/* Floating Action Button for Quick Verify */}
        <Fab
          color="primary"
          aria-label="quick verify"
          sx={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            zIndex: 1000,
          }}
          onClick={() => {
            // Quick paste and verify from clipboard
            navigator.clipboard.readText().then((text) => {
              if (text.trim()) {
                setTextInput(text);
                setActiveTab(0);
                handleTextVerification();
              }
            }).catch(() => {
              toast.error('Unable to access clipboard');
            });
          }}
        >
          <ContentCopyIcon />
        </Fab>

        {/* Dialogs */}
        <HistoryPanel
          open={showHistory}
          onClose={() => setShowHistory(false)}
          history={verificationHistory || []}
          onRefresh={refetchHistory}
        />

        <ShareDialog
          open={showShare}
          onClose={() => setShowShare(false)}
          result={verificationResult}
        />

        <CameraCapture
          open={showCamera}
          onClose={() => setShowCamera(false)}
          onCapture={handleCameraCapture}
        />
      </Container>
    </>
  );
};

export default VerificationInterface;
