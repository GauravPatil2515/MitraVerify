"""
MitraVerify Text Analyzer
Advanced text analysis utilities for misinformation detection

This module provides comprehensive text analysis capabilities including
sentiment analysis, language detection, readability scoring, and
pattern recognition for identifying potential misinformation.
"""

import logging
import re
import string
from typing import Dict, List, Any, Tuple, Optional
from collections import Counter
from datetime import datetime

import numpy as np
import spacy
import nltk
from textblob import TextBlob
from langdetect import detect, DetectorFactory
from sklearn.feature_extraction.text import TfidfVectorizer
import validators

# Set seed for consistent language detection
DetectorFactory.seed = 0

# Download required NLTK data
try:
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.tag import pos_tag
    from nltk.chunk import ne_chunk
    from nltk.sentiment import SentimentIntensityAnalyzer
except LookupError:
    import nltk
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')
    nltk.download('vader_lexicon')

logger = logging.getLogger(__name__)

class TextAnalyzer:
    """
    Comprehensive text analyzer for detecting misinformation patterns,
    analyzing sentiment, and extracting linguistic features.
    """
    
    def __init__(self):
        """Initialize the text analyzer with NLP models and resources."""
        # Load spaCy models for different languages
        self.nlp_models = {}
        try:
            self.nlp_models['en'] = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("English spaCy model not found. Install with: python -m spacy download en_core_web_sm")
        
        # Initialize NLTK sentiment analyzer
        try:
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
        except Exception as e:
            logger.warning(f"NLTK sentiment analyzer not available: {e}")
            self.sentiment_analyzer = None
        
        # Load stopwords for different languages
        self.stopwords = {
            'en': set(stopwords.words('english')),
            'hi': set(['और', 'या', 'हो', 'को', 'की', 'के', 'में', 'से', 'पर', 'का', 'है', 'था', 'थी', 'हैं']),
            'ta': set(['அந்த', 'இந்த', 'அது', 'இது', 'அவர்', 'அவள்', 'நான்', 'நீ', 'நாம்', 'நீங்கள்']),
            'bn': set(['এই', 'সেই', 'তার', 'তাদের', 'আমার', 'আমাদের', 'তুমি', 'তোমার', 'আমি', 'আমরা']),
            'mr': set(['आणि', 'किंवा', 'होते', 'आहे', 'होता', 'या', 'ते', 'तो', 'ती', 'हे'])
        }
        
        # Misinformation linguistic patterns
        self.misinformation_patterns = self._load_misinformation_patterns()
        
        # Credibility indicators
        self.credibility_indicators = self._load_credibility_indicators()
        
        logger.info("TextAnalyzer initialized successfully")
    
    def _load_misinformation_patterns(self) -> Dict[str, List[str]]:
        """Load patterns commonly found in misinformation."""
        return {
            'urgency_markers': [
                r'\b(urgent|emergency|alert|warning|immediate|critical)\b',
                r'\b(breaking|exclusive|leaked|secret|hidden)\b',
                r'\b(shocking|unbelievable|amazing|incredible)\b',
                r'\b(तुरंत|आपातकाल|चेतावनी|गुप्त|छुपा)\b',
                r'\b(উদনডি|অপায়|গুরুত্বপূর্ণ|গোপন)\b'
            ],
            
            'emotional_manipulation': [
                r'\b(will shock you|you won\'t believe|doctors hate)\b',
                r'\b(they don\'t want you to know|conspiracy|cover.*up)\b',
                r'\b(suppressed|banned|censored|forbidden)\b',
                r'\b(आपको चौंका देगा|सरकार नहीं चाहती|छुपाया गया)\b',
                r'\b(সরকার চায় না|লুকানো|নিষিদ্ধ)\b'
            ],
            
            'false_authority': [
                r'\b(scientists discovered|experts revealed|doctors found)\b',
                r'\b(study shows|research proves|data confirms)\b',
                r'\b(according to sources|insider information|leaked document)\b',
                r'\b(वैज्ञानिकों ने खोजा|डॉक्टरों ने पाया|अध्ययन से पता चला)\b'
            ],
            
            'absolute_claims': [
                r'\b(always|never|all|none|everyone|no one|100%|completely)\b',
                r'\b(absolutely|definitely|certainly|guaranteed|proven)\b',
                r'\b(हमेशा|कभी नहीं|सभी|कोई नहीं|पूरी तरह)\b'
            ],
            
            'fear_inducing': [
                r'\b(dangerous|deadly|harmful|toxic|poisonous|fatal)\b',
                r'\b(will kill|will die|death|destruction|disaster)\b',
                r'\b(threat|risk|danger|hazard|peril)\b',
                r'\b(खतरनाक|जहरीला|मौत|मृत्यु|विनाश)\b'
            ]
        }
    
    def _load_credibility_indicators(self) -> Dict[str, List[str]]:
        """Load patterns that indicate credible content."""
        return {
            'uncertainty_markers': [
                r'\b(may|might|could|possibly|perhaps|likely)\b',
                r'\b(according to|suggests|indicates|appears)\b',
                r'\b(preliminary|initial|early results)\b'
            ],
            
            'source_attribution': [
                r'\b(study published in|journal|research from)\b',
                r'\b(university|institute|organization)\b',
                r'\b(official statement|press release|announcement)\b'
            ],
            
            'factual_language': [
                r'\b(data shows|statistics indicate|evidence suggests)\b',
                r'\b(peer-reviewed|published|documented)\b',
                r'\b(methodology|sample size|participants)\b'
            ]
        }
    
    def analyze_text(self, text: str, language: str = 'auto') -> Dict[str, Any]:
        """
        Perform comprehensive text analysis for misinformation detection.
        
        Args:
            text: The text to analyze
            language: Language code ('auto' for auto-detection)
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Detect language if auto
            if language == 'auto':
                language = self._detect_language(text)
            
            analysis_result = {
                'language': language,
                'text_length': len(text),
                'word_count': len(text.split()),
                'sentence_count': len(sent_tokenize(text)),
                'timestamp': datetime.now().isoformat()
            }
            
            # Basic linguistic analysis
            analysis_result.update(self._analyze_linguistic_features(text, language))
            
            # Sentiment analysis
            analysis_result['sentiment'] = self._analyze_sentiment(text, language)
            
            # Misinformation pattern detection
            analysis_result['misinformation_patterns'] = self._detect_misinformation_patterns(text, language)
            
            # Credibility indicators
            analysis_result['credibility_indicators'] = self._detect_credibility_indicators(text, language)
            
            # Readability analysis
            analysis_result['readability'] = self._analyze_readability(text, language)
            
            # Named entity recognition
            analysis_result['entities'] = self._extract_entities(text, language)
            
            # URL and contact extraction
            analysis_result['urls'] = self._extract_urls(text)
            analysis_result['contact_info'] = self._extract_contact_info(text)
            
            # Writing style analysis
            analysis_result['writing_style'] = self._analyze_writing_style(text, language)
            
            # Calculate overall credibility score
            analysis_result['credibility_score'] = self._calculate_credibility_score(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in text analysis: {e}")
            return {
                'error': str(e),
                'language': language,
                'text_length': len(text),
                'credibility_score': 0.5  # Neutral score on error
            }
    
    def _detect_language(self, text: str) -> str:
        """Detect the language of the text."""
        try:
            # Remove URLs and special characters for better detection
            clean_text = re.sub(r'http\S+|www\S+|[^\w\s]', ' ', text)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            
            if len(clean_text) < 10:
                return 'en'  # Default to English for short texts
            
            detected_lang = detect(clean_text)
            
            # Map some common detections to our supported languages
            lang_mapping = {
                'hi': 'hi',  # Hindi
                'en': 'en',  # English
                'ta': 'ta',  # Tamil
                'bn': 'bn',  # Bengali
                'mr': 'mr',  # Marathi
                'te': 'te',  # Telugu
                'gu': 'gu',  # Gujarati
                'kn': 'kn',  # Kannada
                'ml': 'ml',  # Malayalam
                'pa': 'pa',  # Punjabi
            }
            
            return lang_mapping.get(detected_lang, 'en')
            
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return 'en'
    
    def _analyze_linguistic_features(self, text: str, language: str) -> Dict[str, Any]:
        """Analyze basic linguistic features of the text."""
        words = text.split()
        sentences = sent_tokenize(text)
        
        features = {
            'avg_word_length': np.mean([len(word) for word in words]) if words else 0,
            'avg_sentence_length': np.mean([len(sent.split()) for sent in sentences]) if sentences else 0,
            'punctuation_density': sum(1 for char in text if char in string.punctuation) / len(text) if text else 0,
            'capitalization_ratio': sum(1 for char in text if char.isupper()) / len(text) if text else 0,
            'exclamation_density': text.count('!') / len(words) if words else 0,
            'question_density': text.count('?') / len(words) if words else 0,
        }
        
        # Language-specific features
        if language in self.stopwords:
            stopwords_set = self.stopwords[language]
            stopword_count = sum(1 for word in words if word.lower() in stopwords_set)
            features['stopword_ratio'] = stopword_count / len(words) if words else 0
        else:
            features['stopword_ratio'] = 0
        
        # Repetition analysis
        word_counts = Counter(word.lower() for word in words)
        features['word_repetition_score'] = sum(count - 1 for count in word_counts.values()) / len(words) if words else 0
        
        # All caps words
        all_caps_words = sum(1 for word in words if word.isupper() and len(word) > 1)
        features['all_caps_ratio'] = all_caps_words / len(words) if words else 0
        
        return features
    
    def _analyze_sentiment(self, text: str, language: str) -> Dict[str, Any]:
        """Analyze sentiment and emotional content."""
        sentiment_result = {
            'polarity': 0.0,
            'subjectivity': 0.0,
            'emotional_intensity': 0.0,
            'emotion_distribution': {}
        }
        
        try:
            # Use TextBlob for basic sentiment (works best with English)
            if language == 'en':
                blob = TextBlob(text)
                sentiment_result['polarity'] = blob.sentiment.polarity
                sentiment_result['subjectivity'] = blob.sentiment.subjectivity
            
            # Use VADER sentiment analyzer if available
            if self.sentiment_analyzer and language == 'en':
                vader_scores = self.sentiment_analyzer.polarity_scores(text)
                sentiment_result['vader_scores'] = vader_scores
                sentiment_result['emotional_intensity'] = vader_scores['compound']
            
            # Emotion word analysis
            emotion_words = self._count_emotion_words(text, language)
            sentiment_result['emotion_distribution'] = emotion_words
            
            # Calculate overall emotional intensity
            total_emotions = sum(emotion_words.values())
            text_length = len(text.split())
            sentiment_result['emotion_density'] = total_emotions / text_length if text_length > 0 else 0
            
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {e}")
        
        return sentiment_result
    
    def _count_emotion_words(self, text: str, language: str) -> Dict[str, int]:
        """Count emotional words in different categories."""
        emotion_lexicons = {
            'en': {
                'anger': ['angry', 'furious', 'rage', 'mad', 'irritated', 'annoyed', 'outraged'],
                'fear': ['afraid', 'scared', 'terrified', 'worried', 'anxious', 'panic', 'frightened'],
                'joy': ['happy', 'glad', 'delighted', 'pleased', 'excited', 'thrilled', 'cheerful'],
                'sadness': ['sad', 'depressed', 'miserable', 'unhappy', 'grief', 'sorrow', 'heartbroken'],
                'disgust': ['disgusted', 'revolted', 'sickened', 'appalled', 'repulsed', 'nauseated'],
                'surprise': ['surprised', 'amazed', 'astonished', 'shocked', 'stunned', 'bewildered']
            },
            'hi': {
                'anger': ['गुस्सा', 'क्रोध', 'नाराज़', 'चिढ़', 'गुस्से'],
                'fear': ['डर', 'भय', 'चिंता', 'घबराहट', 'आतंक'],
                'joy': ['खुश', 'प्रसन्न', 'आनंद', 'हर्ष', 'उत्साह'],
                'sadness': ['दुख', 'उदास', 'गम', 'शोक', 'निराश'],
                'disgust': ['घृणा', 'नफरत', 'अरुचि', 'जुगुप्सा'],
                'surprise': ['आश्चर्य', 'हैरान', 'चौंक', 'विस्मय']
            }
        }
        
        text_lower = text.lower()
        emotion_counts = {}
        
        if language in emotion_lexicons:
            for emotion, words in emotion_lexicons[language].items():
                count = sum(1 for word in words if word in text_lower)
                emotion_counts[emotion] = count
        
        return emotion_counts
    
    def _detect_misinformation_patterns(self, text: str, language: str) -> Dict[str, Any]:
        """Detect patterns commonly associated with misinformation."""
        pattern_matches = {
            'urgency_markers': 0,
            'emotional_manipulation': 0,
            'false_authority': 0,
            'absolute_claims': 0,
            'fear_inducing': 0,
            'specific_matches': []
        }
        
        text_lower = text.lower()
        
        for pattern_type, patterns in self.misinformation_patterns.items():
            matches = []
            for pattern in patterns:
                found_matches = re.findall(pattern, text_lower, re.IGNORECASE)
                if found_matches:
                    matches.extend(found_matches)
                    pattern_matches[pattern_type] += len(found_matches)
            
            if matches:
                pattern_matches['specific_matches'].append({
                    'pattern_type': pattern_type,
                    'matches': matches,
                    'count': len(matches)
                })
        
        # Calculate overall pattern intensity
        total_patterns = sum(pattern_matches[key] for key in pattern_matches if isinstance(pattern_matches[key], int))
        text_length = len(text.split())
        pattern_matches['pattern_density'] = total_patterns / text_length if text_length > 0 else 0
        pattern_matches['total_pattern_score'] = total_patterns
        
        return pattern_matches
    
    def _detect_credibility_indicators(self, text: str, language: str) -> Dict[str, Any]:
        """Detect patterns that indicate credible content."""
        credibility_matches = {
            'uncertainty_markers': 0,
            'source_attribution': 0,
            'factual_language': 0,
            'specific_matches': []
        }
        
        text_lower = text.lower()
        
        for indicator_type, patterns in self.credibility_indicators.items():
            matches = []
            for pattern in patterns:
                found_matches = re.findall(pattern, text_lower, re.IGNORECASE)
                if found_matches:
                    matches.extend(found_matches)
                    credibility_matches[indicator_type] += len(found_matches)
            
            if matches:
                credibility_matches['specific_matches'].append({
                    'indicator_type': indicator_type,
                    'matches': matches,
                    'count': len(matches)
                })
        
        # Calculate credibility score
        total_indicators = sum(credibility_matches[key] for key in credibility_matches if isinstance(credibility_matches[key], int))
        text_length = len(text.split())
        credibility_matches['credibility_density'] = total_indicators / text_length if text_length > 0 else 0
        credibility_matches['total_credibility_score'] = total_indicators
        
        return credibility_matches
    
    def _analyze_readability(self, text: str, language: str) -> Dict[str, Any]:
        """Analyze text readability and complexity."""
        if not text:
            return {'error': 'Empty text'}
        
        sentences = sent_tokenize(text)
        words = text.split()
        
        if not sentences or not words:
            return {'error': 'No sentences or words found'}
        
        # Basic readability metrics
        avg_sentence_length = len(words) / len(sentences)
        
        # Count syllables (approximation for non-English)
        syllable_count = self._count_syllables(text, language)
        avg_syllables_per_word = syllable_count / len(words) if words else 0
        
        # Flesch Reading Ease (approximation)
        if avg_sentence_length > 0 and avg_syllables_per_word > 0:
            flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
            flesch_score = max(0, min(100, flesch_score))  # Clamp between 0-100
        else:
            flesch_score = 50  # Neutral score
        
        # Reading level classification
        if flesch_score >= 90:
            reading_level = 'very_easy'
        elif flesch_score >= 80:
            reading_level = 'easy'
        elif flesch_score >= 70:
            reading_level = 'fairly_easy'
        elif flesch_score >= 60:
            reading_level = 'standard'
        elif flesch_score >= 50:
            reading_level = 'fairly_difficult'
        elif flesch_score >= 30:
            reading_level = 'difficult'
        else:
            reading_level = 'very_difficult'
        
        return {
            'flesch_score': flesch_score,
            'reading_level': reading_level,
            'avg_sentence_length': avg_sentence_length,
            'avg_syllables_per_word': avg_syllables_per_word,
            'total_syllables': syllable_count
        }
    
    def _count_syllables(self, text: str, language: str) -> int:
        """Approximate syllable counting (works best for English)."""
        # Simple syllable counting - count vowel groups
        vowels = 'aeiouAEIOU'
        syllables = 0
        previous_was_vowel = False
        
        for char in text:
            if char in vowels:
                if not previous_was_vowel:
                    syllables += 1
                previous_was_vowel = True
            else:
                previous_was_vowel = False
        
        # Adjust for silent e
        if text.endswith('e') and syllables > 1:
            syllables -= 1
        
        return max(1, syllables) if text.strip() else 0
    
    def _extract_entities(self, text: str, language: str) -> Dict[str, List[str]]:
        """Extract named entities from text."""
        entities = {
            'persons': [],
            'organizations': [],
            'locations': [],
            'dates': [],
            'money': [],
            'other': []
        }
        
        try:
            # Use spaCy if available for the language
            if language in self.nlp_models:
                doc = self.nlp_models[language](text)
                for ent in doc.ents:
                    if ent.label_ in ['PERSON', 'PER']:
                        entities['persons'].append(ent.text)
                    elif ent.label_ in ['ORG', 'ORGANIZATION']:
                        entities['organizations'].append(ent.text)
                    elif ent.label_ in ['GPE', 'LOC', 'LOCATION']:
                        entities['locations'].append(ent.text)
                    elif ent.label_ in ['DATE', 'TIME']:
                        entities['dates'].append(ent.text)
                    elif ent.label_ in ['MONEY', 'QUANTITY']:
                        entities['money'].append(ent.text)
                    else:
                        entities['other'].append(ent.text)
            
            # Fallback to NLTK for English
            elif language == 'en':
                tokens = word_tokenize(text)
                pos_tags = pos_tag(tokens)
                chunks = ne_chunk(pos_tags)
                
                for chunk in chunks:
                    if hasattr(chunk, 'label'):
                        entity_name = ' '.join([token for token, pos in chunk.leaves()])
                        if chunk.label() == 'PERSON':
                            entities['persons'].append(entity_name)
                        elif chunk.label() == 'ORGANIZATION':
                            entities['organizations'].append(entity_name)
                        elif chunk.label() == 'GPE':
                            entities['locations'].append(entity_name)
                        else:
                            entities['other'].append(entity_name)
            
        except Exception as e:
            logger.warning(f"Entity extraction failed: {e}")
        
        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text."""
        url_patterns = [
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            r'\b[a-zA-Z0-9.-]+\.(com|org|net|gov|edu|co|in|info|biz)\b'
        ]
        
        urls = []
        for pattern in url_patterns:
            found_urls = re.findall(pattern, text, re.IGNORECASE)
            urls.extend(found_urls)
        
        # Validate URLs
        valid_urls = []
        for url in urls:
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            if validators.url(url):
                valid_urls.append(url)
        
        return list(set(valid_urls))
    
    def _extract_contact_info(self, text: str) -> Dict[str, List[str]]:
        """Extract contact information from text."""
        contact_info = {
            'emails': [],
            'phones': [],
            'social_handles': []
        }
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        contact_info['emails'] = list(set(emails))
        
        # Phone pattern (various formats)
        phone_patterns = [
            r'\b\d{3}-\d{3}-\d{4}\b',  # 123-456-7890
            r'\b\(\d{3}\)\s*\d{3}-\d{4}\b',  # (123) 456-7890
            r'\b\d{10}\b',  # 1234567890
            r'\+\d{1,3}\s*\d{10}\b'  # +91 1234567890
        ]
        
        phones = []
        for pattern in phone_patterns:
            found_phones = re.findall(pattern, text)
            phones.extend(found_phones)
        contact_info['phones'] = list(set(phones))
        
        # Social media handles
        social_pattern = r'@[A-Za-z0-9_]+\b'
        handles = re.findall(social_pattern, text)
        contact_info['social_handles'] = list(set(handles))
        
        return contact_info
    
    def _analyze_writing_style(self, text: str, language: str) -> Dict[str, Any]:
        """Analyze writing style characteristics."""
        words = text.split()
        sentences = sent_tokenize(text)
        
        style_features = {
            'formality_score': 0.5,  # Default neutral
            'technical_complexity': 0.0,
            'personal_pronouns_ratio': 0.0,
            'passive_voice_ratio': 0.0,
            'conjunction_ratio': 0.0
        }
        
        if not words:
            return style_features
        
        # Personal pronouns (indicates informal/personal style)
        personal_pronouns = {
            'en': ['i', 'me', 'my', 'mine', 'you', 'your', 'yours', 'we', 'us', 'our', 'ours'],
            'hi': ['मैं', 'मुझे', 'मेरा', 'तुम', 'तुम्हारा', 'हम', 'हमारा'],
            'ta': ['நான்', 'என்', 'எங்கள்', 'நீ', 'உன்', 'உங்கள்'],
            'bn': ['আমি', 'আমার', 'তুমি', 'তোমার', 'আমরা', 'আমাদের'],
            'mr': ['मी', 'माझा', 'तू', 'तुझा', 'आम्ही', 'आमचा']
        }
        
        if language in personal_pronouns:
            pronoun_count = sum(1 for word in words if word.lower() in personal_pronouns[language])
            style_features['personal_pronouns_ratio'] = pronoun_count / len(words)
        
        # Technical/complex words (approximation)
        complex_words = sum(1 for word in words if len(word) > 6)
        style_features['technical_complexity'] = complex_words / len(words)
        
        # Formality score (inverse of personal pronouns + technical complexity)
        style_features['formality_score'] = min(1.0, 
            (1 - style_features['personal_pronouns_ratio']) * 0.6 + 
            style_features['technical_complexity'] * 0.4
        )
        
        return style_features
    
    def _calculate_credibility_score(self, analysis_result: Dict[str, Any]) -> float:
        """Calculate overall credibility score based on all analysis factors."""
        try:
            # Initialize score
            credibility_score = 0.5  # Start neutral
            
            # Factor 1: Misinformation patterns (negative impact)
            misinformation = analysis_result.get('misinformation_patterns', {})
            pattern_density = misinformation.get('pattern_density', 0)
            credibility_score -= min(pattern_density * 2, 0.4)  # Max penalty of 0.4
            
            # Factor 2: Credibility indicators (positive impact)
            credibility_indicators = analysis_result.get('credibility_indicators', {})
            credibility_density = credibility_indicators.get('credibility_density', 0)
            credibility_score += min(credibility_density * 2, 0.3)  # Max bonus of 0.3
            
            # Factor 3: Sentiment extremity (negative impact)
            sentiment = analysis_result.get('sentiment', {})
            emotion_density = sentiment.get('emotion_density', 0)
            credibility_score -= min(emotion_density * 0.5, 0.2)  # Max penalty of 0.2
            
            # Factor 4: Writing style (formal = more credible)
            writing_style = analysis_result.get('writing_style', {})
            formality_score = writing_style.get('formality_score', 0.5)
            credibility_score += (formality_score - 0.5) * 0.2  # -0.1 to +0.1
            
            # Factor 5: Contact information presence (positive impact)
            contact_info = analysis_result.get('contact_info', {})
            has_contact = any(contact_info.get(key, []) for key in contact_info)
            if has_contact:
                credibility_score += 0.1
            
            # Factor 6: Source URLs presence (positive impact)
            urls = analysis_result.get('urls', [])
            if urls:
                credibility_score += 0.1
            
            # Factor 7: Readability (moderate complexity is good)
            readability = analysis_result.get('readability', {})
            flesch_score = readability.get('flesch_score', 50)
            # Optimal range is 30-70 (not too simple, not too complex)
            if 30 <= flesch_score <= 70:
                credibility_score += 0.1
            
            # Ensure score is between 0 and 1
            credibility_score = max(0.0, min(1.0, credibility_score))
            
            return round(credibility_score, 3)
            
        except Exception as e:
            logger.error(f"Error calculating credibility score: {e}")
            return 0.5  # Return neutral score on error
    
    def get_text_summary(self, text: str, max_sentences: int = 3) -> str:
        """Generate a summary of the text."""
        try:
            sentences = sent_tokenize(text)
            
            if len(sentences) <= max_sentences:
                return text
            
            # Simple extractive summarization using sentence position and length
            sentence_scores = []
            for i, sentence in enumerate(sentences):
                score = 0
                
                # Position weight (beginning and end are important)
                if i < len(sentences) * 0.3:
                    score += 0.3
                elif i > len(sentences) * 0.7:
                    score += 0.2
                
                # Length weight (moderate length preferred)
                word_count = len(sentence.split())
                if 10 <= word_count <= 30:
                    score += 0.2
                
                sentence_scores.append((score, i, sentence))
            
            # Select top sentences
            sentence_scores.sort(reverse=True)
            selected_sentences = sorted(
                sentence_scores[:max_sentences], 
                key=lambda x: x[1]
            )  # Sort by original order
            
            summary = ' '.join([sentence[2] for sentence in selected_sentences])
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return text[:500] + "..." if len(text) > 500 else text
    
    def compare_texts(self, text1: str, text2: str) -> Dict[str, Any]:
        """Compare two texts for similarity and differences."""
        try:
            # Analyze both texts
            analysis1 = self.analyze_text(text1)
            analysis2 = self.analyze_text(text2)
            
            # Calculate similarity scores
            similarity_result = {
                'overall_similarity': 0.0,
                'sentiment_similarity': 0.0,
                'style_similarity': 0.0,
                'content_similarity': 0.0,
                'differences': []
            }
            
            # Content similarity using simple word overlap
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            if words1 or words2:
                content_similarity = len(words1 & words2) / len(words1 | words2)
                similarity_result['content_similarity'] = content_similarity
            
            # Sentiment similarity
            sent1 = analysis1.get('sentiment', {})
            sent2 = analysis2.get('sentiment', {})
            
            pol1 = sent1.get('polarity', 0)
            pol2 = sent2.get('polarity', 0)
            sentiment_similarity = 1 - abs(pol1 - pol2) / 2  # Normalize to 0-1
            similarity_result['sentiment_similarity'] = sentiment_similarity
            
            # Style similarity
            style1 = analysis1.get('writing_style', {})
            style2 = analysis2.get('writing_style', {})
            
            formality_diff = abs(style1.get('formality_score', 0.5) - style2.get('formality_score', 0.5))
            style_similarity = 1 - formality_diff
            similarity_result['style_similarity'] = style_similarity
            
            # Overall similarity
            similarity_result['overall_similarity'] = (
                content_similarity * 0.5 + 
                sentiment_similarity * 0.3 + 
                style_similarity * 0.2
            )
            
            # Identify key differences
            if analysis1.get('credibility_score', 0.5) != analysis2.get('credibility_score', 0.5):
                similarity_result['differences'].append({
                    'type': 'credibility',
                    'description': 'Different credibility scores detected'
                })
            
            return similarity_result
            
        except Exception as e:
            logger.error(f"Error comparing texts: {e}")
            return {'error': str(e)}
    
    def get_analyzer_stats(self) -> Dict[str, Any]:
        """Get statistics about the analyzer's capabilities."""
        return {
            'supported_languages': list(self.stopwords.keys()),
            'nlp_models_loaded': list(self.nlp_models.keys()),
            'misinformation_patterns': len(sum(self.misinformation_patterns.values(), [])),
            'credibility_indicators': len(sum(self.credibility_indicators.values(), [])),
            'sentiment_analyzer_available': self.sentiment_analyzer is not None,
            'features': [
                'Language detection',
                'Sentiment analysis',
                'Readability scoring',
                'Named entity recognition',
                'Pattern detection',
                'Writing style analysis',
                'URL extraction',
                'Contact information extraction'
            ]
        }
