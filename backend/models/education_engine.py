"""
MitraVerify Education Engine
Personalized digital literacy and misinformation awareness education system

This module provides comprehensive educational content, progress tracking,
and personalized learning paths for users to improve their digital literacy skills.
"""

import logging
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class EducationEngine:
    """
    Educational engine that provides personalized learning content,
    tracks user progress, and manages achievement systems.
    """
    
    def __init__(self):
        """Initialize the education engine with learning modules and content."""
        self.learning_modules = self._load_learning_modules()
        self.achievements = self._load_achievements()
        self.quiz_questions = self._load_quiz_questions()
        self.tips_and_tricks = self._load_tips_and_tricks()
        self.case_studies = self._load_case_studies()
        
        # User progress tracking
        self.user_progress = {}
        self.user_preferences = {}
        
        logger.info("EducationEngine initialized successfully")
    
    def _load_learning_modules(self) -> Dict[str, Dict]:
        """Load structured learning modules for different skill levels."""
        return {
            'beginner_basics': {
                'id': 'beginner_basics',
                'title': 'Digital Literacy Basics',
                'description': 'Fundamental concepts of digital literacy and information verification',
                'level': 'beginner',
                'estimated_time': 30,  # minutes
                'prerequisites': [],
                'topics': [
                    'What is misinformation?',
                    'Common types of false information',
                    'Why misinformation spreads',
                    'Basic verification techniques',
                    'Reliable vs unreliable sources'
                ],
                'content': {
                    'introduction': """
                    Digital literacy is the ability to find, evaluate, and create information using digital technologies.
                    In today's world, it's crucial to distinguish between reliable and unreliable information.
                    """,
                    'key_concepts': [
                        {
                            'concept': 'Misinformation',
                            'definition': 'False or inaccurate information, regardless of intent to deceive',
                            'examples': ['Outdated health advice', 'Misinterpreted statistics', 'Honest mistakes in reporting']
                        },
                        {
                            'concept': 'Disinformation',
                            'definition': 'Deliberately false information created to deceive',
                            'examples': ['Fabricated news stories', 'Manipulated images', 'False political claims']
                        },
                        {
                            'concept': 'Malinformation',
                            'definition': 'True information used maliciously to harm individuals or groups',
                            'examples': ['Leaked private information', 'True but out-of-context quotes', 'Doxxing']
                        }
                    ],
                    'practical_tips': [
                        'Check the source and publication date',
                        'Look for author credentials and contact information',
                        'Cross-reference with multiple reliable sources',
                        'Be skeptical of emotional or sensational headlines',
                        'Check if the URL looks suspicious'
                    ]
                }
            },
            
            'source_evaluation': {
                'id': 'source_evaluation',
                'title': 'Evaluating Information Sources',
                'description': 'Learn to assess the credibility and reliability of different information sources',
                'level': 'beginner',
                'estimated_time': 45,
                'prerequisites': ['beginner_basics'],
                'topics': [
                    'Identifying credible sources',
                    'Understanding bias in media',
                    'Government and institutional sources',
                    'Academic and peer-reviewed sources',
                    'Social media source evaluation'
                ],
                'content': {
                    'source_hierarchy': [
                        {
                            'tier': 'Tier 1 - Highest Credibility',
                            'sources': ['Government agencies', 'Peer-reviewed journals', 'Established news organizations'],
                            'characteristics': ['Professional editorial standards', 'Transparent correction policies', 'Expert contributors']
                        },
                        {
                            'tier': 'Tier 2 - Good Credibility',
                            'sources': ['Reputable magazines', 'Professional associations', 'Expert blogs'],
                            'characteristics': ['Clear authorship', 'Regular publication', 'Industry recognition']
                        },
                        {
                            'tier': 'Tier 3 - Variable Credibility',
                            'sources': ['Personal blogs', 'Social media posts', 'Opinion pieces'],
                            'characteristics': ['Individual perspectives', 'May lack editorial oversight', 'Requires extra verification']
                        }
                    ],
                    'red_flags': [
                        'No author information provided',
                        'Excessive emotional language',
                        'Claims that seem too good to be true',
                        'No sources or references cited',
                        'Suspicious website design or URL'
                    ]
                }
            },
            
            'social_media_literacy': {
                'id': 'social_media_literacy',
                'title': 'Social Media Information Literacy',
                'description': 'Navigate social media platforms safely and identify misinformation',
                'level': 'intermediate',
                'estimated_time': 60,
                'prerequisites': ['beginner_basics', 'source_evaluation'],
                'topics': [
                    'How algorithms shape what you see',
                    'Echo chambers and filter bubbles',
                    'Viral misinformation patterns',
                    'Fact-checking on social platforms',
                    'Responsible sharing practices'
                ],
                'content': {
                    'algorithm_awareness': """
                    Social media algorithms are designed to show you content that keeps you engaged.
                    This can create 'filter bubbles' where you only see information that confirms your existing beliefs.
                    """,
                    'viral_patterns': [
                        'Emotional manipulation to encourage sharing',
                        'Vague or misleading headlines',
                        'Lack of specific details or sources',
                        'Appeals to share "before it\'s deleted"',
                        'Claims of exclusive or secret information'
                    ],
                    'verification_techniques': [
                        'Check the original source before sharing',
                        'Look for verification badges on accounts',
                        'Search for fact-checks on the claim',
                        'Consider the motivation behind the post',
                        'Pause before reacting emotionally'
                    ]
                }
            },
            
            'visual_media_analysis': {
                'id': 'visual_media_analysis',
                'title': 'Analyzing Images and Videos',
                'description': 'Detect manipulated visual content and verify image authenticity',
                'level': 'intermediate',
                'estimated_time': 50,
                'prerequisites': ['source_evaluation'],
                'topics': [
                    'Reverse image searching',
                    'Identifying deepfakes and manipulated videos',
                    'Photo manipulation detection',
                    'Context and metadata analysis',
                    'Visual verification tools'
                ],
                'content': {
                    'manipulation_signs': [
                        'Inconsistent lighting or shadows',
                        'Blurred or pixelated areas',
                        'Unnatural facial expressions',
                        'Mismatched image quality in different areas',
                        'Inconsistent backgrounds or perspectives'
                    ],
                    'verification_tools': [
                        'Google Reverse Image Search',
                        'TinEye reverse search',
                        'Yandex image search',
                        'InVID browser extension',
                        'FotoForensics analysis'
                    ]
                }
            },
            
            'advanced_verification': {
                'id': 'advanced_verification',
                'title': 'Advanced Verification Techniques',
                'description': 'Professional-level fact-checking and investigation methods',
                'level': 'advanced',
                'estimated_time': 90,
                'prerequisites': ['social_media_literacy', 'visual_media_analysis'],
                'topics': [
                    'Open source intelligence (OSINT)',
                    'Cross-platform verification',
                    'Timeline and location verification',
                    'Expert consultation strategies',
                    'Building verification reports'
                ],
                'content': {
                    'osint_techniques': [
                        'Geolocation using visual clues',
                        'Metadata analysis',
                        'Social network analysis',
                        'Timeline reconstruction',
                        'Public records research'
                    ],
                    'professional_tools': [
                        'Maltego for network analysis',
                        'Bellingcat online investigation toolkit',
                        'Wayback Machine for historical content',
                        'Whois database searches',
                        'Social media archiving tools'
                    ]
                }
            },
            
            'cultural_context_india': {
                'id': 'cultural_context_india',
                'title': 'Indian Context and Misinformation',
                'description': 'Understanding misinformation patterns specific to India',
                'level': 'intermediate',
                'estimated_time': 75,
                'prerequisites': ['beginner_basics'],
                'topics': [
                    'Common misinformation themes in India',
                    'Religious and political sensitivities',
                    'Regional language considerations',
                    'WhatsApp forward culture',
                    'Traditional vs digital media'
                ],
                'content': {
                    'common_themes': [
                        'Health and medical misinformation',
                        'Political conspiracy theories',
                        'Religious communalism',
                        'Economic rumors and panic',
                        'Celebrity death hoaxes'
                    ],
                    'platform_specific': {
                        'WhatsApp': 'Family groups, emotional sharing, limited fact-checking',
                        'Facebook': 'Community pages, viral videos, image-based content',
                        'Twitter': 'Breaking news, political discussions, real-time events',
                        'YouTube': 'Video testimonials, conspiracy documentaries, influencer content'
                    }
                }
            }
        }
    
    def _load_achievements(self) -> Dict[str, Dict]:
        """Load achievement system for gamified learning."""
        return {
            'first_verification': {
                'id': 'first_verification',
                'title': 'Truth Seeker',
                'description': 'Complete your first content verification',
                'icon': '🔍',
                'points': 10,
                'requirement_type': 'verification_count',
                'requirement_value': 1
            },
            'verification_streak': {
                'id': 'verification_streak',
                'title': 'Consistency Champion',
                'description': 'Verify content for 7 consecutive days',
                'icon': '🔥',
                'points': 50,
                'requirement_type': 'daily_streak',
                'requirement_value': 7
            },
            'module_completion': {
                'id': 'module_completion',
                'title': 'Knowledge Builder',
                'description': 'Complete your first learning module',
                'icon': '📚',
                'points': 25,
                'requirement_type': 'modules_completed',
                'requirement_value': 1
            },
            'perfect_quiz': {
                'id': 'perfect_quiz',
                'title': 'Quiz Master',
                'description': 'Score 100% on any quiz',
                'icon': '💯',
                'points': 30,
                'requirement_type': 'perfect_quiz_score',
                'requirement_value': 1
            },
            'helper': {
                'id': 'helper',
                'title': 'Community Helper',
                'description': 'Provide feedback on 10 verifications',
                'icon': '🤝',
                'points': 40,
                'requirement_type': 'feedback_count',
                'requirement_value': 10
            },
            'expert': {
                'id': 'expert',
                'title': 'Misinformation Expert',
                'description': 'Complete all learning modules',
                'icon': '🎓',
                'points': 100,
                'requirement_type': 'all_modules_completed',
                'requirement_value': 1
            },
            'accuracy_master': {
                'id': 'accuracy_master',
                'title': 'Accuracy Master',
                'description': 'Maintain 90%+ verification accuracy for 30 days',
                'icon': '🎯',
                'points': 75,
                'requirement_type': 'accuracy_streak',
                'requirement_value': 30
            }
        }
    
    def _load_quiz_questions(self) -> Dict[str, List[Dict]]:
        """Load quiz questions for each module."""
        return {
            'beginner_basics': [
                {
                    'question': 'What is the difference between misinformation and disinformation?',
                    'options': [
                        'There is no difference',
                        'Misinformation is false information regardless of intent, disinformation is deliberately false',
                        'Misinformation is worse than disinformation',
                        'Disinformation only applies to political content'
                    ],
                    'correct_answer': 1,
                    'explanation': 'Misinformation is false information shared without malicious intent, while disinformation is deliberately created to deceive.'
                },
                {
                    'question': 'Which of these is a red flag for potentially unreliable information?',
                    'options': [
                        'The article cites multiple sources',
                        'The headline uses emotional language like "SHOCKING" or "UNBELIEVABLE"',
                        'The author\'s name and credentials are provided',
                        'The publication date is recent'
                    ],
                    'correct_answer': 1,
                    'explanation': 'Emotional, sensational language in headlines is often used to grab attention and may indicate unreliable content.'
                },
                {
                    'question': 'What should you do before sharing information on social media?',
                    'options': [
                        'Share it immediately if it\'s interesting',
                        'Only share if it supports your views',
                        'Verify the information from reliable sources first',
                        'Add your own opinion to the post'
                    ],
                    'correct_answer': 2,
                    'explanation': 'Always verify information from reliable sources before sharing to prevent the spread of misinformation.'
                }
            ],
            
            'source_evaluation': [
                {
                    'question': 'Which type of source generally has the highest credibility?',
                    'options': [
                        'Social media posts',
                        'Personal blogs',
                        'Peer-reviewed academic journals',
                        'Opinion articles'
                    ],
                    'correct_answer': 2,
                    'explanation': 'Peer-reviewed academic journals undergo rigorous fact-checking and review processes by experts.'
                },
                {
                    'question': 'What is a good way to check if a news website is reliable?',
                    'options': [
                        'Check if it has a colorful design',
                        'Look for an "About Us" page and editorial policies',
                        'See if it has many advertisements',
                        'Check if the articles are short'
                    ],
                    'correct_answer': 1,
                    'explanation': 'Reliable news sources typically provide transparency about their organization, staff, and editorial standards.'
                }
            ],
            
            'social_media_literacy': [
                {
                    'question': 'What is a "filter bubble" in social media?',
                    'options': [
                        'A way to filter out spam',
                        'When algorithms show you only information that confirms your existing beliefs',
                        'A privacy setting for your profile',
                        'A method to block unwanted users'
                    ],
                    'correct_answer': 1,
                    'explanation': 'Filter bubbles occur when algorithms create an echo chamber by showing content similar to what you\'ve previously engaged with.'
                },
                {
                    'question': 'What should make you suspicious of viral content?',
                    'options': [
                        'It has many shares and likes',
                        'It\'s shared by your friends',
                        'It asks you to "share before it\'s deleted"',
                        'It\'s about current events'
                    ],
                    'correct_answer': 2,
                    'explanation': 'Urgent calls to share "before deletion" are often used to spread misinformation quickly before fact-checkers can respond.'
                }
            ]
        }
    
    def _load_tips_and_tricks(self) -> List[Dict]:
        """Load daily tips and tricks for users."""
        return [
            {
                'category': 'verification',
                'title': 'Check the Date',
                'tip': 'Always check when an article was published. Old news can be recycled to seem current.',
                'example': 'A 2018 article about protests might be shared during 2023 events to create confusion.'
            },
            {
                'category': 'sources',
                'title': 'Look for Contact Information',
                'tip': 'Reliable sources provide clear contact information and author details.',
                'example': 'Check if the website has an address, phone number, or email for inquiries.'
            },
            {
                'category': 'images',
                'title': 'Reverse Image Search',
                'tip': 'Use Google Images to check if a photo has been used elsewhere or manipulated.',
                'example': 'Right-click an image and select "Search Google for this image".'
            },
            {
                'category': 'social_media',
                'title': 'Check Account Verification',
                'tip': 'Blue checkmarks indicate verified accounts, but still cross-check important claims.',
                'example': 'Even verified accounts can share unverified information or be hacked.'
            },
            {
                'category': 'emotional',
                'title': 'Pause Before Reacting',
                'tip': 'Take a moment to think before sharing emotional content. Strong emotions can cloud judgment.',
                'example': 'If a post makes you very angry or sad, take time to verify it first.'
            },
            {
                'category': 'whatsapp',
                'title': 'Be Cautious with Forwards',
                'tip': 'WhatsApp forwards often lack context. Verify before resharing.',
                'example': 'Check if the message has original source information or just says "Forward as received".'
            }
        ]
    
    def _load_case_studies(self) -> List[Dict]:
        """Load real-world case studies for learning."""
        return [
            {
                'id': 'covid_cure_hoax',
                'title': 'COVID-19 "Miracle Cure" Misinformation',
                'description': 'Analysis of false medical claims during the pandemic',
                'scenario': '''
                During COVID-19, a WhatsApp message claimed that drinking hot water with lemon
                every hour would prevent the virus. The message was attributed to a "doctor friend"
                and urged people to share it with everyone.
                ''',
                'red_flags': [
                    'Vague attribution ("doctor friend")',
                    'Too-good-to-be-true simple solution',
                    'Urgent sharing request',
                    'No scientific evidence provided',
                    'Contradicts official health guidance'
                ],
                'verification_steps': [
                    'Check with official health organizations (WHO, CDC, local health ministry)',
                    'Search for scientific studies on the claimed cure',
                    'Verify if any credible medical professionals endorse this',
                    'Look for fact-checks from reliable sources'
                ],
                'lesson': 'Medical misinformation can be harmful. Always verify health claims with official sources.',
                'outcome': 'This claim was debunked by WHO and multiple fact-checking organizations.'
            },
            
            {
                'id': 'election_fraud_video',
                'title': 'Manipulated Election Video',
                'description': 'How old footage was misused to support false claims',
                'scenario': '''
                A video showing ballot boxes being stuffed went viral on social media,
                claimed to be evidence of fraud in recent elections. The video had
                emotional music and dramatic captions.
                ''',
                'red_flags': [
                    'No clear date or location information',
                    'Emotional background music (manipulation tactic)',
                    'Dramatic captions without context',
                    'Shared by accounts with political bias',
                    'No verification from election officials'
                ],
                'verification_steps': [
                    'Reverse image search on video frames',
                    'Check election commission official statements',
                    'Look for original source and context',
                    'Cross-reference with established news reports',
                    'Verify location and timing of the footage'
                ],
                'lesson': 'Videos can be taken out of context or from different times/places.',
                'outcome': 'The video was found to be from a different country and unrelated to the claimed election.'
            }
        ]
    
    def get_educational_content(self, user_id: int, content_type: str = 'module',
                              difficulty_level: str = 'beginner', topics: List[str] = None) -> Dict[str, Any]:
        """Get personalized educational content for a user."""
        try:
            if content_type == 'module':
                return self._get_learning_module(user_id, difficulty_level, topics)
            elif content_type == 'quiz':
                return self._get_quiz_content(user_id, difficulty_level)
            elif content_type == 'tip':
                return self._get_daily_tip(user_id)
            elif content_type == 'case_study':
                return self._get_case_study(user_id, difficulty_level)
            else:
                return self._get_mixed_content(user_id, difficulty_level)
        
        except Exception as e:
            logger.error(f"Error getting educational content: {e}")
            return {
                'error': 'Unable to fetch educational content',
                'fallback_tip': 'Always verify information with multiple reliable sources before sharing.'
            }
    
    def _get_learning_module(self, user_id: int, difficulty_level: str, topics: List[str] = None) -> Dict[str, Any]:
        """Get appropriate learning module for user."""
        user_progress = self.get_user_progress(user_id)
        completed_modules = set(user_progress.get('completed_modules', []))
        
        # Filter modules by level and prerequisites
        available_modules = []
        for module_id, module in self.learning_modules.items():
            # Check level requirement
            if module['level'] != difficulty_level:
                continue
            
            # Check if already completed
            if module_id in completed_modules:
                continue
            
            # Check prerequisites
            prerequisites_met = all(prereq in completed_modules for prereq in module['prerequisites'])
            if not prerequisites_met:
                continue
            
            # Check topic filter
            if topics:
                module_topics_lower = [topic.lower() for topic in module['topics']]
                if not any(topic.lower() in module_topics_lower for topic in topics):
                    continue
            
            available_modules.append(module)
        
        if not available_modules:
            # Return next level content or review
            return self._get_next_level_content(user_id, completed_modules)
        
        # Return the most suitable module
        recommended_module = available_modules[0]  # For simplicity, return first available
        
        return {
            'type': 'learning_module',
            'module': recommended_module,
            'user_progress': user_progress,
            'estimated_completion': recommended_module['estimated_time'],
            'next_steps': self._get_next_steps(user_id, recommended_module['id'])
        }
    
    def _get_quiz_content(self, user_id: int, difficulty_level: str) -> Dict[str, Any]:
        """Generate quiz content based on user progress."""
        user_progress = self.get_user_progress(user_id)
        completed_modules = user_progress.get('completed_modules', [])
        
        # Find appropriate quiz topics
        available_quizzes = []
        for module_id in completed_modules:
            if module_id in self.quiz_questions:
                available_quizzes.extend(self.quiz_questions[module_id])
        
        if not available_quizzes:
            # Default to basic questions
            available_quizzes = self.quiz_questions.get('beginner_basics', [])
        
        # Select random questions
        num_questions = min(5, len(available_quizzes))
        selected_questions = random.sample(available_quizzes, num_questions)
        
        return {
            'type': 'quiz',
            'questions': selected_questions,
            'total_questions': len(selected_questions),
            'estimated_time': len(selected_questions) * 2,  # 2 minutes per question
            'scoring': {
                'passing_score': 70,
                'perfect_score': 100
            }
        }
    
    def _get_daily_tip(self, user_id: int) -> Dict[str, Any]:
        """Get personalized daily tip for user."""
        user_progress = self.get_user_progress(user_id)
        user_level = self.get_user_level(user_id)
        
        # Filter tips based on user level and recent activity
        relevant_tips = []
        recent_verification_types = user_progress.get('recent_verification_types', [])
        
        for tip in self.tips_and_tricks:
            # Prioritize tips relevant to user's recent activity
            if tip['category'] in recent_verification_types:
                relevant_tips.append(tip)
        
        # If no relevant tips, use all tips
        if not relevant_tips:
            relevant_tips = self.tips_and_tricks
        
        # Select random tip
        selected_tip = random.choice(relevant_tips)
        
        return {
            'type': 'daily_tip',
            'tip': selected_tip,
            'user_level': user_level,
            'relevance_score': 0.8 if selected_tip['category'] in recent_verification_types else 0.6
        }
    
    def _get_case_study(self, user_id: int, difficulty_level: str) -> Dict[str, Any]:
        """Get appropriate case study for user."""
        user_progress = self.get_user_progress(user_id)
        completed_case_studies = set(user_progress.get('completed_case_studies', []))
        
        # Filter available case studies
        available_studies = [study for study in self.case_studies 
                           if study['id'] not in completed_case_studies]
        
        if not available_studies:
            available_studies = self.case_studies  # Reset if all completed
        
        selected_study = random.choice(available_studies)
        
        return {
            'type': 'case_study',
            'case_study': selected_study,
            'interactive_elements': {
                'questions': [
                    'What red flags can you identify in this scenario?',
                    'What would be your first step in verifying this information?',
                    'How would you explain to someone why this is unreliable?'
                ],
                'activities': [
                    'Practice the verification steps described',
                    'Find similar examples online',
                    'Share your findings with others'
                ]
            }
        }
    
    def _get_mixed_content(self, user_id: int, difficulty_level: str) -> Dict[str, Any]:
        """Get mixed educational content for variety."""
        content_types = ['tip', 'quiz', 'case_study']
        selected_type = random.choice(content_types)
        
        return self.get_educational_content(user_id, selected_type, difficulty_level)
    
    def get_user_progress(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user progress information."""
        # In production, this would query the database
        # For now, return sample data structure
        return {
            'user_id': user_id,
            'literacy_score': 75.5,
            'level': 'intermediate',
            'completed_modules': ['beginner_basics', 'source_evaluation'],
            'in_progress_modules': ['social_media_literacy'],
            'completed_case_studies': ['covid_cure_hoax'],
            'quiz_scores': {
                'beginner_basics': 85,
                'source_evaluation': 92
            },
            'total_verifications': 45,
            'accurate_verifications': 38,
            'accuracy_rate': 84.4,
            'streak_days': 12,
            'recent_verification_types': ['text', 'social_media', 'url'],
            'achievements_earned': ['first_verification', 'module_completion'],
            'total_study_time': 180,  # minutes
            'last_active': datetime.now().isoformat(),
            'preferences': {
                'content_language': 'en',
                'difficulty_preference': 'adaptive',
                'notification_frequency': 'daily'
            }
        }
    
    def get_user_level(self, user_id: int) -> str:
        """Determine user's current skill level."""
        progress = self.get_user_progress(user_id)
        
        completed_modules = len(progress.get('completed_modules', []))
        accuracy_rate = progress.get('accuracy_rate', 0)
        total_verifications = progress.get('total_verifications', 0)
        
        # Level calculation logic
        if completed_modules >= 5 and accuracy_rate >= 90 and total_verifications >= 100:
            return 'expert'
        elif completed_modules >= 3 and accuracy_rate >= 80 and total_verifications >= 30:
            return 'advanced'
        elif completed_modules >= 2 and accuracy_rate >= 70 and total_verifications >= 10:
            return 'intermediate'
        else:
            return 'beginner'
    
    def get_user_achievements(self, user_id: int) -> List[Dict]:
        """Get user's earned and available achievements."""
        progress = self.get_user_progress(user_id)
        earned_achievements = []
        available_achievements = []
        
        for achievement_id, achievement in self.achievements.items():
            is_earned = self._check_achievement_earned(achievement, progress)
            
            achievement_data = {
                **achievement,
                'earned': is_earned,
                'progress': self._calculate_achievement_progress(achievement, progress)
            }
            
            if is_earned:
                earned_achievements.append(achievement_data)
            else:
                available_achievements.append(achievement_data)
        
        return {
            'earned': earned_achievements,
            'available': available_achievements,
            'total_points': sum(ach['points'] for ach in earned_achievements)
        }
    
    def _check_achievement_earned(self, achievement: Dict, progress: Dict) -> bool:
        """Check if user has earned a specific achievement."""
        req_type = achievement['requirement_type']
        req_value = achievement['requirement_value']
        
        if req_type == 'verification_count':
            return progress.get('total_verifications', 0) >= req_value
        elif req_type == 'modules_completed':
            return len(progress.get('completed_modules', [])) >= req_value
        elif req_type == 'accuracy_streak':
            return progress.get('accuracy_rate', 0) >= 90 and progress.get('streak_days', 0) >= req_value
        elif req_type == 'all_modules_completed':
            return len(progress.get('completed_modules', [])) >= len(self.learning_modules)
        elif req_type == 'perfect_quiz_score':
            quiz_scores = progress.get('quiz_scores', {})
            return any(score == 100 for score in quiz_scores.values())
        
        return False
    
    def _calculate_achievement_progress(self, achievement: Dict, progress: Dict) -> float:
        """Calculate progress towards achievement (0.0 to 1.0)."""
        req_type = achievement['requirement_type']
        req_value = achievement['requirement_value']
        
        if req_type == 'verification_count':
            current = progress.get('total_verifications', 0)
            return min(current / req_value, 1.0)
        elif req_type == 'modules_completed':
            current = len(progress.get('completed_modules', []))
            return min(current / req_value, 1.0)
        elif req_type == 'accuracy_streak':
            if progress.get('accuracy_rate', 0) >= 90:
                current = progress.get('streak_days', 0)
                return min(current / req_value, 1.0)
            return 0.0
        
        return 0.0
    
    def get_personalized_recommendations(self, user_id: int) -> List[Dict]:
        """Get personalized learning recommendations for user."""
        progress = self.get_user_progress(user_id)
        user_level = self.get_user_level(user_id)
        completed_modules = set(progress.get('completed_modules', []))
        
        recommendations = []
        
        # Module recommendations
        for module_id, module in self.learning_modules.items():
            if module_id not in completed_modules:
                prerequisites_met = all(prereq in completed_modules for prereq in module['prerequisites'])
                if prerequisites_met and module['level'] == user_level:
                    recommendations.append({
                        'type': 'module',
                        'title': module['title'],
                        'description': module['description'],
                        'estimated_time': module['estimated_time'],
                        'priority': 'high',
                        'reason': 'Matches your current skill level'
                    })
        
        # Practice recommendations based on weak areas
        accuracy_rate = progress.get('accuracy_rate', 100)
        if accuracy_rate < 80:
            recommendations.append({
                'type': 'practice',
                'title': 'Accuracy Improvement Practice',
                'description': 'Practice with guided examples to improve verification accuracy',
                'estimated_time': 20,
                'priority': 'high',
                'reason': f'Your accuracy rate is {accuracy_rate}% - let\'s improve it!'
            })
        
        # Streak maintenance
        streak_days = progress.get('streak_days', 0)
        if streak_days > 0:
            recommendations.append({
                'type': 'daily_verification',
                'title': 'Maintain Your Streak',
                'description': f'Keep your {streak_days}-day verification streak going!',
                'estimated_time': 5,
                'priority': 'medium',
                'reason': 'Consistency helps build strong verification habits'
            })
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _get_next_level_content(self, user_id: int, completed_modules: set) -> Dict[str, Any]:
        """Get content for when user is ready for next level."""
        current_level = self.get_user_level(user_id)
        
        level_progression = {
            'beginner': 'intermediate',
            'intermediate': 'advanced',
            'advanced': 'expert'
        }
        
        next_level = level_progression.get(current_level, 'expert')
        
        return {
            'type': 'level_progression',
            'current_level': current_level,
            'next_level': next_level,
            'congratulations': f'Congratulations! You\'ve completed all {current_level} modules.',
            'next_steps': f'Ready to advance to {next_level} level?',
            'unlock_requirements': 'Complete the readiness assessment to unlock new content.'
        }
    
    def _get_next_steps(self, user_id: int, current_module_id: str) -> List[str]:
        """Get suggested next steps after completing a module."""
        module = self.learning_modules.get(current_module_id, {})
        
        next_steps = [
            f'Take the quiz for {module.get("title", "this module")}',
            'Practice with real examples',
            'Share what you learned with others'
        ]
        
        # Find dependent modules
        for module_id, mod in self.learning_modules.items():
            if current_module_id in mod.get('prerequisites', []):
                next_steps.append(f'Continue to "{mod["title"]}" module')
                break
        
        return next_steps
    
    def record_module_completion(self, user_id: int, module_id: str, score: float, time_spent: int) -> Dict[str, Any]:
        """Record completion of a learning module."""
        # In production, this would update the database
        completion_data = {
            'user_id': user_id,
            'module_id': module_id,
            'score': score,
            'time_spent': time_spent,
            'completed_at': datetime.now().isoformat(),
            'next_recommendations': self.get_personalized_recommendations(user_id)
        }
        
        # Check for new achievements
        new_achievements = self._check_new_achievements(user_id)
        if new_achievements:
            completion_data['new_achievements'] = new_achievements
        
        return completion_data
    
    def _check_new_achievements(self, user_id: int) -> List[Dict]:
        """Check for newly earned achievements."""
        # This would implement real achievement checking logic
        return []
    
    def get_learning_analytics(self, user_id: int) -> Dict[str, Any]:
        """Get detailed learning analytics for user."""
        progress = self.get_user_progress(user_id)
        
        return {
            'learning_velocity': self._calculate_learning_velocity(progress),
            'knowledge_gaps': self._identify_knowledge_gaps(progress),
            'strength_areas': self._identify_strengths(progress),
            'time_investment': self._analyze_time_investment(progress),
            'improvement_trends': self._calculate_improvement_trends(progress),
            'peer_comparison': self._get_peer_comparison(user_id),
            'personalized_insights': self._generate_insights(progress)
        }
    
    def _calculate_learning_velocity(self, progress: Dict) -> Dict[str, float]:
        """Calculate how quickly user is learning."""
        total_time = progress.get('total_study_time', 0)
        completed_modules = len(progress.get('completed_modules', []))
        
        return {
            'modules_per_hour': completed_modules / (total_time / 60) if total_time > 0 else 0,
            'average_module_time': total_time / completed_modules if completed_modules > 0 else 0,
            'efficiency_score': min(completed_modules / max(total_time / 60, 1) * 10, 100)
        }
    
    def _identify_knowledge_gaps(self, progress: Dict) -> List[str]:
        """Identify areas where user needs improvement."""
        gaps = []
        accuracy_rate = progress.get('accuracy_rate', 100)
        
        if accuracy_rate < 70:
            gaps.append('Basic verification skills need strengthening')
        
        completed_modules = set(progress.get('completed_modules', []))
        if 'source_evaluation' not in completed_modules:
            gaps.append('Source evaluation skills')
        
        if 'visual_media_analysis' not in completed_modules:
            gaps.append('Image and video verification techniques')
        
        return gaps
    
    def _identify_strengths(self, progress: Dict) -> List[str]:
        """Identify user's strong areas."""
        strengths = []
        accuracy_rate = progress.get('accuracy_rate', 0)
        
        if accuracy_rate > 90:
            strengths.append('High verification accuracy')
        
        if progress.get('streak_days', 0) > 7:
            strengths.append('Consistent practice habits')
        
        quiz_scores = progress.get('quiz_scores', {})
        high_scoring_modules = [module for module, score in quiz_scores.items() if score > 85]
        
        if high_scoring_modules:
            strengths.append(f'Strong knowledge in: {", ".join(high_scoring_modules)}')
        
        return strengths
    
    def _analyze_time_investment(self, progress: Dict) -> Dict[str, Any]:
        """Analyze user's time investment patterns."""
        total_time = progress.get('total_study_time', 0)
        completed_modules = len(progress.get('completed_modules', []))
        
        return {
            'total_study_time': total_time,
            'average_session_length': total_time / max(completed_modules, 1),
            'efficiency_rating': 'high' if total_time / max(completed_modules, 1) < 45 else 'moderate',
            'recommended_session_length': '30-45 minutes for optimal retention'
        }
    
    def _calculate_improvement_trends(self, progress: Dict) -> Dict[str, Any]:
        """Calculate improvement trends over time."""
        # This would use historical data in production
        return {
            'accuracy_trend': 'improving',
            'learning_speed_trend': 'stable',
            'engagement_trend': 'increasing'
        }
    
    def _get_peer_comparison(self, user_id: int) -> Dict[str, Any]:
        """Compare user's progress with peers."""
        # This would use aggregated data in production
        return {
            'percentile_rank': 75,
            'above_average_areas': ['accuracy', 'consistency'],
            'improvement_opportunities': ['speed', 'advanced_techniques']
        }
    
    def _generate_insights(self, progress: Dict) -> List[str]:
        """Generate personalized insights for user."""
        insights = []
        
        accuracy_rate = progress.get('accuracy_rate', 0)
        if accuracy_rate > 85:
            insights.append('Your verification accuracy is excellent! Consider helping others learn.')
        
        streak_days = progress.get('streak_days', 0)
        if streak_days > 14:
            insights.append('Your consistency is impressive! This builds strong digital literacy habits.')
        
        completed_modules = len(progress.get('completed_modules', []))
        if completed_modules >= 3:
            insights.append('You\'re making great progress! Consider sharing your knowledge with friends and family.')
        
        return insights
