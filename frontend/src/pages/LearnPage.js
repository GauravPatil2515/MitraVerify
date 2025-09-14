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
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  FormLabel,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Paper,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  TextField,
  Rating,
  Tabs,
  Tab
} from '@mui/material';
import {
  School,
  ExpandMore,
  CheckCircle,
  Cancel,
  PlayArrow,
  Quiz,
  Star,
  LightbulbOutlined,
  Security,
  Visibility,
  Psychology,
  Gavel,
  TrendingUp,
  Article,
  Image as ImageIcon,
  Link as LinkIcon,
  Warning,
  Info
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import apiService from '../services/api';
import { useQuery, useMutation, useQueryClient } from 'react-query';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`learn-tabpanel-${index}`}
      aria-labelledby={`learn-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

// Educational modules data
const educationalModules = [
  {
    id: 'basics',
    title: 'Understanding Misinformation',
    description: 'Learn the fundamentals of identifying false information',
    difficulty: 'Beginner',
    duration: '15 min',
    icon: <LightbulbOutlined />,
    color: 'primary',
    content: {
      introduction: 'Misinformation is false or inaccurate information that spreads regardless of intent to mislead.',
      keyPoints: [
        'Misinformation vs Disinformation: Intent matters',
        'Common types: False facts, misleading context, manipulated content',
        'Impact: Can influence decisions, elections, and public health',
        'Sources: Social media, messaging apps, fake news websites'
      ],
      examples: [
        {
          title: 'False Medical Claim',
          content: '"Drinking hot water cures COVID-19"',
          explanation: 'No scientific evidence supports this claim. WHO has debunked such remedies.'
        },
        {
          title: 'Misleading Statistics',
          content: '"Crime rate increased 200% in our city"',
          explanation: 'Without context (timeframe, source, comparison), statistics can be misleading.'
        }
      ]
    },
    quiz: [
      {
        question: 'What is the main difference between misinformation and disinformation?',
        options: [
          'Misinformation is always intentional',
          'Disinformation is spread with intent to deceive',
          'There is no difference',
          'Misinformation only happens online'
        ],
        correct: 1
      },
      {
        question: 'Which is NOT a common source of misinformation?',
        options: [
          'Social media posts',
          'WhatsApp forwards',
          'Peer-reviewed scientific journals',
          'Fake news websites'
        ],
        correct: 2
      }
    ]
  },
  {
    id: 'verification',
    title: 'Fact-Checking Techniques',
    description: 'Master the art of verifying information online',
    difficulty: 'Intermediate',
    duration: '20 min',
    icon: <Security />,
    color: 'success',
    content: {
      introduction: 'Learn systematic approaches to verify claims and sources.',
      keyPoints: [
        'Check the source: Who published this? Are they credible?',
        'Cross-reference: Multiple reliable sources saying the same thing?',
        'Check dates: Is this recent or being recirculated?',
        'Look for evidence: Photos, videos, documents - are they authentic?'
      ],
      examples: [
        {
          title: 'Source Verification',
          content: 'Always check if the website is known for reliable reporting',
          explanation: 'Look for About pages, contact information, and editorial standards.'
        },
        {
          title: 'Reverse Image Search',
          content: 'Use Google Images to find original source of photos',
          explanation: 'Old photos are often reused in false contexts.'
        }
      ]
    },
    quiz: [
      {
        question: 'What should you do first when verifying a news article?',
        options: [
          'Share it with friends',
          'Check the source and publication',
          'Read only the headline',
          'Assume it\'s true if it\'s popular'
        ],
        correct: 1
      },
      {
        question: 'Why is reverse image search useful?',
        options: [
          'To make images larger',
          'To find similar images',
          'To check if images are being reused from other contexts',
          'To download images'
        ],
        correct: 2
      }
    ]
  },
  {
    id: 'psychology',
    title: 'Psychology of Misinformation',
    description: 'Understand why people believe and share false information',
    difficulty: 'Intermediate',
    duration: '25 min',
    icon: <Psychology />,
    color: 'warning',
    content: {
      introduction: 'Understanding psychological factors helps in both recognizing and countering misinformation.',
      keyPoints: [
        'Confirmation bias: We tend to believe information that confirms our existing beliefs',
        'Emotional appeals: False news often triggers strong emotions like anger or fear',
        'Social proof: "Everyone believes it, so it must be true"',
        'Repetition effect: The more we hear something, the more likely we are to believe it'
      ],
      examples: [
        {
          title: 'Confirmation Bias Example',
          content: 'Political posts that only confirm your existing political views',
          explanation: 'We\'re more likely to share content that supports our beliefs without fact-checking.'
        },
        {
          title: 'Emotional Manipulation',
          content: '"SHOCKING: Government hiding this from you!"',
          explanation: 'Strong emotional words are designed to bypass critical thinking.'
        }
      ]
    },
    quiz: [
      {
        question: 'What is confirmation bias?',
        options: [
          'Confirming facts before sharing',
          'Believing information that supports our existing beliefs',
          'Getting confirmation from multiple sources',
          'Confirming the author of an article'
        ],
        correct: 1
      },
      {
        question: 'Why do false stories often use emotional language?',
        options: [
          'To make them more interesting',
          'To bypass critical thinking',
          'To make them easier to remember',
          'To attract more readers'
        ],
        correct: 1
      }
    ]
  },
  {
    id: 'legal',
    title: 'Legal and Ethical Aspects',
    description: 'Learn about the legal implications of sharing misinformation',
    difficulty: 'Advanced',
    duration: '18 min',
    icon: <Gavel />,
    color: 'error',
    content: {
      introduction: 'Understanding the legal and ethical responsibilities when sharing information.',
      keyPoints: [
        'Legal consequences: Defamation, inciting violence, election interference',
        'Platform policies: Social media terms of service',
        'Ethical responsibility: Think before you share',
        'Indian laws: IT Act 2000, IPC sections on spreading false information'
      ],
      examples: [
        {
          title: 'Section 66D of IT Act',
          content: 'Punishment for cheating by personation using computer resource',
          explanation: 'Creating fake profiles or impersonating others online is punishable.'
        },
        {
          title: 'Section 505 IPC',
          content: 'Statements conducing to public mischief',
          explanation: 'Spreading rumors that can cause fear or alarm is a criminal offense.'
        }
      ]
    },
    quiz: [
      {
        question: 'Which Indian law deals with cybercrimes including online misinformation?',
        options: [
          'Companies Act 2013',
          'Information Technology Act 2000',
          'Consumer Protection Act',
          'Right to Information Act'
        ],
        correct: 1
      },
      {
        question: 'What should you consider before sharing information online?',
        options: [
          'How many likes it will get',
          'Whether it\'s true and verified',
          'If it supports your views',
          'How controversial it is'
        ],
        correct: 1
      }
    ]
  },
  {
    id: 'tools',
    title: 'Digital Tools for Verification',
    description: 'Master digital tools and techniques for fact-checking',
    difficulty: 'Advanced',
    duration: '30 min',
    icon: <Visibility />,
    color: 'info',
    content: {
      introduction: 'Learn to use various digital tools for comprehensive fact-checking.',
      keyPoints: [
        'Google Reverse Image Search: Verify image authenticity',
        'TinEye: Advanced image verification',
        'Wayback Machine: Check historical versions of websites',
        'InVID WeVerify: Video verification toolkit',
        'Fact-checking websites: Snopes, PolitiFact, Alt News, Boom Live'
      ],
      examples: [
        {
          title: 'Using Google Reverse Image Search',
          content: 'Right-click image → Search Google for image',
          explanation: 'Helps identify original source and context of images.'
        },
        {
          title: 'Wayback Machine Usage',
          content: 'Enter website URL at web.archive.org',
          explanation: 'See how websites looked in the past and verify claims about changes.'
        }
      ]
    },
    quiz: [
      {
        question: 'What is the Wayback Machine used for?',
        options: [
          'Creating backups of your files',
          'Viewing historical versions of websites',
          'Machine learning algorithms',
          'Time travel simulation'
        ],
        correct: 1
      },
      {
        question: 'Which tool is specifically designed for video verification?',
        options: [
          'Google Images',
          'TinEye',
          'InVID WeVerify',
          'Snopes'
        ],
        correct: 2
      }
    ]
  },
  {
    id: 'trends',
    title: 'Current Misinformation Trends',
    description: 'Stay updated with latest misinformation patterns and trends',
    difficulty: 'Intermediate',
    duration: '22 min',
    icon: <TrendingUp />,
    color: 'secondary',
    content: {
      introduction: 'Understanding current trends helps in early detection of emerging misinformation.',
      keyPoints: [
        'Deepfakes: AI-generated fake videos and audio',
        'COVID-19 misinformation: False cures, conspiracy theories',
        'Election misinformation: Voter fraud claims, polling manipulation',
        'WhatsApp forwards: Chain messages with false health/safety tips'
      ],
      examples: [
        {
          title: 'Deepfake Detection',
          content: 'Look for unnatural facial movements, lip-sync issues',
          explanation: 'Technology is improving, but there are still telltale signs.'
        },
        {
          title: 'Health Misinformation',
          content: '"Gargling with salt water prevents COVID-19"',
          explanation: 'Always verify health claims with official health authorities.'
        }
      ]
    },
    quiz: [
      {
        question: 'What are deepfakes?',
        options: [
          'Deep ocean fish',
          'AI-generated fake videos',
          'Expensive fake jewelry',
          'Underground fake news networks'
        ],
        correct: 1
      },
      {
        question: 'How should you verify health-related claims?',
        options: [
          'Ask friends on social media',
          'Check with official health authorities like WHO, CDC',
          'Search for YouTube videos',
          'Trust the most shared post'
        ],
        correct: 1
      }
    ]
  }
];

const LearnPage = () => {
  const { user } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  const [selectedModule, setSelectedModule] = useState(null);
  const [moduleDialogOpen, setModuleDialogOpen] = useState(false);
  const [quizMode, setQuizMode] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [quizScore, setQuizScore] = useState(0);
  const [quizCompleted, setQuizCompleted] = useState(false);
  const [userAnswers, setUserAnswers] = useState([]);
  const [moduleProgress, setModuleProgress] = useState({});

  const queryClient = useQueryClient();

  // Track progress mutation
  const trackProgressMutation = useMutation(
    (progressData) => apiService.trackProgress(progressData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('userStats');
        queryClient.invalidateQueries('educationModules');
      },
    }
  );

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const openModule = (module) => {
    setSelectedModule(module);
    setModuleDialogOpen(true);
    setQuizMode(false);
    setCurrentQuestion(0);
    setQuizScore(0);
    setQuizCompleted(false);
    setUserAnswers([]);
  };

  const startQuiz = () => {
    setQuizMode(true);
    setCurrentQuestion(0);
    setSelectedAnswer('');
    setQuizScore(0);
    setQuizCompleted(false);
    setUserAnswers([]);
  };

  const handleAnswerSelect = (answerIndex) => {
    setSelectedAnswer(answerIndex);
  };

  const nextQuestion = () => {
    const isCorrect = selectedAnswer === selectedModule.quiz[currentQuestion].correct;
    const newAnswers = [...userAnswers, { 
      question: currentQuestion, 
      selected: selectedAnswer, 
      correct: isCorrect 
    }];
    setUserAnswers(newAnswers);

    if (isCorrect) {
      setQuizScore(quizScore + 1);
    }

    if (currentQuestion < selectedModule.quiz.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setSelectedAnswer('');
    } else {
      // Quiz completed
      setQuizCompleted(true);
      const finalScore = isCorrect ? quizScore + 1 : quizScore;
      const scorePercentage = (finalScore / selectedModule.quiz.length) * 100;
      
      // Track progress
      trackProgressMutation.mutate({
        module_id: selectedModule.id,
        module_name: selectedModule.title,
        score: scorePercentage,
        status: scorePercentage >= 70 ? 'completed' : 'in_progress',
        time_spent: 15 // Estimated time
      });

      // Update local progress
      setModuleProgress(prev => ({
        ...prev,
        [selectedModule.id]: {
          score: scorePercentage,
          status: scorePercentage >= 70 ? 'completed' : 'in_progress',
          completed_at: scorePercentage >= 70 ? new Date().toISOString() : null
        }
      }));
    }
  };

  const getModuleStatusColor = (moduleId) => {
    const progress = moduleProgress[moduleId];
    if (!progress) return 'default';
    if (progress.status === 'completed') return 'success';
    if (progress.status === 'in_progress') return 'warning';
    return 'default';
  };

  const getModuleStatusText = (moduleId) => {
    const progress = moduleProgress[moduleId];
    if (!progress) return 'Not Started';
    if (progress.status === 'completed') return `Completed (${Math.round(progress.score)}%)`;
    if (progress.status === 'in_progress') return `In Progress (${Math.round(progress.score)}%)`;
    return 'Not Started';
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'Beginner': return 'success';
      case 'Intermediate': return 'warning';
      case 'Advanced': return 'error';
      default: return 'default';
    }
  };

  return (
    <Container maxWidth="lg">
      <Box py={4}>
        {/* Header */}
        <Box mb={4} textAlign="center">
          <Typography variant="h3" gutterBottom>
            Digital Literacy Learning Center
          </Typography>
          <Typography variant="h6" color="textSecondary" gutterBottom>
            Master the skills to identify and combat misinformation
          </Typography>
          <Box display="flex" justifyContent="center" gap={2} mt={2}>
            <Chip icon={<School />} label="Interactive Modules" color="primary" />
            <Chip icon={<Quiz />} label="Practice Quizzes" color="secondary" />
            <Chip icon={<Star />} label="Track Progress" color="success" />
          </Box>
        </Box>

        {/* Learning Path Overview */}
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Your Learning Journey
            </Typography>
            <Box display="flex" alignItems="center" mb={2}>
              <Typography variant="body1" sx={{ mr: 2 }}>
                Overall Progress:
              </Typography>
              <LinearProgress
                variant="determinate"
                value={(Object.values(moduleProgress).filter(p => p.status === 'completed').length / educationalModules.length) * 100}
                sx={{ flexGrow: 1, mr: 2 }}
              />
              <Typography variant="body2">
                {Object.values(moduleProgress).filter(p => p.status === 'completed').length} / {educationalModules.length} completed
              </Typography>
            </Box>
            <Typography variant="body2" color="textSecondary">
              Complete all modules to become a certified fact-checker and improve your digital literacy score!
            </Typography>
          </CardContent>
        </Card>

        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="All Modules" />
            <Tab label="Beginner" />
            <Tab label="Intermediate" />
            <Tab label="Advanced" />
          </Tabs>
        </Box>

        {/* Module Cards */}
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            {educationalModules.map((module) => (
              <Grid item xs={12} md={6} lg={4} key={module.id}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box display="flex" alignItems="center" mb={2}>
                      <Box sx={{ color: `${module.color}.main`, mr: 1 }}>
                        {module.icon}
                      </Box>
                      <Typography variant="h6">
                        {module.title}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="textSecondary" mb={2}>
                      {module.description}
                    </Typography>
                    <Box display="flex" gap={1} mb={2}>
                      <Chip
                        label={module.difficulty}
                        color={getDifficultyColor(module.difficulty)}
                        size="small"
                      />
                      <Chip label={module.duration} variant="outlined" size="small" />
                    </Box>
                    <Box mb={2}>
                      <Chip
                        label={getModuleStatusText(module.id)}
                        color={getModuleStatusColor(module.id)}
                        size="small"
                      />
                    </Box>
                  </CardContent>
                  <CardActions>
                    <Button
                      variant="contained"
                      color={module.color}
                      fullWidth
                      startIcon={<PlayArrow />}
                      onClick={() => openModule(module)}
                    >
                      {moduleProgress[module.id]?.status === 'completed' ? 'Review' : 'Start Learning'}
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* Filtered Tabs */}
        {['Beginner', 'Intermediate', 'Advanced'].map((difficulty, index) => (
          <TabPanel value={tabValue} index={index + 1} key={difficulty}>
            <Grid container spacing={3}>
              {educationalModules
                .filter(module => module.difficulty === difficulty)
                .map((module) => (
                  <Grid item xs={12} md={6} lg={4} key={module.id}>
                    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                      <CardContent sx={{ flexGrow: 1 }}>
                        <Box display="flex" alignItems="center" mb={2}>
                          <Box sx={{ color: `${module.color}.main`, mr: 1 }}>
                            {module.icon}
                          </Box>
                          <Typography variant="h6">
                            {module.title}
                          </Typography>
                        </Box>
                        <Typography variant="body2" color="textSecondary" mb={2}>
                          {module.description}
                        </Typography>
                        <Box display="flex" gap={1} mb={2}>
                          <Chip label={module.duration} variant="outlined" size="small" />
                        </Box>
                        <Box mb={2}>
                          <Chip
                            label={getModuleStatusText(module.id)}
                            color={getModuleStatusColor(module.id)}
                            size="small"
                          />
                        </Box>
                      </CardContent>
                      <CardActions>
                        <Button
                          variant="contained"
                          color={module.color}
                          fullWidth
                          startIcon={<PlayArrow />}
                          onClick={() => openModule(module)}
                        >
                          {moduleProgress[module.id]?.status === 'completed' ? 'Review' : 'Start Learning'}
                        </Button>
                      </CardActions>
                    </Card>
                  </Grid>
                ))}
            </Grid>
          </TabPanel>
        ))}

        {/* Module Dialog */}
        <Dialog
          open={moduleDialogOpen}
          onClose={() => setModuleDialogOpen(false)}
          maxWidth="md"
          fullWidth
        >
          {selectedModule && (
            <>
              <DialogTitle>
                <Box display="flex" alignItems="center">
                  <Box sx={{ color: `${selectedModule.color}.main`, mr: 1 }}>
                    {selectedModule.icon}
                  </Box>
                  {selectedModule.title}
                </Box>
              </DialogTitle>
              <DialogContent>
                {!quizMode ? (
                  <Box>
                    {/* Learning Content */}
                    <Typography variant="h6" gutterBottom>
                      Introduction
                    </Typography>
                    <Typography variant="body1" mb={3}>
                      {selectedModule.content.introduction}
                    </Typography>

                    <Typography variant="h6" gutterBottom>
                      Key Points
                    </Typography>
                    <List>
                      {selectedModule.content.keyPoints.map((point, index) => (
                        <ListItem key={index}>
                          <ListItemIcon>
                            <CheckCircle color="success" />
                          </ListItemIcon>
                          <ListItemText primary={point} />
                        </ListItem>
                      ))}
                    </List>

                    <Typography variant="h6" gutterBottom>
                      Examples
                    </Typography>
                    {selectedModule.content.examples.map((example, index) => (
                      <Accordion key={index} sx={{ mb: 1 }}>
                        <AccordionSummary expandIcon={<ExpandMore />}>
                          <Typography variant="subtitle1">{example.title}</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Alert severity="info" sx={{ mb: 2 }}>
                            <Typography variant="body2" fontWeight="bold">
                              Example: {example.content}
                            </Typography>
                          </Alert>
                          <Typography variant="body2">
                            {example.explanation}
                          </Typography>
                        </AccordionDetails>
                      </Accordion>
                    ))}
                  </Box>
                ) : !quizCompleted ? (
                  <Box>
                    {/* Quiz Mode */}
                    <Box mb={3}>
                      <Typography variant="h6" gutterBottom>
                        Quiz: Question {currentQuestion + 1} of {selectedModule.quiz.length}
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={((currentQuestion + 1) / selectedModule.quiz.length) * 100}
                        sx={{ mb: 2 }}
                      />
                    </Box>

                    <Paper sx={{ p: 3, mb: 3 }}>
                      <Typography variant="h6" gutterBottom>
                        {selectedModule.quiz[currentQuestion].question}
                      </Typography>
                      <FormControl component="fieldset">
                        <RadioGroup
                          value={selectedAnswer}
                          onChange={(e) => handleAnswerSelect(parseInt(e.target.value))}
                        >
                          {selectedModule.quiz[currentQuestion].options.map((option, index) => (
                            <FormControlLabel
                              key={index}
                              value={index}
                              control={<Radio />}
                              label={option}
                            />
                          ))}
                        </RadioGroup>
                      </FormControl>
                    </Paper>
                  </Box>
                ) : (
                  <Box textAlign="center">
                    {/* Quiz Results */}
                    <Typography variant="h4" gutterBottom>
                      Quiz Completed!
                    </Typography>
                    <Box mb={3}>
                      <CircularProgress
                        variant="determinate"
                        value={(quizScore / selectedModule.quiz.length) * 100}
                        size={80}
                        sx={{ mb: 2 }}
                      />
                      <Typography variant="h5">
                        Score: {quizScore} / {selectedModule.quiz.length}
                      </Typography>
                      <Typography variant="h6" color="textSecondary">
                        {Math.round((quizScore / selectedModule.quiz.length) * 100)}%
                      </Typography>
                    </Box>
                    
                    {quizScore / selectedModule.quiz.length >= 0.7 ? (
                      <Alert severity="success" sx={{ mb: 2 }}>
                        <Typography variant="h6">Congratulations!</Typography>
                        <Typography>You've successfully completed this module!</Typography>
                      </Alert>
                    ) : (
                      <Alert severity="warning" sx={{ mb: 2 }}>
                        <Typography variant="h6">Good effort!</Typography>
                        <Typography>You might want to review the content and try again.</Typography>
                      </Alert>
                    )}

                    <Box textAlign="left">
                      <Typography variant="h6" gutterBottom>
                        Review Your Answers:
                      </Typography>
                      {userAnswers.map((answer, index) => (
                        <Box key={index} mb={2}>
                          <Typography variant="subtitle1" gutterBottom>
                            Q{index + 1}: {selectedModule.quiz[index].question}
                          </Typography>
                          <Box display="flex" alignItems="center">
                            {answer.correct ? (
                              <CheckCircle color="success" sx={{ mr: 1 }} />
                            ) : (
                              <Cancel color="error" sx={{ mr: 1 }} />
                            )}
                            <Typography>
                              Your answer: {selectedModule.quiz[index].options[answer.selected]}
                            </Typography>
                          </Box>
                          {!answer.correct && (
                            <Typography variant="body2" color="success.main">
                              Correct answer: {selectedModule.quiz[index].options[selectedModule.quiz[index].correct]}
                            </Typography>
                          )}
                        </Box>
                      ))}
                    </Box>
                  </Box>
                )}
              </DialogContent>
              <DialogActions>
                {!quizMode ? (
                  <>
                    <Button onClick={() => setModuleDialogOpen(false)}>
                      Close
                    </Button>
                    <Button
                      variant="contained"
                      onClick={startQuiz}
                      startIcon={<Quiz />}
                    >
                      Take Quiz
                    </Button>
                  </>
                ) : !quizCompleted ? (
                  <>
                    <Button onClick={() => setQuizMode(false)}>
                      Back to Content
                    </Button>
                    <Button
                      variant="contained"
                      onClick={nextQuestion}
                      disabled={selectedAnswer === ''}
                    >
                      {currentQuestion < selectedModule.quiz.length - 1 ? 'Next Question' : 'Finish Quiz'}
                    </Button>
                  </>
                ) : (
                  <>
                    <Button onClick={() => setModuleDialogOpen(false)}>
                      Close
                    </Button>
                    <Button
                      variant="outlined"
                      onClick={startQuiz}
                    >
                      Retake Quiz
                    </Button>
                  </>
                )}
              </DialogActions>
            </>
          )}
        </Dialog>
      </Box>
    </Container>
  );
};

export default LearnPage;
