"""
MitraVerify Verification Engine
Comprehensive AI-powered content verification system

This module provides sophisticated algorithms for detecting misinformation
across multiple content types including text, images, videos, and URLs.
"""

import logging
import re
import hashlib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
import spacy
import nltk
from textblob import TextBlob
from langdetect import detect
import validators
from fake_useragent import UserAgent

from utils.text_analyzer import TextAnalyzer
from utils.cultural_context import CulturalContextAnalyzer

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

logger = logging.getLogger(__name__)

class VerificationEngine:
    """
    Main verification engine that orchestrates different verification modules
    to provide comprehensive misinformation detection.
    """
    
    def __init__(self):
        """Initialize the verification engine with AI models and analyzers."""
        self.text_analyzer = TextAnalyzer()
        self.cultural_analyzer = CulturalContextAnalyzer()
        self.user_agent = UserAgent()
        
        # Load spaCy models
        try:
            self.nlp_en = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("English spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp_en = None
        
        # Initialize machine learning models
        self.text_classifier = None
        self.source_credibility_model = None
        self.urgency_detector = None
        
        # Known misinformation patterns
        self.misinformation_patterns = self._load_misinformation_patterns()
        
        # Credible source database
        self.credible_sources = self._load_credible_sources()
        
        # Initialize models
        self._initialize_models()
        
        logger.info("VerificationEngine initialized successfully")
    
    def _load_misinformation_patterns(self) -> Dict[str, List[str]]:
        """Load known misinformation patterns and keywords."""
        return {
            'urgency_keywords': [
                'urgent', 'breaking', 'alert', 'immediate', 'emergency',
                'critical', 'warning', 'danger', 'threat', 'crisis',
                'shocking', 'exclusive', 'leaked', 'secret', 'hidden',
                'तुरंत', 'खतरा', 'चेतावनी', 'आपातकाल', 'महत्वपूर्ण',
                'உடனடி', 'அபாயம்', 'எச্ছাপনী', 'গুরুত্বপূর্ণ'
            ],
            'emotional_manipulation': [
                'will shock you', "you won't believe", 'doctors hate',
                "government doesn't want", "they don't want you to know",
                'conspiracy', 'cover up', 'suppressed', 'banned',
                'आपको चौंका देगा', 'सरकार नहीं चाहती', 'छुपाया गया'
            ],
            'false_medical_claims': [
                'miracle cure', 'instant healing', '100% natural',
                'pharmaceutical conspiracy', 'big pharma', 'suppressed treatment',
                'चमत्कारी इलाज', 'तुरंत ठीक', 'प्राकृतिक उपचार'
            ],
            'political_manipulation': [
                'leaked document', 'insider revealed', 'government plan',
                'secret meeting', 'classified information', 'whistleblower',
                'गुप्त दस्तावेज़', 'सरकारी योजना', 'गुप्त बैठक'
            ]
        }
    
    def _load_credible_sources(self) -> Dict[str, float]:
        """Load credible source database with credibility scores."""
        return {
            # International news sources
            'bbc.com': 0.95,
            'reuters.com': 0.95,
            'ap.org': 0.95,
            'npr.org': 0.90,
            'cnn.com': 0.85,
            'theguardian.com': 0.90,
            'nytimes.com': 0.90,
            'washingtonpost.com': 0.88,
            
            # Indian news sources
            'thehindu.com': 0.92,
            'indianexpress.com': 0.90,
            'ndtv.com': 0.85,
            'hindustantimes.com': 0.85,
            'timesofIndia.indiatimes.com': 0.80,
            'livemint.com': 0.88,
            'scroll.in': 0.85,
            'thewire.in': 0.83,
            'news18.com': 0.75,
            'zee news.india.com': 0.70,
            'aajtak.in': 0.75,
            'abpnews.abplive.com': 0.75,
            
            # Government sources
            'pib.gov.in': 0.95,
            'mygov.in': 0.95,
            'india.gov.in': 0.95,
            'who.int': 0.95,
            'cdc.gov': 0.95,
            'mohfw.gov.in': 0.95,
            
            # Fact-checking sites
            'factcheck.afp.com': 0.95,
            'snopes.com': 0.92,
            'politifact.com': 0.90,
            'factchecker.in': 0.90,
            'boomlive.in': 0.88,
            'altnews.in': 0.88,
            'thequint.com/news/webqoof': 0.85,
            'vishvasnews.com': 0.85,
            
            # Low credibility sources
            'whatsappforwards.com': 0.20,
            'fakingnews.firstpost.com': 0.25,
            'postcard.news': 0.30,
            'opindia.com': 0.40,
            'swarajyamag.com': 0.45
        }
    
    def _initialize_models(self):
        """Initialize and train machine learning models."""
        try:
            # Create dummy training data for demonstration
            # In production, this would use real labeled datasets
            training_data = self._generate_training_data()
            
            # Text classification model
            self.text_classifier = self._train_text_classifier(training_data)
            
            # Source credibility model
            self.source_credibility_model = self._train_credibility_model()
            
            # Urgency detection model
            self.urgency_detector = self._train_urgency_detector(training_data)
            
            logger.info("All ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            # Fallback to rule-based systems
            self._initialize_fallback_models()
    
    def _generate_training_data(self) -> pd.DataFrame:
        """Generate synthetic training data for model training."""
        # This is a simplified version. In production, use real labeled datasets
        fake_news_samples = [
            "BREAKING: Government plans to ban cash transactions next week!",
            "Doctors HATE this one simple trick that cures cancer instantly",
            "SECRET: Politicians meeting tonight to decide your fate",
            "URGENT: Share this before it gets deleted by authorities",
            "LEAKED: Government document reveals shocking truth about vaccines"
        ]
        
        real_news_samples = [
            "Prime Minister announces new education policy in parliament session",
            "Stock market closes higher amid positive economic indicators",
            "Health ministry releases guidelines for seasonal flu prevention",
            "Supreme Court hearing scheduled for constitutional amendment case",
            "Economic survey shows gradual recovery in manufacturing sector"
        ]
        
        data = []
        
        # Add fake news samples
        for text in fake_news_samples:
            data.append({
                'text': text,
                'label': 'false',
                'urgency_score': np.random.uniform(0.7, 1.0),
                'emotional_score': np.random.uniform(0.6, 0.9),
                'source_credibility': np.random.uniform(0.1, 0.4)
            })
        
        # Add real news samples
        for text in real_news_samples:
            data.append({
                'text': text,
                'label': 'verified',
                'urgency_score': np.random.uniform(0.1, 0.4),
                'emotional_score': np.random.uniform(0.2, 0.5),
                'source_credibility': np.random.uniform(0.7, 0.95)
            })
        
        return pd.DataFrame(data)
    
    def _train_text_classifier(self, training_data: pd.DataFrame) -> RandomForestClassifier:
        """Train text classification model."""
        try:
            # Extract features
            vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            X_text = vectorizer.fit_transform(training_data['text'])
            
            # Additional features
            X_features = training_data[['urgency_score', 'emotional_score', 'source_credibility']].values
            
            # Combine features
            X = np.hstack([X_text.toarray(), X_features])
            y = training_data['label']
            
            # Train model
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X, y)
            
            # Store vectorizer for later use
            self.text_vectorizer = vectorizer
            
            return model
            
        except Exception as e:
            logger.error(f"Error training text classifier: {e}")
            return None
    
    def _train_credibility_model(self) -> LogisticRegression:
        """Train source credibility assessment model."""
        try:
            # Create training data for source credibility
            sources = list(self.credible_sources.keys())
            features = []
            labels = []
            
            for source in sources:
                # Extract domain features
                domain_features = self._extract_domain_features(source)
                features.append(domain_features)
                
                # Convert continuous credibility scores to discrete classes
                credibility_score = self.credible_sources[source]
                if credibility_score >= 0.8:
                    label = 'high'
                elif credibility_score >= 0.6:
                    label = 'medium'
                else:
                    label = 'low'
                labels.append(label)
            
            if len(features) > 10:  # Minimum samples needed
                X = np.array(features)
                y = np.array(labels)
                
                model = LogisticRegression(random_state=42)
                model.fit(X, y)
                return model
            
            return None
            
        except Exception as e:
            logger.error(f"Error training credibility model: {e}")
            return None

    def _extract_domain_features(self, domain: str) -> List[float]:
        """Extract numerical features from a domain name."""
        try:
            features = []
            
            # Domain length
            features.append(len(domain))
            
            # Number of subdomains
            features.append(len(domain.split('.')) - 1)
            
            # Contains common TLDs
            common_tlds = ['.com', '.org', '.gov', '.edu', '.in']
            features.append(sum(1 for tld in common_tlds if domain.endswith(tld)))
            
            # Contains numbers
            features.append(sum(1 for char in domain if char.isdigit()))
            
            # Contains hyphens
            features.append(domain.count('-'))
            
            # Government domain indicator
            features.append(1.0 if '.gov' in domain or '.edu' in domain else 0.0)
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting domain features: {e}")
            return [0.0] * 6  # Return default features

    def _initialize_fallback_models(self):
        """Initialize fallback rule-based models when ML models fail."""
        logger.warning("Using fallback rule-based models")
        self.text_classifier = None
        self.source_credibility_model = None
        self.urgency_detector = None
    
    def _train_urgency_detector(self, training_data: pd.DataFrame) -> GradientBoostingClassifier:
        """Train urgency detection model."""
        try:
            # Create urgency labels
            training_data['is_urgent'] = training_data['urgency_score'] > 0.6
            
            # Extract text features for urgency detection
            urgency_features = []
            for text in training_data['text']:
                features = self._extract_urgency_features(text)
                urgency_features.append(features)
            
            X = np.array(urgency_features)
            y = training_data['is_urgent']
            
            model = GradientBoostingClassifier(n_estimators=50, random_state=42)
            model.fit(X, y)
            
            return model
            
        except Exception as e:
            logger.error(f"Error training urgency detector: {e}")
            return None
    
    def _extract_domain_features(self, domain: str) -> List[float]:
        """Extract features from domain name for credibility assessment."""
        features = []
        
        # Domain length
        features.append(len(domain))
        
        # Has subdomain
        features.append(1.0 if len(domain.split('.')) > 2 else 0.0)
        
        # Contains numbers
        features.append(1.0 if any(char.isdigit() for char in domain) else 0.0)
        
        # Contains hyphens
        features.append(1.0 if '-' in domain else 0.0)
        
        # Top-level domain type
        tld = domain.split('.')[-1]
        features.append(1.0 if tld in ['com', 'org', 'gov', 'edu'] else 0.0)
        
        # Domain age proxy (simplified)
        features.append(0.8 if domain in self.credible_sources else 0.2)
        
        return features
    
    def _extract_urgency_features(self, text: str) -> List[float]:
        """Extract urgency-related features from text."""
        text_lower = text.lower()
        features = []
        
        # Urgency keyword count
        urgency_count = sum(1 for keyword in self.misinformation_patterns['urgency_keywords'] 
                          if keyword in text_lower)
        features.append(urgency_count / len(text.split()))
        
        # Capitalization ratio
        caps_ratio = sum(1 for char in text if char.isupper()) / len(text) if text else 0
        features.append(caps_ratio)
        
        # Exclamation marks
        features.append(text.count('!') / len(text.split()))
        
        # Question marks
        features.append(text.count('?') / len(text.split()))
        
        # All caps words
        words = text.split()
        all_caps_ratio = sum(1 for word in words if word.isupper()) / len(words) if words else 0
        features.append(all_caps_ratio)
        
        return features
    
    def _initialize_fallback_models(self):
        """Initialize fallback rule-based models if ML models fail."""
        logger.warning("Using fallback rule-based models")
        self.text_classifier = None
        self.source_credibility_model = None
        self.urgency_detector = None
    
    def verify_content(self, content: str, content_type: str = 'text', 
                      language: str = 'en', user_context: Dict = None) -> Dict[str, Any]:
        """
        Main verification method that analyzes content for misinformation.
        
        Args:
            content: The content to verify
            content_type: Type of content ('text', 'url', 'image')
            language: Content language
            user_context: Additional user context
            
        Returns:
            Dictionary with verification results
        """
        try:
            start_time = datetime.now()
            
            # Detect language if auto-detect
            if language == 'auto-detect':
                try:
                    language = detect(content)
                except:
                    language = 'en'
            
            # Initialize result structure
            result = {
                'result': 'questionable',  # verified, questionable, false
                'confidence_score': 0.5,
                'analysis_details': {
                    'language': language,
                    'content_type': content_type,
                    'timestamp': start_time.isoformat()
                },
                'educational_tip': '',
                'sources': []
            }
            
            # Route to appropriate verification method
            if content_type == 'url':
                return self._verify_url(content, language, result)
            elif content_type == 'image':
                return self._verify_image_text(content, language, result)
            else:
                return self._verify_text(content, language, result)
                
        except Exception as e:
            logger.error(f"Error in content verification: {e}")
            return {
                'result': 'error',
                'confidence_score': 0.0,
                'analysis_details': {'error': str(e)},
                'educational_tip': 'Unable to verify content due to technical error.',
                'sources': []
            }
    
    def _verify_text(self, content: str, language: str, result: Dict) -> Dict[str, Any]:
        """Verify text content for misinformation."""
        analysis_details = result['analysis_details']
        
        # Basic text analysis
        text_analysis = self.text_analyzer.analyze_text(content, language)
        analysis_details['text_analysis'] = text_analysis
        
        # Sentiment analysis
        blob = TextBlob(content)
        sentiment = blob.sentiment
        analysis_details['sentiment'] = {
            'polarity': sentiment.polarity,
            'subjectivity': sentiment.subjectivity
        }
        
        # Pattern matching for misinformation indicators
        misinformation_indicators = self._detect_misinformation_patterns(content, language)
        analysis_details['misinformation_indicators'] = misinformation_indicators
        
        # Urgency detection
        urgency_score = self._calculate_urgency_score(content)
        analysis_details['urgency_score'] = urgency_score
        
        # Emotional manipulation detection
        emotional_score = self._detect_emotional_manipulation(content)
        analysis_details['emotional_manipulation_score'] = emotional_score
        
        # Logical fallacy detection
        logical_fallacies = self._detect_logical_fallacies(content)
        analysis_details['logical_fallacies'] = logical_fallacies
        
        # Source extraction and credibility check
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
        source_credibility = 0.5
        
        if urls:
            source_scores = []
            for url in urls:
                score = self._assess_source_credibility(url)
                source_scores.append(score)
            source_credibility = np.mean(source_scores) if source_scores else 0.5
        
        analysis_details['source_credibility'] = source_credibility
        analysis_details['extracted_urls'] = urls
        
        # Calculate overall confidence score
        confidence_factors = []
        
        # Factor 1: Misinformation pattern intensity
        pattern_intensity = sum(indicator['severity'] for indicator in misinformation_indicators) / 10
        confidence_factors.append(min(pattern_intensity, 1.0))
        
        # Factor 2: Urgency and emotional manipulation
        manipulation_score = (urgency_score + emotional_score) / 2
        confidence_factors.append(manipulation_score)
        
        # Factor 3: Source credibility (inverted)
        confidence_factors.append(1.0 - source_credibility)
        
        # Factor 4: Sentiment extremity
        sentiment_extremity = abs(sentiment.polarity)
        confidence_factors.append(sentiment_extremity)
        
        # Factor 5: Logical fallacies
        fallacy_score = len(logical_fallacies) / 10  # Normalize by max expected fallacies
        confidence_factors.append(min(fallacy_score, 1.0))
        
        # Calculate weighted confidence score
        weights = [0.3, 0.25, 0.2, 0.15, 0.1]
        overall_score = sum(factor * weight for factor, weight in zip(confidence_factors, weights))
        
        # Determine result based on confidence score
        if overall_score < 0.3:
            result['result'] = 'verified'
            result['confidence_score'] = 1.0 - overall_score
            result['educational_tip'] = "This content appears to be reliable. Always verify with multiple sources."
        elif overall_score < 0.7:
            result['result'] = 'questionable'
            result['confidence_score'] = 0.7
            result['educational_tip'] = "This content has some concerning elements. Verify with trusted sources before sharing."
        else:
            result['result'] = 'false'
            result['confidence_score'] = overall_score
            result['educational_tip'] = "This content shows strong indicators of misinformation. Do not share without verification."
        
        # Add cultural context
        cultural_context = self.cultural_analyzer.analyze_cultural_context(content, language)
        analysis_details['cultural_context'] = cultural_context
        
        # Generate fact-checking suggestions
        result['sources'] = self._suggest_fact_check_sources(content, language)
        
        return result
    
    def _verify_url(self, url: str, language: str, result: Dict) -> Dict[str, Any]:
        """Verify URL content and source credibility."""
        analysis_details = result['analysis_details']
        
        # Validate URL format
        if not validators.url(url):
            result['result'] = 'false'
            result['confidence_score'] = 0.9
            result['educational_tip'] = "Invalid URL format detected."
            return result
        
        # Extract domain and assess credibility
        domain = urlparse(url).netloc.lower()
        source_credibility = self._assess_source_credibility(url)
        analysis_details['source_credibility'] = source_credibility
        analysis_details['domain'] = domain
        
        # Try to fetch and analyze content
        try:
            headers = {'User-Agent': self.user_agent.random}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Extract text content
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                text_content = soup.get_text()
                
                # Verify the extracted text
                text_result = self._verify_text(text_content[:2000], language, result)  # Limit to first 2000 chars
                
                # Override source credibility from URL analysis
                text_result['analysis_details']['url_source_credibility'] = source_credibility
                text_result['analysis_details']['webpage_title'] = soup.title.string if soup.title else "No title"
                
                return text_result
            else:
                analysis_details['fetch_error'] = f"HTTP {response.status_code}"
                
        except Exception as e:
            analysis_details['fetch_error'] = str(e)
        
        # Fallback to URL-only analysis
        if source_credibility > 0.8:
            result['result'] = 'verified'
            result['confidence_score'] = source_credibility
        elif source_credibility > 0.5:
            result['result'] = 'questionable'
            result['confidence_score'] = 0.6
        else:
            result['result'] = 'false'
            result['confidence_score'] = 0.8
        
        result['educational_tip'] = f"Source credibility score: {source_credibility:.2f}. Always check multiple sources."
        
        return result
    
    def _verify_image_text(self, image_text: str, language: str, result: Dict) -> Dict[str, Any]:
        """Verify text extracted from images."""
        if not image_text or len(image_text.strip()) < 10:
            result['result'] = 'questionable'
            result['confidence_score'] = 0.5
            result['educational_tip'] = "Insufficient text content to verify. Be cautious with image-based claims."
            return result
        
        # Verify extracted text
        return self._verify_text(image_text, language, result)
    
    def _detect_misinformation_patterns(self, content: str, language: str) -> List[Dict]:
        """Detect known misinformation patterns in content."""
        indicators = []
        content_lower = content.lower()
        
        # Check urgency keywords
        urgency_matches = []
        for keyword in self.misinformation_patterns['urgency_keywords']:
            if keyword in content_lower:
                urgency_matches.append(keyword)
        
        if urgency_matches:
            indicators.append({
                'type': 'urgency_language',
                'description': 'Contains urgency-inducing language',
                'matches': urgency_matches,
                'severity': min(len(urgency_matches) / 3, 1.0)
            })
        
        # Check emotional manipulation
        emotional_matches = []
        for phrase in self.misinformation_patterns['emotional_manipulation']:
            if phrase in content_lower:
                emotional_matches.append(phrase)
        
        if emotional_matches:
            indicators.append({
                'type': 'emotional_manipulation',
                'description': 'Contains emotionally manipulative language',
                'matches': emotional_matches,
                'severity': min(len(emotional_matches) / 2, 1.0)
            })
        
        # Check false medical claims
        medical_matches = []
        for phrase in self.misinformation_patterns['false_medical_claims']:
            if phrase in content_lower:
                medical_matches.append(phrase)
        
        if medical_matches:
            indicators.append({
                'type': 'false_medical_claims',
                'description': 'Contains potentially false medical claims',
                'matches': medical_matches,
                'severity': 0.9  # High severity for medical misinformation
            })
        
        # Check political manipulation
        political_matches = []
        for phrase in self.misinformation_patterns['political_manipulation']:
            if phrase in content_lower:
                political_matches.append(phrase)
        
        if political_matches:
            indicators.append({
                'type': 'political_manipulation',
                'description': 'Contains political manipulation indicators',
                'matches': political_matches,
                'severity': 0.7
            })
        
        return indicators
    
    def _calculate_urgency_score(self, content: str) -> float:
        """Calculate urgency score based on content features."""
        if self.urgency_detector:
            try:
                features = self._extract_urgency_features(content)
                urgency_prob = self.urgency_detector.predict_proba([features])[0][1]
                return urgency_prob
            except:
                pass
        
        # Fallback to rule-based scoring
        urgency_indicators = [
            content.count('!') / len(content.split()),  # Exclamation density
            content.count('URGENT') + content.count('BREAKING'),  # Urgent keywords
            sum(1 for word in content.split() if word.isupper()) / len(content.split()),  # Caps ratio
        ]
        
        return min(sum(urgency_indicators) / 3, 1.0)
    
    def _detect_emotional_manipulation(self, content: str) -> float:
        """Detect emotional manipulation tactics."""
        content_lower = content.lower()
        
        # Emotional trigger words
        trigger_words = [
            'shocking', 'unbelievable', 'amazing', 'incredible', 'outrageous',
            'disgusting', 'terrifying', 'horrifying', 'devastating', 'heartbreaking'
        ]
        
        trigger_count = sum(1 for word in trigger_words if word in content_lower)
        
        # Superlative density
        superlatives = ['most', 'best', 'worst', 'greatest', 'terrible', 'amazing', 'incredible']
        superlative_count = sum(1 for word in superlatives if word in content_lower)
        
        # Calculate emotional manipulation score
        total_words = len(content.split())
        emotional_density = (trigger_count + superlative_count) / total_words if total_words > 0 else 0
        
        return min(emotional_density * 5, 1.0)  # Scale and cap at 1.0
    
    def _detect_logical_fallacies(self, content: str) -> List[Dict]:
        """Detect logical fallacies in content."""
        fallacies = []
        content_lower = content.lower()
        
        # Ad hominem attacks
        ad_hominem_patterns = [
            'stupid', 'idiot', 'moron', 'corrupt', 'evil', 'criminal'
        ]
        
        if any(pattern in content_lower for pattern in ad_hominem_patterns):
            fallacies.append({
                'type': 'ad_hominem',
                'description': 'Contains personal attacks instead of addressing arguments'
            })
        
        # False dichotomy
        dichotomy_patterns = [
            'either you', 'only two', 'you must choose', 'no other option'
        ]
        
        if any(pattern in content_lower for pattern in dichotomy_patterns):
            fallacies.append({
                'type': 'false_dichotomy',
                'description': 'Presents only two options when more exist'
            })
        
        # Appeal to fear
        fear_patterns = [
            "if you don't", 'will destroy', 'end of', 'dangerous', 'threat to'
        ]
        
        if any(pattern in content_lower for pattern in fear_patterns):
            fallacies.append({
                'type': 'appeal_to_fear',
                'description': 'Uses fear to persuade rather than logic'
            })
        
        return fallacies
    
    def _assess_source_credibility(self, url: str) -> float:
        """Assess the credibility of a source URL."""
        try:
            domain = urlparse(url).netloc.lower()
            
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Check known sources
            if domain in self.credible_sources:
                return self.credible_sources[domain]
            
            # Check for subdomains of known sources
            for known_domain, score in self.credible_sources.items():
                if domain.endswith(known_domain):
                    return score * 0.9  # Slightly lower for subdomains
            
            # Rule-based assessment for unknown sources
            credibility_score = 0.5  # Neutral starting point
            
            # Government domains
            if domain.endswith('.gov') or domain.endswith('.gov.in'):
                credibility_score = 0.95
            
            # Educational domains
            elif domain.endswith('.edu') or domain.endswith('.ac.in'):
                credibility_score = 0.90
            
            # Organization domains
            elif domain.endswith('.org'):
                credibility_score = 0.75
            
            # Commercial domains with red flags
            elif any(flag in domain for flag in ['fake', 'news', 'viral', 'click']):
                credibility_score = 0.2
            
            # Very new or suspicious patterns
            elif any(char.isdigit() for char in domain) or domain.count('-') > 2:
                credibility_score = 0.3
            
            return credibility_score
            
        except Exception as e:
            logger.error(f"Error assessing source credibility: {e}")
            return 0.5
    
    def _suggest_fact_check_sources(self, content: str, language: str) -> List[Dict]:
        """Suggest fact-checking sources based on content."""
        sources = []
        
        # General fact-checking sites
        sources.extend([
            {
                'name': 'Snopes',
                'url': 'https://www.snopes.com',
                'description': 'Comprehensive fact-checking database'
            },
            {
                'name': 'FactCheck.org',
                'url': 'https://www.factcheck.org',
                'description': 'Nonpartisan fact-checking site'
            }
        ])
        
        # Indian fact-checking sites
        if language in ['hi', 'en']:
            sources.extend([
                {
                    'name': 'Boom Live',
                    'url': 'https://www.boomlive.in',
                    'description': 'Indian fact-checking organization'
                },
                {
                    'name': 'Alt News',
                    'url': 'https://www.altnews.in',
                    'description': 'Fact-checking platform for India'
                },
                {
                    'name': 'Vishvas News',
                    'url': 'https://www.vishvasnews.com',
                    'description': 'Multilingual fact-checking in India'
                }
            ])
        
        # Medical fact-checking
        if any(keyword in content.lower() for keyword in ['health', 'medicine', 'cure', 'treatment', 'vaccine']):
            sources.extend([
                {
                    'name': 'WHO Fact Sheets',
                    'url': 'https://www.who.int/news-room/fact-sheets',
                    'description': 'World Health Organization fact sheets'
                },
                {
                    'name': 'CDC Information',
                    'url': 'https://www.cdc.gov',
                    'description': 'Centers for Disease Control and Prevention'
                }
            ])
        
        return sources[:5]  # Return top 5 sources

    def get_verification_statistics(self) -> Dict[str, Any]:
        """Get engine performance statistics."""
        return {
            'models_loaded': {
                'text_classifier': self.text_classifier is not None,
                'source_credibility_model': self.source_credibility_model is not None,
                'urgency_detector': self.urgency_detector is not None
            },
            'known_sources': len(self.credible_sources),
            'misinformation_patterns': sum(len(patterns) for patterns in self.misinformation_patterns.values()),
            'supported_languages': ['en', 'hi', 'ta', 'bn', 'mr', 'auto-detect']
        }
