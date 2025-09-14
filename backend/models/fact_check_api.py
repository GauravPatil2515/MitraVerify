"""
MitraVerify Google Fact Check API Integration
Integrates with Google Fact Check Tools API for direct claim verification
"""

import os
import json
import logging
import requests
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import time
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleFactCheckAPI:
    """Google Fact Check Tools API integration for claim verification"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Google Fact Check API client

        Args:
            api_key: Google API key (optional, can be set via environment variable)
        """
        self.api_key = api_key or os.environ.get('GOOGLE_API_KEY')
        self.base_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        self.session = requests.Session()

        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1 second between requests

        # Cache for API responses
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache TTL

        if not self.api_key:
            logger.warning("Google API key not provided. Set GOOGLE_API_KEY environment variable.")
        else:
            logger.info("Google Fact Check API initialized")

    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _get_cache_key(self, query: str, language_code: str = "en") -> str:
        """Generate cache key for API response"""
        key_data = f"{query}:{language_code}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response if available and not expired"""
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                logger.info("Using cached Google Fact Check response")
                return cached_data
            else:
                # Remove expired cache entry
                del self.cache[cache_key]
        return None

    def _cache_response(self, cache_key: str, response_data: Dict[str, Any]):
        """Cache API response"""
        self.cache[cache_key] = (response_data, time.time())

    def search_claims(self, query: str, language_code: str = "en",
                     max_age_days: Optional[int] = None) -> Dict[str, Any]:
        """
        Search for fact-checks related to a claim

        Args:
            query: The claim to search for
            language_code: Language code (default: 'en')
            max_age_days: Maximum age of fact-checks in days

        Returns:
            Dictionary containing search results and metadata
        """
        if not self.api_key:
            return {
                'error': 'Google API key not configured',
                'claims': [],
                'total_results': 0
            }

        # Check cache first
        cache_key = self._get_cache_key(query, language_code)
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            return cached_response

        try:
            # Rate limiting
            self._rate_limit()

            # Prepare parameters
            params = {
                'key': self.api_key,
                'query': query,
                'languageCode': language_code
            }

            if max_age_days:
                # Calculate max age in seconds
                max_age_seconds = max_age_days * 24 * 60 * 60
                params['maxAgeDays'] = max_age_days

            # Make API request
            logger.info(f"Searching Google Fact Check API for: {query[:50]}...")
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Process and format results
            processed_data = self._process_api_response(data, query)

            # Cache the response
            self._cache_response(cache_key, processed_data)

            return processed_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Google Fact Check API request failed: {e}")
            return {
                'error': f'API request failed: {str(e)}',
                'claims': [],
                'total_results': 0
            }
        except Exception as e:
            logger.error(f"Error searching Google Fact Check API: {e}")
            return {
                'error': f'Unexpected error: {str(e)}',
                'claims': [],
                'total_results': 0
            }

    def _process_api_response(self, api_response: Dict[str, Any], original_query: str) -> Dict[str, Any]:
        """
        Process and format Google Fact Check API response

        Args:
            api_response: Raw API response
            original_query: Original search query

        Returns:
            Processed response with standardized format
        """
        try:
            claims = api_response.get('claims', [])

            processed_claims = []
            for claim in claims:
                processed_claim = self._process_claim(claim)
                if processed_claim:
                    processed_claims.append(processed_claim)

            # Sort by review date (most recent first)
            processed_claims.sort(key=lambda x: x.get('review_date', ''), reverse=True)

            return {
                'query': original_query,
                'total_results': len(processed_claims),
                'claims': processed_claims,
                'api_response_time': datetime.utcnow().isoformat(),
                'source': 'google_fact_check'
            }

        except Exception as e:
            logger.error(f"Error processing API response: {e}")
            return {
                'query': original_query,
                'total_results': 0,
                'claims': [],
                'error': f'Processing error: {str(e)}',
                'source': 'google_fact_check'
            }

    def _process_claim(self, claim: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process individual claim from API response

        Args:
            claim: Raw claim data from API

        Returns:
            Processed claim data or None if invalid
        """
        try:
            claim_review = claim.get('claimReview', [{}])[0] if claim.get('claimReview') else {}

            if not claim_review:
                return None

            # Extract rating information
            rating = self._extract_rating(claim_review)

            processed_claim = {
                'id': f"google_{claim.get('claimReviewId', '')}",
                'claim_text': claim.get('text', ''),
                'claimant': claim.get('claimant', ''),
                'claim_date': claim.get('claimDate', ''),
                'publisher_name': claim_review.get('publisher', {}).get('name', ''),
                'publisher_site': claim_review.get('publisher', {}).get('site', ''),
                'url': claim_review.get('url', ''),
                'title': claim_review.get('title', ''),
                'review_date': claim_review.get('reviewDate', ''),
                'rating': rating,
                'language_code': claim.get('languageCode', 'en'),
                'appearance': claim.get('claimAppearance', [])
            }

            return processed_claim

        except Exception as e:
            logger.error(f"Error processing claim: {e}")
            return None

    def _extract_rating(self, claim_review: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and standardize rating information

        Args:
            claim_review: Claim review data

        Returns:
            Standardized rating information
        """
        try:
            textual_rating = claim_review.get('textualRating', '')
            rating_value = None

            # Try to extract numeric rating if available
            if 'ratingValue' in claim_review:
                try:
                    rating_value = float(claim_review['ratingValue'])
                except (ValueError, TypeError):
                    rating_value = None

            # Determine truthfulness score (0-1 scale)
            truthfulness_score = self._calculate_truthfulness_score(textual_rating, rating_value)

            return {
                'textual_rating': textual_rating,
                'numeric_rating': rating_value,
                'truthfulness_score': truthfulness_score,
                'rating_explanation': claim_review.get('ratingExplanation', '')
            }

        except Exception as e:
            logger.error(f"Error extracting rating: {e}")
            return {
                'textual_rating': 'Unknown',
                'numeric_rating': None,
                'truthfulness_score': 0.5,
                'rating_explanation': ''
            }

    def _calculate_truthfulness_score(self, textual_rating: str, numeric_rating: Optional[float]) -> float:
        """
        Calculate truthfulness score from rating information

        Args:
            textual_rating: Text description of rating
            numeric_rating: Numeric rating value

        Returns:
            Truthfulness score (0-1, where 1 is most truthful)
        """
        try:
            # Use numeric rating if available
            if numeric_rating is not None:
                # Assume scale of 1-5 or similar, normalize to 0-1
                if 0 <= numeric_rating <= 5:
                    return numeric_rating / 5.0
                elif 0 <= numeric_rating <= 10:
                    return numeric_rating / 10.0
                else:
                    return max(0.0, min(1.0, numeric_rating))

            # Fallback to textual rating analysis
            rating_lower = textual_rating.lower()

            # Positive indicators
            if any(word in rating_lower for word in ['true', 'correct', 'accurate', 'verified']):
                return 0.9
            elif any(word in rating_lower for word in ['mostly true', 'largely correct']):
                return 0.7
            elif any(word in rating_lower for word in ['half true', 'partially true']):
                return 0.5
            elif any(word in rating_lower for word in ['mostly false', 'largely incorrect']):
                return 0.3
            elif any(word in rating_lower for word in ['false', 'incorrect', 'misleading']):
                return 0.1
            else:
                return 0.5  # Neutral/unknown

        except Exception as e:
            logger.error(f"Error calculating truthfulness score: {e}")
            return 0.5

    def get_claim_details(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific claim

        Args:
            claim_id: Google Fact Check claim ID

        Returns:
            Detailed claim information or None if not found
        """
        # Note: Google Fact Check API doesn't have a direct "get by ID" endpoint
        # This would require storing claim details locally or using search
        logger.warning("Google Fact Check API doesn't support direct claim retrieval by ID")
        return None

    def clear_cache(self):
        """Clear the API response cache"""
        self.cache.clear()
        logger.info("Google Fact Check API cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'cache_entries': len(self.cache),
            'cache_ttl_seconds': self.cache_ttl,
            'api_key_configured': self.api_key is not None
        }

class FactCheckVerifier:
    """High-level interface for fact-checking claims using multiple sources"""

    def __init__(self, google_api_key: Optional[str] = None):
        """
        Initialize fact-check verifier

        Args:
            google_api_key: Google API key for Fact Check Tools
        """
        self.google_api = GoogleFactCheckAPI(google_api_key)

    def verify_claim(self, claim: str, language_code: str = "en",
                    max_age_days: int = 365) -> Dict[str, Any]:
        """
        Verify a claim using available fact-checking sources

        Args:
            claim: The claim to verify
            language_code: Language code
            max_age_days: Maximum age of fact-checks to consider

        Returns:
            Verification results with confidence scores
        """
        try:
            logger.info(f"Verifying claim: {claim[:100]}...")

            # Search Google Fact Check
            google_results = self.google_api.search_claims(
                claim, language_code, max_age_days
            )

            # Combine results from all sources
            verification_result = self._combine_verification_results(
                claim, google_results
            )

            return verification_result

        except Exception as e:
            logger.error(f"Error verifying claim: {e}")
            return {
                'claim': claim,
                'verdict': 'error',
                'confidence': 0.0,
                'sources': [],
                'error': str(e)
            }

    def _combine_verification_results(self, claim: str,
                                    google_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combine verification results from multiple sources

        Args:
            claim: Original claim
            google_results: Results from Google Fact Check API

        Returns:
            Combined verification result
        """
        try:
            all_claims = google_results.get('claims', [])

            if not all_claims:
                return {
                    'claim': claim,
                    'verdict': 'insufficient_data',
                    'confidence': 0.0,
                    'sources': [],
                    'explanation': 'No fact-checks found for this claim'
                }

            # Calculate overall truthfulness score
            truthfulness_scores = [c.get('rating', {}).get('truthfulness_score', 0.5)
                                 for c in all_claims if c.get('rating')]

            if truthfulness_scores:
                avg_truthfulness = sum(truthfulness_scores) / len(truthfulness_scores)

                # Determine verdict based on average score
                if avg_truthfulness >= 0.8:
                    verdict = 'true'
                elif avg_truthfulness >= 0.6:
                    verdict = 'mostly_true'
                elif avg_truthfulness >= 0.4:
                    verdict = 'mixed'
                elif avg_truthfulness >= 0.2:
                    verdict = 'mostly_false'
                else:
                    verdict = 'false'

                confidence = min(avg_truthfulness, 1.0 - avg_truthfulness) * 2  # 0-1 scale
            else:
                verdict = 'unknown'
                confidence = 0.0

            return {
                'claim': claim,
                'verdict': verdict,
                'confidence': round(confidence, 3),
                'average_truthfulness': round(avg_truthfulness, 3) if truthfulness_scores else None,
                'sources': [{
                    'name': 'Google Fact Check',
                    'total_results': len(all_claims),
                    'top_claims': all_claims[:3]  # Top 3 most relevant
                }],
                'all_claims': all_claims,
                'verification_date': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error combining verification results: {e}")
            return {
                'claim': claim,
                'verdict': 'error',
                'confidence': 0.0,
                'sources': [],
                'error': str(e)
            }

def main():
    """Test the Google Fact Check API integration"""
    print("Testing Google Fact Check API Integration...")

    try:
        # Initialize verifier
        verifier = FactCheckVerifier()

        # Test claims
        test_claims = [
            "COVID-19 vaccines are completely safe with no side effects",
            "The Earth is flat",
            "Climate change is caused by human activities"
        ]

        for claim in test_claims:
            print(f"\n{'='*60}")
            print(f"Verifying: {claim}")
            print('='*60)

            result = verifier.verify_claim(claim)

            print(f"Verdict: {result['verdict']}")
            print(f"Confidence: {result['confidence']}")
            print(f"Sources: {len(result['sources'])}")

            if result['sources']:
                source = result['sources'][0]
                print(f"Google Fact Check results: {source['total_results']}")

                if source['top_claims']:
                    print("\nTop fact-check:")
                    top_claim = source['top_claims'][0]
                    print(f"  Publisher: {top_claim.get('publisher_name', 'Unknown')}")
                    print(f"  Rating: {top_claim.get('rating', {}).get('textual_rating', 'Unknown')}")
                    print(f"  URL: {top_claim.get('url', 'N/A')}")

        print("\n✅ Google Fact Check API test completed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("Make sure to set GOOGLE_API_KEY environment variable")

if __name__ == '__main__':
    main()