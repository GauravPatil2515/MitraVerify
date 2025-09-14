"""
MitraVerify Cultural Context Analyzer
Cultural and regional context analysis for Indian misinformation patterns

This module provides specialized analysis for understanding misinformation
in the Indian context, including regional patterns, linguistic nuances,
and cultural sensitivities specific to Indian social media and communication.
"""

import logging
import re
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import json

import numpy as np
from langdetect import detect

logger = logging.getLogger(__name__)

class CulturalContextAnalyzer:
    """
    Specialized analyzer for Indian cultural context and misinformation patterns.
    Provides insights into regional, linguistic, and cultural factors that
    influence misinformation spread in India.
    """
    
    def __init__(self):
        """Initialize the cultural context analyzer with Indian-specific data."""
        # Regional misinformation patterns
        self.regional_patterns = self._load_regional_patterns()
        
        # Religious and communal sensitivity indicators
        self.sensitivity_indicators = self._load_sensitivity_indicators()
        
        # Indian social media culture patterns
        self.social_media_patterns = self._load_social_media_patterns()
        
        # Festival and event-based misinformation
        self.seasonal_patterns = self._load_seasonal_patterns()
        
        # Language-specific patterns
        self.language_patterns = self._load_language_patterns()
        
        # Political context indicators
        self.political_indicators = self._load_political_indicators()
        
        # Economic misinformation patterns
        self.economic_patterns = self._load_economic_patterns()
        
        logger.info("CulturalContextAnalyzer initialized successfully")
    
    def _load_regional_patterns(self) -> Dict[str, Dict]:
        """Load region-specific misinformation patterns."""
        return {
            'north_india': {
                'common_themes': [
                    'political_manipulation', 'religious_tensions', 'agricultural_rumors',
                    'government_scheme_misinformation', 'covid_misinformation'
                ],
                'keywords': [
                    'सरकारी योजना', 'किसान', 'धर्म', 'राजनीति', 'मोदी', 'राहुल',
                    'government scheme', 'farmer', 'religion', 'politics'
                ],
                'platforms': ['whatsapp', 'facebook', 'twitter', 'youtube'],
                'vulnerability_factors': ['rural_population', 'low_digital_literacy', 'language_barriers']
            },
            
            'south_india': {
                'common_themes': [
                    'language_politics', 'regional_autonomy', 'dravidian_politics',
                    'tamil_nationalism', 'karnataka_water_disputes'
                ],
                'keywords': [
                    'தமிழ்', 'కన్నడ', 'മലയാളം', 'తెలుగు', 'hindi_imposition',
                    'cauvery', 'water_sharing', 'regional_parties'
                ],
                'platforms': ['whatsapp', 'facebook', 'instagram', 'telegram'],
                'vulnerability_factors': ['language_pride', 'regional_identity', 'political_polarization']
            },
            
            'west_india': {
                'common_themes': [
                    'business_rumors', 'stock_market_manipulation', 'real_estate_fraud',
                    'bollywood_gossip', 'mumbai_specific_issues'
                ],
                'keywords': [
                    'शेयर बाजार', 'रियल एस्टेट', 'बॉलीवूड', 'मुंबई', 'गुजरात',
                    'share market', 'real estate', 'bollywood', 'mumbai', 'gujarat'
                ],
                'platforms': ['whatsapp', 'linkedin', 'twitter', 'instagram'],
                'vulnerability_factors': ['business_community', 'financial_anxiety', 'urban_rumors']
            },
            
            'east_india': {
                'common_themes': [
                    'bengali_culture', 'intellectual_debates', 'political_violence',
                    'cultural_superiority', 'fish_rice_culture'
                ],
                'keywords': [
                    'বাঙালি', 'পশ্চিমবঙ্গ', 'কলকাতা', 'তৃণমূল', 'সিপিএম',
                    'bengali', 'west_bengal', 'kolkata', 'trinamool', 'cpim'
                ],
                'platforms': ['facebook', 'whatsapp', 'twitter', 'youtube'],
                'vulnerability_factors': ['political_violence', 'cultural_identity', 'economic_migration']
            },
            
            'northeast_india': {
                'common_themes': [
                    'ethnic_tensions', 'immigration_fears', 'mainland_discrimination',
                    'insurgency_rumors', 'tribal_rights'
                ],
                'keywords': [
                    'northeastern', 'tribal', 'insurgency', 'immigration', 'discrimination',
                    'assam', 'manipur', 'nagaland', 'arunachal'
                ],
                'platforms': ['whatsapp', 'facebook', 'telegram', 'instagram'],
                'vulnerability_factors': ['ethnic_diversity', 'isolation_feeling', 'security_concerns']
            }
        }
    
    def _load_sensitivity_indicators(self) -> Dict[str, List[str]]:
        """Load religious and communal sensitivity indicators."""
        return {
            'religious_keywords': [
                # Hindu-related
                'हिंदू', 'hindu', 'ram', 'राम', 'krishna', 'कृष्ण', 'shiva', 'शिव',
                'temple', 'मंदिर', 'puja', 'पूजा', 'aarti', 'आरती', 'bhajan', 'भजन',
                
                # Muslim-related
                'muslim', 'मुस्लिम', 'islam', 'इस्लाम', 'allah', 'अल्लाह', 'quran', 'कुरान',
                'mosque', 'मस्जिद', 'namaz', 'नमाज', 'jihad', 'जिहाद', 'halal', 'हलाल',
                
                # Christian-related
                'christian', 'ईसाई', 'jesus', 'यीशु', 'church', 'चर्च', 'bible', 'बाइबल',
                'pastor', 'पादरी', 'conversion', 'धर्म परिवर्तन',
                
                # Sikh-related
                'sikh', 'सिख', 'guru', 'गुरु', 'gurdwara', 'गुरुद्वारा', 'khalsa', 'खालसा',
                
                # Buddhist/Jain-related
                'buddhist', 'बौद्ध', 'buddha', 'बुद्ध', 'jain', 'जैन', 'monastery', 'विहार'
            ],
            
            'caste_keywords': [
                'brahmin', 'ब्राह्मण', 'kshatriya', 'क्षत्रिय', 'vaishya', 'वैश्य',
                'shudra', 'शूद्र', 'dalit', 'दलित', 'sc', 'st', 'obc', 'ओबीसी',
                'reservation', 'आरक्षण', 'quota', 'कोटा', 'caste', 'जाति'
            ],
            
            'communal_tension_words': [
                'riot', 'दंगा', 'violence', 'हिंसा', 'attack', 'हमला', 'mob', 'भीड़',
                'lynching', 'lynch', 'मॉब लिंचिंग', 'communal', 'सांप्रदायिक',
                'polarization', 'ध्रुवीकरण', 'hate', 'घृणा', 'bigotry', 'कट्टरता'
            ],
            
            'political_polarization': [
                'modi', 'मोदी', 'rahul', 'राहुल', 'bjp', 'बीजेपी', 'congress', 'कांग्रेस',
                'rss', 'आरएसएस', 'sanghi', 'संघी', 'bhakt', 'भक्त', 'secular', 'धर्मनिरपेक्ष',
                'nationalist', 'राष्ट्रवादी', 'anti_national', 'देशद्रोही'
            ]
        }
    
    def _load_social_media_patterns(self) -> Dict[str, Dict]:
        """Load Indian social media culture patterns."""
        return {
            'whatsapp_forwards': {
                'common_phrases': [
                    'forward as received', 'फॉरवर्ड एज़ रिसीव्ड', 'share maximum',
                    'जल्दी शेयर करें', 'urgent share', 'family group forward',
                    'good morning', 'गुड मॉर्निंग', 'jai shri ram', 'जय श्री राम',
                    'share if you are hindu', 'अगर आप हिंदू हैं तो शेयर करें'
                ],
                'manipulation_tactics': [
                    'emotional_blackmail', 'religious_obligation', 'family_pressure',
                    'nationalism_appeal', 'fear_mongering', 'health_scare'
                ],
                'format_patterns': [
                    'text_with_emojis', 'audio_message', 'video_with_dramatic_music',
                    'image_with_text_overlay', 'multiple_forwards_chain'
                ]
            },
            
            'facebook_patterns': {
                'common_behaviors': [
                    'uncle_aunty_sharing', 'family_group_posts', 'community_page_shares',
                    'political_rants', 'festival_wishes_spam', 'fake_news_believing'
                ],
                'content_types': [
                    'motivational_quotes', 'religious_posts', 'political_memes',
                    'health_misinformation', 'conspiracy_theories', 'fake_schemes'
                ]
            },
            
            'twitter_patterns': {
                'hashtag_manipulation': [
                    'trending_hashtag_hijacking', 'political_hashtag_wars',
                    'manufactured_trends', 'bot_amplification'
                ],
                'content_patterns': [
                    'thread_misinformation', 'selective_quoting', 'context_stripping',
                    'coordinated_campaigns', 'astroturfing'
                ]
            },
            
            'youtube_patterns': {
                'channel_types': [
                    'news_channels', 'conspiracy_channels', 'political_channels',
                    'religious_channels', 'health_gurus', 'financial_advisors'
                ],
                'content_patterns': [
                    'clickbait_thumbnails', 'dramatic_titles', 'fear_based_content',
                    'miracle_cures', 'secret_revelations', 'government_conspiracies'
                ]
            }
        }
    
    def _load_seasonal_patterns(self) -> Dict[str, Dict]:
        """Load festival and seasonal misinformation patterns."""
        return {
            'festivals': {
                'diwali': {
                    'period': ['october', 'november'],
                    'common_misinformation': [
                        'pollution_denial', 'firecracker_health_benefits',
                        'anti_diwali_conspiracy', 'fake_pollution_data'
                    ]
                },
                'holi': {
                    'period': ['march'],
                    'common_misinformation': [
                        'color_safety_myths', 'water_wastage_denial',
                        'chemical_color_benefits', 'festival_origin_myths'
                    ]
                },
                'eid': {
                    'period': ['varies'],
                    'common_misinformation': [
                        'halal_conspiracy', 'meat_health_myths',
                        'religious_conversion_rumors', 'food_safety_lies'
                    ]
                }
            },
            
            'seasons': {
                'monsoon': {
                    'period': ['june', 'july', 'august', 'september'],
                    'common_misinformation': [
                        'weather_modification_conspiracy', 'cloud_seeding_myths',
                        'flood_prediction_hoax', 'government_weather_control'
                    ]
                },
                'election_season': {
                    'period': ['varies'],
                    'common_misinformation': [
                        'evm_hacking', 'voter_fraud', 'candidate_fake_promises',
                        'booth_capturing_videos', 'exit_poll_manipulation'
                    ]
                }
            },
            
            'special_events': {
                'budget_day': {
                    'common_misinformation': [
                        'tax_rumor_spreading', 'scheme_misinterpretation',
                        'economic_data_manipulation', 'market_manipulation_news'
                    ]
                },
                'exam_results': {
                    'common_misinformation': [
                        'result_hacking_claims', 'paper_leak_rumors',
                        'grade_manipulation_stories', 'fake_topper_news'
                    ]
                }
            }
        }
    
    def _load_language_patterns(self) -> Dict[str, Dict]:
        """Load language-specific misinformation patterns."""
        return {
            'hindi': {
                'manipulation_phrases': [
                    'सरकार छुपा रही है', 'डॉक्टर नहीं बताते', 'मीडिया दिखा नहीं रहा',
                    'विदेशी साजिश', 'गुप्त रिपोर्ट', 'बड़ी खबर', 'तुरंत शेयर करें'
                ],
                'authority_claims': [
                    'आयुर्वेद कहता है', 'शास्त्रों में लिखा है', 'ऋषि मुनियों का ज्ञान',
                    'प्राचीन भारतीय विज्ञान', 'वेदों में वर्णित', 'संस्कृति के अनुसार'
                ],
                'emotional_triggers': [
                    'मां-बाप', 'बच्चों का भविष्य', 'धर्म की रक्षा', 'देश का सम्मान',
                    'समाज की भलाई', 'परंपरा का नुकसान'
                ]
            },
            
            'english': {
                'manipulation_phrases': [
                    'mainstream media won\'t tell you', 'doctors don\'t want you to know',
                    'government cover-up', 'foreign conspiracy', 'leaked document',
                    'exclusive report', 'breaking news', 'urgent share'
                ],
                'pseudo_scientific': [
                    'research shows', 'studies prove', 'scientists discovered',
                    'according to experts', 'medical breakthrough', 'natural cure'
                ],
                'nationalist_appeals': [
                    'proud to be indian', 'bharatmata ki jai', 'vande mataram',
                    'indian culture superior', 'western conspiracy', 'cultural invasion'
                ]
            },
            
            'regional_languages': {
                'tamil': {
                    'common_themes': ['dravidian_pride', 'anti_hindi_sentiment', 'tamil_superiority'],
                    'trigger_words': ['தமிழ்', 'திராவிடம்', 'हिंदी थोपना']
                },
                'bengali': {
                    'common_themes': ['intellectual_superiority', 'cultural_pride', 'political_violence'],
                    'trigger_words': ['বাঙালি', 'বুদ্ধিজীবী', 'সংস্কৃতি']
                },
                'marathi': {
                    'common_themes': ['marathi_manoos', 'outsider_resentment', 'regional_pride'],
                    'trigger_words': ['मराठी माणूस', 'परकीय', 'महाराष्ट्र']
                }
            }
        }
    
    def _load_political_indicators(self) -> Dict[str, List[str]]:
        """Load political context indicators."""
        return {
            'pro_government': [
                'development', 'विकास', 'progress', 'प्रगति', 'achhe din', 'अच्छे दिन',
                'digital india', 'डिजिटल इंडिया', 'swachh bharat', 'स्वच्छ भारत',
                'make in india', 'मेक इन इंडिया', 'atmanirbhar', 'आत्मनिर्भर'
            ],
            
            'anti_government': [
                'corruption', 'भ्रष्टाचार', 'unemployment', 'बेरोजगारी', 'inflation', 'महंगाई',
                'farmer_suicide', 'किसान आत्महत्या', 'economic_crisis', 'आर्थिक संकट',
                'authoritarianism', 'तानाशाही', 'democracy_in_danger', 'लोकतंत्र खतरे में'
            ],
            
            'polarizing_terms': [
                'hindu_rashtra', 'हिंदू राष्ट्र', 'secular_mafia', 'सेकुलर माफिया',
                'love_jihad', 'लव जिहाद', 'urban_naxal', 'अर्बन नक्सल',
                'anti_national', 'देशद्रोही', 'bhakt', 'भक्त', 'sanghi', 'संघी'
            ]
        }
    
    def _load_economic_patterns(self) -> Dict[str, List[str]]:
        """Load economic misinformation patterns."""
        return {
            'financial_scams': [
                'get_rich_quick', 'जल्दी अमीर बनें', 'guaranteed_returns', 'गारंटीड रिटर्न',
                'no_risk_investment', 'बिना रिस्क निवेश', 'secret_formula', 'गुप्त फॉर्मूला',
                'limited_time_offer', 'सीमित समय ऑफर'
            ],
            
            'scheme_misinformation': [
                'government_giving_money', 'सरकार पैसे दे रही है', 'free_laptop_scheme', 'फ्री लैपटॉप योजना',
                'gas_subsidy_trick', 'गैस सब्सिडी ट्रिक', 'bank_account_reward', 'बैंक अकाउंट इनाम'
            ],
            
            'market_manipulation': [
                'stock_tip', 'शेयर टिप', 'insider_information', 'इनसाइडर जानकारी',
                'sure_shot_profit', 'पक्का मुनाफा', 'market_crash_prediction', 'मार्केट क्रैश भविष्यवाणी'
            ]
        }
    
    def analyze_cultural_context(self, content: str, language: str = 'auto') -> Dict[str, Any]:
        """
        Analyze cultural context and regional patterns in content.
        
        Args:
            content: The content to analyze
            language: Language of the content
            
        Returns:
            Dictionary containing cultural context analysis
        """
        try:
            # Detect language if auto
            if language == 'auto':
                try:
                    language = detect(content)
                except:
                    language = 'en'
            
            analysis_result = {
                'language': language,
                'cultural_indicators': {},
                'regional_context': {},
                'sensitivity_analysis': {},
                'social_media_patterns': {},
                'temporal_context': {},
                'risk_assessment': {},
                'timestamp': datetime.now().isoformat()
            }
            
            # Analyze cultural indicators
            analysis_result['cultural_indicators'] = self._analyze_cultural_indicators(content, language)
            
            # Regional context analysis
            analysis_result['regional_context'] = self._analyze_regional_context(content, language)
            
            # Religious and communal sensitivity
            analysis_result['sensitivity_analysis'] = self._analyze_sensitivity(content, language)
            
            # Social media pattern detection
            analysis_result['social_media_patterns'] = self._detect_social_media_patterns(content, language)
            
            # Temporal/seasonal context
            analysis_result['temporal_context'] = self._analyze_temporal_context(content)
            
            # Overall risk assessment
            analysis_result['risk_assessment'] = self._assess_cultural_risk(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in cultural context analysis: {e}")
            return {
                'error': str(e),
                'language': language,
                'risk_level': 'unknown'
            }
    
    def _analyze_cultural_indicators(self, content: str, language: str) -> Dict[str, Any]:
        """Analyze cultural and linguistic indicators."""
        content_lower = content.lower()
        
        cultural_indicators = {
            'language_mixing': False,
            'cultural_references': [],
            'traditional_values_appeal': [],
            'modern_vs_traditional_conflict': False,
            'generational_divide_indicators': []
        }
        
        # Detect language mixing (common in Indian content)
        if language == 'hi' or language == 'en':
            # Check for Hindi-English mixing
            hindi_pattern = r'[\u0900-\u097F]+'
            english_pattern = r'[a-zA-Z]+'
            
            has_hindi = bool(re.search(hindi_pattern, content))
            has_english = bool(re.search(english_pattern, content))
            
            if has_hindi and has_english:
                cultural_indicators['language_mixing'] = True
        
        # Cultural reference detection
        cultural_refs = [
            'sanskar', 'संस्कार', 'tradition', 'परंपरा', 'culture', 'संस्कृति',
            'respect_elders', 'बड़ों का सम्मान', 'family_values', 'पारिवारिक मूल्य',
            'indian_way', 'भारतीय तरीका', 'our_culture', 'हमारी संस्कृति'
        ]
        
        found_refs = [ref for ref in cultural_refs if ref in content_lower]
        cultural_indicators['cultural_references'] = found_refs
        
        # Traditional values appeal
        traditional_appeals = [
            'ancient_wisdom', 'प्राचीन ज्ञान', 'vedic_knowledge', 'वैदिक ज्ञान',
            'ayurveda', 'आयुर्वेद', 'yoga', 'योग', 'meditation', 'ध्यान',
            'spiritual', 'आध्यात्मिक', 'dharma', 'धर्म', 'karma', 'कर्म'
        ]
        
        found_appeals = [appeal for appeal in traditional_appeals if appeal in content_lower]
        cultural_indicators['traditional_values_appeal'] = found_appeals
        
        return cultural_indicators
    
    def _analyze_regional_context(self, content: str, language: str) -> Dict[str, Any]:
        """Analyze regional context and patterns."""
        content_lower = content.lower()
        
        regional_context = {
            'likely_regions': [],
            'regional_keywords_found': {},
            'linguistic_patterns': {},
            'regional_issues': []
        }
        
        # Check against regional patterns
        for region, patterns in self.regional_patterns.items():
            keyword_matches = 0
            found_keywords = []
            
            for keyword in patterns['keywords']:
                if keyword.lower() in content_lower:
                    keyword_matches += 1
                    found_keywords.append(keyword)
            
            if keyword_matches > 0:
                regional_context['likely_regions'].append({
                    'region': region,
                    'match_score': keyword_matches / len(patterns['keywords']),
                    'matched_keywords': found_keywords
                })
                regional_context['regional_keywords_found'][region] = found_keywords
        
        # Sort regions by match score
        regional_context['likely_regions'].sort(key=lambda x: x['match_score'], reverse=True)
        
        return regional_context
    
    def _analyze_sensitivity(self, content: str, language: str) -> Dict[str, Any]:
        """Analyze religious and communal sensitivity."""
        content_lower = content.lower()
        
        sensitivity_analysis = {
            'religious_content_detected': False,
            'communal_tension_indicators': [],
            'caste_related_content': False,
            'political_polarization_score': 0.0,
            'sensitivity_level': 'low',
            'potential_triggers': []
        }
        
        # Religious content detection
        religious_matches = 0
        for keyword in self.sensitivity_indicators['religious_keywords']:
            if keyword.lower() in content_lower:
                religious_matches += 1
                sensitivity_analysis['potential_triggers'].append(keyword)
        
        if religious_matches > 0:
            sensitivity_analysis['religious_content_detected'] = True
        
        # Communal tension indicators
        communal_indicators = []
        for keyword in self.sensitivity_indicators['communal_tension_words']:
            if keyword.lower() in content_lower:
                communal_indicators.append(keyword)
        
        sensitivity_analysis['communal_tension_indicators'] = communal_indicators
        
        # Caste-related content
        caste_matches = sum(1 for keyword in self.sensitivity_indicators['caste_keywords'] 
                           if keyword.lower() in content_lower)
        sensitivity_analysis['caste_related_content'] = caste_matches > 0
        
        # Political polarization score
        political_matches = sum(1 for keyword in self.sensitivity_indicators['political_polarization'] 
                               if keyword.lower() in content_lower)
        total_words = len(content.split())
        sensitivity_analysis['political_polarization_score'] = political_matches / total_words if total_words > 0 else 0
        
        # Calculate overall sensitivity level
        total_sensitive_content = religious_matches + len(communal_indicators) + caste_matches + political_matches
        
        if total_sensitive_content == 0:
            sensitivity_analysis['sensitivity_level'] = 'low'
        elif total_sensitive_content <= 2:
            sensitivity_analysis['sensitivity_level'] = 'medium'
        else:
            sensitivity_analysis['sensitivity_level'] = 'high'
        
        return sensitivity_analysis
    
    def _detect_social_media_patterns(self, content: str, language: str) -> Dict[str, Any]:
        """Detect social media specific patterns."""
        content_lower = content.lower()
        
        social_patterns = {
            'platform_indicators': {},
            'sharing_pressure_tactics': [],
            'manipulation_techniques': [],
            'format_patterns': []
        }
        
        # WhatsApp pattern detection
        whatsapp_patterns = self.social_media_patterns['whatsapp_forwards']
        whatsapp_matches = sum(1 for phrase in whatsapp_patterns['common_phrases'] 
                              if phrase.lower() in content_lower)
        
        if whatsapp_matches > 0:
            social_patterns['platform_indicators']['whatsapp'] = whatsapp_matches
            social_patterns['sharing_pressure_tactics'].extend([
                phrase for phrase in whatsapp_patterns['common_phrases'] 
                if phrase.lower() in content_lower
            ])
        
        # Facebook pattern detection
        facebook_patterns = self.social_media_patterns['facebook_patterns']
        facebook_indicators = [
            'tag your friends', 'share this post', 'like if you agree',
            'comment below', 'viral post', 'trending now'
        ]
        
        facebook_matches = sum(1 for indicator in facebook_indicators 
                              if indicator.lower() in content_lower)
        
        if facebook_matches > 0:
            social_patterns['platform_indicators']['facebook'] = facebook_matches
        
        # Manipulation technique detection
        manipulation_techniques = [
            'emotional_blackmail', 'religious_obligation', 'nationalism_appeal',
            'fear_mongering', 'health_scare', 'social_pressure'
        ]
        
        for technique in manipulation_techniques:
            # Check for technique-specific patterns
            if self._check_manipulation_technique(content_lower, technique):
                social_patterns['manipulation_techniques'].append(technique)
        
        return social_patterns
    
    def _check_manipulation_technique(self, content: str, technique: str) -> bool:
        """Check for specific manipulation techniques."""
        technique_patterns = {
            'emotional_blackmail': ['if you love', 'अगर प्यार करते हो', 'prove your love', 'अपना प्यार साबित करो'],
            'religious_obligation': ['dharma says', 'धर्म कहता है', 'god will bless', 'भगवान आशीर्वाद देगा'],
            'nationalism_appeal': ['true indian', 'सच्चा भारतीय', 'patriotic duty', 'देशभक्ति का फर्ज'],
            'fear_mongering': ['dangerous consequences', 'खतरनाक परिणाम', 'your family at risk', 'आपका परिवार खतरे में'],
            'health_scare': ['will cause cancer', 'कैंसर का कारण', 'deadly disease', 'जानलेवा बीमारी'],
            'social_pressure': ['everyone is sharing', 'सभी शेयर कर रहे', 'don\'t be left out', 'पीछे मत रहो']
        }
        
        if technique in technique_patterns:
            return any(pattern in content for pattern in technique_patterns[technique])
        
        return False
    
    def _analyze_temporal_context(self, content: str) -> Dict[str, Any]:
        """Analyze temporal and seasonal context."""
        current_month = datetime.now().strftime('%B').lower()
        
        temporal_context = {
            'current_month': current_month,
            'seasonal_relevance': [],
            'festival_context': [],
            'timing_manipulation': False
        }
        
        # Check seasonal patterns
        for season, data in self.seasonal_patterns['seasons'].items():
            if current_month in data['period']:
                # Check if content matches seasonal misinformation patterns
                content_lower = content.lower()
                matches = sum(1 for pattern in data['common_misinformation'] 
                             if any(word in content_lower for word in pattern.split('_')))
                
                if matches > 0:
                    temporal_context['seasonal_relevance'].append({
                        'season': season,
                        'relevance_score': matches
                    })
        
        # Check festival context
        for festival, data in self.seasonal_patterns['festivals'].items():
            if current_month in data['period']:
                content_lower = content.lower()
                matches = sum(1 for pattern in data['common_misinformation'] 
                             if any(word in content_lower for word in pattern.split('_')))
                
                if matches > 0:
                    temporal_context['festival_context'].append({
                        'festival': festival,
                        'relevance_score': matches
                    })
        
        # Check for timing manipulation indicators
        timing_indicators = [
            'happening now', 'अभी हो रहा है', 'breaking news', 'ताज़ा खबर',
            'urgent update', 'तुरंत अपडेट', 'just happened', 'अभी अभी हुआ'
        ]
        
        content_lower = content.lower()
        temporal_context['timing_manipulation'] = any(indicator in content_lower for indicator in timing_indicators)
        
        return temporal_context
    
    def _assess_cultural_risk(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall cultural and social risk."""
        risk_factors = []
        risk_score = 0.0
        
        # Sensitivity analysis risk
        sensitivity = analysis_result.get('sensitivity_analysis', {})
        sensitivity_level = sensitivity.get('sensitivity_level', 'low')
        
        if sensitivity_level == 'high':
            risk_score += 0.4
            risk_factors.append('High religious/communal sensitivity detected')
        elif sensitivity_level == 'medium':
            risk_score += 0.2
            risk_factors.append('Moderate religious/communal content detected')
        
        # Social media manipulation risk
        social_patterns = analysis_result.get('social_media_patterns', {})
        manipulation_techniques = social_patterns.get('manipulation_techniques', [])
        
        if len(manipulation_techniques) > 2:
            risk_score += 0.3
            risk_factors.append('Multiple manipulation techniques detected')
        elif len(manipulation_techniques) > 0:
            risk_score += 0.15
            risk_factors.append('Manipulation techniques detected')
        
        # Regional context risk
        regional = analysis_result.get('regional_context', {})
        likely_regions = regional.get('likely_regions', [])
        
        if likely_regions:
            highest_match = likely_regions[0]['match_score']
            if highest_match > 0.5:
                risk_score += 0.2
                risk_factors.append('Strong regional context match detected')
        
        # Temporal manipulation risk
        temporal = analysis_result.get('temporal_context', {})
        if temporal.get('timing_manipulation', False):
            risk_score += 0.1
            risk_factors.append('Timing manipulation indicators detected')
        
        # Determine overall risk level
        if risk_score >= 0.7:
            risk_level = 'very_high'
        elif risk_score >= 0.5:
            risk_level = 'high'
        elif risk_score >= 0.3:
            risk_level = 'medium'
        elif risk_score >= 0.1:
            risk_level = 'low'
        else:
            risk_level = 'very_low'
        
        return {
            'overall_risk_score': round(risk_score, 2),
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'cultural_sensitivity_warning': sensitivity_level in ['medium', 'high'],
            'viral_potential': 'high' if len(manipulation_techniques) > 1 else 'medium' if manipulation_techniques else 'low'
        }
    
    def get_region_specific_advice(self, content: str, region: str) -> Dict[str, Any]:
        """Get region-specific advice for content verification."""
        if region not in self.regional_patterns:
            return {'error': 'Region not supported'}
        
        region_data = self.regional_patterns[region]
        
        advice = {
            'region': region,
            'common_vulnerabilities': region_data['vulnerability_factors'],
            'recommended_verification_steps': [],
            'local_fact_checkers': [],
            'cultural_considerations': []
        }
        
        # Region-specific verification steps
        if region == 'north_india':
            advice['recommended_verification_steps'] = [
                'Check with official government websites',
                'Verify with local administration',
                'Cross-check with regional news outlets',
                'Consult local community leaders'
            ]
            advice['local_fact_checkers'] = [
                'Boom Live', 'Alt News', 'Fact Checker India'
            ]
        
        elif region == 'south_india':
            advice['recommended_verification_steps'] = [
                'Check regional language news sources',
                'Verify with state government portals',
                'Consult local academic institutions',
                'Check regional fact-checking organizations'
            ]
        
        # Cultural considerations
        advice['cultural_considerations'] = [
            'Be sensitive to linguistic pride',
            'Respect regional autonomy concerns',
            'Understand local political dynamics',
            'Consider historical context'
        ]
        
        return advice
    
    def get_analyzer_stats(self) -> Dict[str, Any]:
        """Get statistics about the cultural analyzer's capabilities."""
        return {
            'supported_regions': list(self.regional_patterns.keys()),
            'supported_languages': ['hindi', 'english', 'tamil', 'bengali', 'marathi'],
            'cultural_indicators': sum(len(indicators) for indicators in self.sensitivity_indicators.values()),
            'regional_patterns': len(self.regional_patterns),
            'social_media_platforms': ['whatsapp', 'facebook', 'twitter', 'youtube', 'instagram'],
            'manipulation_techniques_detected': [
                'emotional_blackmail', 'religious_obligation', 'nationalism_appeal',
                'fear_mongering', 'health_scare', 'social_pressure'
            ],
            'seasonal_contexts': len(self.seasonal_patterns['festivals']) + len(self.seasonal_patterns['seasons']),
            'sensitivity_categories': list(self.sensitivity_indicators.keys())
        }
