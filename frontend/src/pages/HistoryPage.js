import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  Pagination,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  InputAdornment,
  Alert,
  CircularProgress,
  Avatar,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import {
  History,
  Search,
  FilterList,
  Visibility,
  Share,
  Download,
  CheckCircle,
  Warning,
  Error,
  Info,
  Article,
  Image as ImageIcon,
  Link as LinkIcon,
  DateRange,
  TrendingUp,
  Assessment,
  Cancel
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import apiService from '../services/api';
import { useQuery } from 'react-query';

const HistoryPage = () => {
  const { user } = useAuth();
  const [page, setPage] = useState(1);
  const [contentTypeFilter, setContentTypeFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedVerification, setSelectedVerification] = useState(null);
  const [detailsOpen, setDetailsOpen] = useState(false);

  // Fetch verification history
  const { data: historyData, isLoading, refetch } = useQuery(
    ['verificationHistory', page, contentTypeFilter],
    () => apiService.getHistory(page, contentTypeFilter === 'all' ? null : contentTypeFilter),
    {
      enabled: !!user,
      keepPreviousData: true,
    }
  );

  const handlePageChange = (event, newPage) => {
    setPage(newPage);
  };

  const handleFilterChange = (event) => {
    setContentTypeFilter(event.target.value);
    setPage(1);
  };

  const handleViewDetails = (verification) => {
    setSelectedVerification(verification);
    setDetailsOpen(true);
  };

  const getResultColor = (result) => {
    switch (result) {
      case 'verified':
      case 'likely_true':
        return 'success';
      case 'uncertain':
        return 'warning';
      case 'likely_false':
      case 'false':
        return 'error';
      default:
        return 'info';
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
      default: return 'Analyzed';
    }
  };

  const getContentTypeIcon = (contentType) => {
    switch (contentType) {
      case 'text': return <Article />;
      case 'image': return <ImageIcon />;
      case 'url': return <LinkIcon />;
      default: return <Info />;
    }
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

  const filteredHistory = historyData?.history?.filter(item =>
    searchQuery === '' || 
    item.original_content.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  const exportHistory = () => {
    const csvContent = [
      ['Date', 'Content Type', 'Content', 'Result', 'Confidence', 'Processing Time'],
      ...filteredHistory.map(item => [
        formatDate(item.timestamp),
        item.content_type,
        item.original_content.replace(/,/g, ';'),
        getResultText(item.result),
        `${Math.round((item.confidence_score || 0) * 100)}%`,
        `${item.processing_time || 0}s`
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'mitraverify-history.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const shareVerification = (verification) => {
    if (navigator.share) {
      navigator.share({
        title: 'MitraVerify Analysis Result',
        text: `Content analyzed: ${getResultText(verification.result)} with ${Math.round((verification.confidence_score || 0) * 100)}% confidence`,
        url: window.location.origin,
      });
    }
  };

  if (isLoading) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl">
      <Box py={4}>
        {/* Header */}
        <Box mb={4}>
          <Grid container alignItems="center" spacing={2}>
            <Grid item>
              <Avatar sx={{ bgcolor: 'primary.main', width: 64, height: 64 }}>
                <History fontSize="large" />
              </Avatar>
            </Grid>
            <Grid item xs>
              <Typography variant="h4" gutterBottom>
                Verification History
              </Typography>
              <Typography variant="body1" color="textSecondary">
                Track all your content verification activities and results
              </Typography>
            </Grid>
            <Grid item>
              <Button
                variant="outlined"
                startIcon={<Download />}
                onClick={exportHistory}
                disabled={filteredHistory.length === 0}
              >
                Export History
              </Button>
            </Grid>
          </Grid>
        </Box>

        {/* Stats Summary */}
        <Grid container spacing={3} mb={4}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <Assessment color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6">Total Verifications</Typography>
                </Box>
                <Typography variant="h3" color="primary">
                  {historyData?.pagination?.total_items || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <CheckCircle color="success" sx={{ mr: 1 }} />
                  <Typography variant="h6">Verified True</Typography>
                </Box>
                <Typography variant="h3" color="success.main">
                  {filteredHistory.filter(item => ['verified', 'likely_true'].includes(item.result)).length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <Warning color="warning" sx={{ mr: 1 }} />
                  <Typography variant="h6">Uncertain</Typography>
                </Box>
                <Typography variant="h3" color="warning.main">
                  {filteredHistory.filter(item => item.result === 'uncertain').length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <Error color="error" sx={{ mr: 1 }} />
                  <Typography variant="h6">False/Misleading</Typography>
                </Box>
                <Typography variant="h3" color="error.main">
                  {filteredHistory.filter(item => ['likely_false', 'false'].includes(item.result)).length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Filters */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Grid container spacing={3} alignItems="center">
              <Grid item xs={12} sm={6} md={4}>
                <TextField
                  fullWidth
                  placeholder="Search in content..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Search />
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Content Type</InputLabel>
                  <Select
                    value={contentTypeFilter}
                    onChange={handleFilterChange}
                    label="Content Type"
                  >
                    <MenuItem value="all">All Types</MenuItem>
                    <MenuItem value="text">Text</MenuItem>
                    <MenuItem value="image">Images</MenuItem>
                    <MenuItem value="url">URLs</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={12} md={5}>
                <Box display="flex" alignItems="center" gap={1}>
                  <FilterList />
                  <Typography variant="body2" color="textSecondary">
                    Showing {filteredHistory.length} of {historyData?.pagination?.total_items || 0} verifications
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* History Table */}
        {filteredHistory.length > 0 ? (
          <Card>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Date & Time</TableCell>
                    <TableCell>Content</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Result</TableCell>
                    <TableCell>Confidence</TableCell>
                    <TableCell>Processing Time</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredHistory.map((verification) => (
                    <TableRow key={verification.id} hover>
                      <TableCell>
                        <Typography variant="body2">
                          {formatDate(verification.timestamp)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" noWrap sx={{ maxWidth: 300 }}>
                          {verification.original_content}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          icon={getContentTypeIcon(verification.content_type)}
                          label={verification.content_type.toUpperCase()}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          icon={getResultIcon(verification.result)}
                          label={getResultText(verification.result)}
                          color={getResultColor(verification.result)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Box display="flex" alignItems="center">
                          <Typography variant="body2" sx={{ minWidth: 45 }}>
                            {Math.round((verification.confidence_score || 0) * 100)}%
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {(verification.processing_time || 0).toFixed(2)}s
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box display="flex" gap={1}>
                          <Tooltip title="View Details">
                            <IconButton
                              size="small"
                              onClick={() => handleViewDetails(verification)}
                            >
                              <Visibility />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Share">
                            <IconButton
                              size="small"
                              onClick={() => shareVerification(verification)}
                            >
                              <Share />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            
            {/* Pagination */}
            {historyData?.pagination && historyData.pagination.total_pages > 1 && (
              <Box display="flex" justifyContent="center" p={3}>
                <Pagination
                  count={historyData.pagination.total_pages}
                  page={page}
                  onChange={handlePageChange}
                  color="primary"
                />
              </Box>
            )}
          </Card>
        ) : (
          <Alert severity="info">
            <Typography variant="h6" gutterBottom>
              No verification history found
            </Typography>
            <Typography>
              {searchQuery ? 
                'No verifications match your search criteria. Try adjusting your filters.' :
                'You haven\'t verified any content yet. Start by using our verification tools!'
              }
            </Typography>
          </Alert>
        )}

        {/* Details Dialog */}
        <Dialog
          open={detailsOpen}
          onClose={() => setDetailsOpen(false)}
          maxWidth="md"
          fullWidth
        >
          {selectedVerification && (
            <>
              <DialogTitle>
                <Box display="flex" alignItems="center">
                  {getResultIcon(selectedVerification.result)}
                  <Typography variant="h6" sx={{ ml: 1 }}>
                    Verification Details
                  </Typography>
                </Box>
              </DialogTitle>
              <DialogContent>
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <Typography variant="h6" gutterBottom>
                      Original Content
                    </Typography>
                    <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                      <Typography variant="body2">
                        {selectedVerification.original_content}
                      </Typography>
                    </Paper>
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Typography variant="h6" gutterBottom>
                      Analysis Result
                    </Typography>
                    <Box display="flex" alignItems="center" mb={1}>
                      <Chip
                        icon={getResultIcon(selectedVerification.result)}
                        label={getResultText(selectedVerification.result)}
                        color={getResultColor(selectedVerification.result)}
                      />
                    </Box>
                    <Typography variant="body2" color="textSecondary">
                      Confidence: {Math.round((selectedVerification.confidence_score || 0) * 100)}%
                    </Typography>
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Typography variant="h6" gutterBottom>
                      Processing Details
                    </Typography>
                    <List dense>
                      <ListItem>
                        <ListItemText
                          primary="Content Type"
                          secondary={selectedVerification.content_type.toUpperCase()}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Processing Time"
                          secondary={`${(selectedVerification.processing_time || 0).toFixed(2)} seconds`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Analyzed On"
                          secondary={formatDate(selectedVerification.timestamp)}
                        />
                      </ListItem>
                    </List>
                  </Grid>

                  {selectedVerification.analysis_summary?.main_indicators && (
                    <Grid item xs={12}>
                      <Typography variant="h6" gutterBottom>
                        Key Indicators
                      </Typography>
                      <List>
                        {selectedVerification.analysis_summary.main_indicators.map((indicator, index) => (
                          <ListItem key={index}>
                            <ListItemText primary={indicator} />
                          </ListItem>
                        ))}
                      </List>
                    </Grid>
                  )}
                </Grid>
              </DialogContent>
              <DialogActions>
                <Button onClick={() => setDetailsOpen(false)}>Close</Button>
                <Button
                  variant="contained"
                  onClick={() => shareVerification(selectedVerification)}
                  startIcon={<Share />}
                >
                  Share
                </Button>
              </DialogActions>
            </>
          )}
        </Dialog>
      </Box>
    </Container>
  );
};

export default HistoryPage;
