"""
MitraVerify Data Ingestion Pipeline
Automated pipeline to populate evidence corpus from web scraper and fact-check sources
"""

import os
import json
import logging
import time
from typing import List, Dict, Any, Optional, Generator
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import queue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataIngestionPipeline:
    """Data ingestion pipeline for evidence corpus"""

    def __init__(self, evidence_retriever, web_scraper=None, fact_check_api=None,
                 max_workers: int = 4, batch_size: int = 50):
        """
        Initialize data ingestion pipeline

        Args:
            evidence_retriever: EvidenceRetriever instance
            web_scraper: WebScraper instance (optional)
            fact_check_api: FactCheckVerifier instance (optional)
            max_workers: Maximum number of worker threads
            batch_size: Number of articles to process in each batch
        """
        self.evidence_retriever = evidence_retriever
        self.web_scraper = web_scraper
        self.fact_check_api = fact_check_api
        self.max_workers = max_workers
        self.batch_size = batch_size

        # Processing queues
        self.article_queue = queue.Queue()
        self.result_queue = queue.Queue()

        # Statistics
        self.stats = {
            'articles_processed': 0,
            'articles_added': 0,
            'articles_failed': 0,
            'start_time': None,
            'end_time': None
        }

        # Threading control
        self.stop_event = threading.Event()
        self.workers = []

    def ingest_from_web_scraper(self, sources: List[str] = None,
                               max_articles: int = 1000,
                               date_from: Optional[str] = None) -> Dict[str, Any]:
        """
        Ingest articles from web scraper

        Args:
            sources: List of sources to scrape (None = all sources)
            max_articles: Maximum number of articles to ingest
            date_from: Date from which to scrape articles (YYYY-MM-DD)

        Returns:
            Ingestion statistics
        """
        if not self.web_scraper:
            logger.error("Web scraper not available")
            return {'error': 'Web scraper not configured'}

        try:
            logger.info(f"Starting web scraper ingestion (max {max_articles} articles)")

            self.stats['start_time'] = datetime.utcnow()

            # Get articles from web scraper
            articles = self.web_scraper.scrape_articles(
                sources=sources,
                max_articles=max_articles,
                date_from=date_from
            )

            if not articles:
                logger.warning("No articles found from web scraper")
                return {'articles_processed': 0, 'articles_added': 0}

            # Process articles in batches
            total_processed = 0
            total_added = 0

            for i in range(0, len(articles), self.batch_size):
                batch = articles[i:i + self.batch_size]
                logger.info(f"Processing batch {i//self.batch_size + 1}/{(len(articles) + self.batch_size - 1)//self.batch_size}")

                batch_results = self._process_article_batch(batch)
                total_processed += batch_results['processed']
                total_added += batch_results['added']

                # Save corpus periodically
                if (i + self.batch_size) % (self.batch_size * 5) == 0:
                    self._save_corpus_checkpoint()

            # Final save
            self._save_corpus_checkpoint()

            self.stats['end_time'] = datetime.utcnow()
            self.stats['articles_processed'] = total_processed
            self.stats['articles_added'] = total_added

            logger.info(f"Web scraper ingestion completed: {total_added}/{total_processed} articles added")

            return {
                'articles_processed': total_processed,
                'articles_added': total_added,
                'articles_failed': total_processed - total_added,
                'processing_time_seconds': (self.stats['end_time'] - self.stats['start_time']).total_seconds(),
                'sources': sources or ['all']
            }

        except Exception as e:
            logger.error(f"Error in web scraper ingestion: {e}")
            return {'error': str(e), 'articles_processed': 0, 'articles_added': 0}

    def ingest_from_fact_check_api(self, claims: List[str],
                                  language_code: str = "en") -> Dict[str, Any]:
        """
        Ingest fact-check data from Google Fact Check API

        Args:
            claims: List of claims to verify and ingest
            language_code: Language code for fact-checks

        Returns:
            Ingestion statistics
        """
        if not self.fact_check_api:
            logger.error("Fact check API not available")
            return {'error': 'Fact check API not configured'}

        try:
            logger.info(f"Starting fact-check API ingestion for {len(claims)} claims")

            self.stats['start_time'] = datetime.utcnow()

            # Process claims in parallel
            fact_check_articles = []
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_claim = {
                    executor.submit(self._process_fact_check_claim, claim, language_code): claim
                    for claim in claims
                }

                for future in as_completed(future_to_claim):
                    try:
                        result = future.result()
                        if result:
                            fact_check_articles.extend(result)
                    except Exception as e:
                        logger.error(f"Error processing fact-check claim: {e}")

            if not fact_check_articles:
                logger.warning("No fact-check articles generated")
                return {'articles_processed': 0, 'articles_added': 0}

            # Process fact-check articles in batches
            total_processed = 0
            total_added = 0

            for i in range(0, len(fact_check_articles), self.batch_size):
                batch = fact_check_articles[i:i + self.batch_size]
                batch_results = self._process_article_batch(batch)
                total_processed += batch_results['processed']
                total_added += batch_results['added']

            # Final save
            self._save_corpus_checkpoint()

            self.stats['end_time'] = datetime.utcnow()
            self.stats['articles_processed'] = total_processed
            self.stats['articles_added'] = total_added

            logger.info(f"Fact-check API ingestion completed: {total_added}/{total_processed} articles added")

            return {
                'articles_processed': total_processed,
                'articles_added': total_added,
                'articles_failed': total_processed - total_added,
                'claims_processed': len(claims),
                'processing_time_seconds': (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            }

        except Exception as e:
            logger.error(f"Error in fact-check API ingestion: {e}")
            return {'error': str(e), 'articles_processed': 0, 'articles_added': 0}

    def _process_fact_check_claim(self, claim: str, language_code: str) -> List[Dict[str, Any]]:
        """
        Process a single fact-check claim and convert to articles

        Args:
            claim: Claim to verify
            language_code: Language code

        Returns:
            List of article dictionaries
        """
        try:
            # Verify claim using fact-check API
            verification_result = self.fact_check_api.verify_claim(claim, language_code)

            articles = []

            # Convert fact-check results to article format
            for source in verification_result.get('sources', []):
                for claim_data in source.get('top_claims', []):
                    article = {
                        'id': claim_data.get('id', f"factcheck_{hash(claim)}"),
                        'title': claim_data.get('title', f"Fact Check: {claim[:50]}..."),
                        'content': self._generate_fact_check_content(claim, claim_data),
                        'url': claim_data.get('url', ''),
                        'source': claim_data.get('publisher_name', 'Google Fact Check'),
                        'published_date': claim_data.get('review_date'),
                        'author': claim_data.get('publisher_name', ''),
                        'tags': ['fact-check', 'verification', claim_data.get('rating', {}).get('textual_rating', '').lower()],
                        'credibility_score': claim_data.get('rating', {}).get('truthfulness_score', 0.5),
                        'claim_text': claim,
                        'verification_result': verification_result.get('verdict'),
                        'verification_confidence': verification_result.get('confidence', 0.0)
                    }
                    articles.append(article)

            return articles

        except Exception as e:
            logger.error(f"Error processing fact-check claim '{claim}': {e}")
            return []

    def _generate_fact_check_content(self, claim: str, claim_data: Dict[str, Any]) -> str:
        """
        Generate article content from fact-check data

        Args:
            claim: Original claim
            claim_data: Fact-check data

        Returns:
            Formatted article content
        """
        try:
            rating = claim_data.get('rating', {})
            content_parts = [
                f"Claim: {claim}",
                f"",
                f"Fact-Check Rating: {rating.get('textual_rating', 'Unknown')}",
                f"Publisher: {claim_data.get('publisher_name', 'Unknown')}",
                f"Review Date: {claim_data.get('review_date', 'Unknown')}",
                f"",
                f"Rating Explanation: {rating.get('rating_explanation', 'No explanation provided')}",
                f"",
                f"Source: {claim_data.get('url', 'N/A')}"
            ]

            return "\n".join(content_parts)

        except Exception as e:
            logger.error(f"Error generating fact-check content: {e}")
            return f"Claim: {claim}\n\nFact-check data could not be processed."

    def _process_article_batch(self, articles: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Process a batch of articles

        Args:
            articles: List of article dictionaries

        Returns:
            Processing statistics
        """
        try:
            processed = 0
            added = 0

            # Embed articles if they don't have embeddings
            embedded_articles = []
            for article in articles:
                if 'embedding' not in article:
                    # Generate embedding using evidence retriever's embedding engine
                    embedding = self.evidence_retriever.embedding_engine.encode_text(
                        article.get('content', '')
                    )
                    if embedding is not None:
                        article_copy = article.copy()
                        article_copy['embedding'] = embedding.tolist()
                        embedded_articles.append(article_copy)
                    else:
                        logger.warning(f"Failed to embed article: {article.get('title', 'Unknown')}")
                else:
                    embedded_articles.append(article)

            # Add to evidence corpus
            if embedded_articles:
                success = self.evidence_retriever.add_evidence(embedded_articles)
                if success:
                    added = len(embedded_articles)
                processed = len(embedded_articles)

            return {'processed': processed, 'added': added}

        except Exception as e:
            logger.error(f"Error processing article batch: {e}")
            return {'processed': len(articles), 'added': 0}

    def _save_corpus_checkpoint(self):
        """Save current corpus state as checkpoint"""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            checkpoint_path = f"evidence_corpus_checkpoint_{timestamp}"

            success = self.evidence_retriever.save_corpus(
                index_path=f"{checkpoint_path}_index.idx",
                metadata_path=f"{checkpoint_path}_metadata.pkl"
            )

            if success:
                logger.info(f"Corpus checkpoint saved: {checkpoint_path}")
            else:
                logger.warning("Failed to save corpus checkpoint")

        except Exception as e:
            logger.error(f"Error saving corpus checkpoint: {e}")

    def get_ingestion_stats(self) -> Dict[str, Any]:
        """Get current ingestion statistics"""
        current_stats = self.stats.copy()

        if current_stats['start_time'] and current_stats['end_time']:
            current_stats['total_time_seconds'] = (
                current_stats['end_time'] - current_stats['start_time']
            ).total_seconds()

        return current_stats

    def stop_ingestion(self):
        """Stop the ingestion process"""
        logger.info("Stopping data ingestion pipeline...")
        self.stop_event.set()

        # Wait for workers to finish
        for worker in self.workers:
            if worker.is_alive():
                worker.join(timeout=5)

        logger.info("Data ingestion pipeline stopped")

class AutomatedIngestionScheduler:
    """Automated scheduler for periodic data ingestion"""

    def __init__(self, ingestion_pipeline: DataIngestionPipeline,
                 schedule_config: Dict[str, Any] = None):
        """
        Initialize automated ingestion scheduler

        Args:
            ingestion_pipeline: DataIngestionPipeline instance
            schedule_config: Configuration for scheduling
        """
        self.pipeline = ingestion_pipeline
        self.schedule_config = schedule_config or self._default_schedule_config()
        self.running = False
        self.thread = None

    def _default_schedule_config(self) -> Dict[str, Any]:
        """Get default schedule configuration"""
        return {
            'web_scraper_interval_hours': 24,  # Daily
            'fact_check_interval_hours': 6,    # 4 times per day
            'max_articles_per_run': 500,
            'sources': ['altnews', 'boom', 'factly', 'indiatoday'],
            'fact_check_claims': [
                "COVID-19 vaccines cause infertility",
                "5G technology spreads coronavirus",
                "Climate change is a hoax",
                "Vaccines contain microchips"
            ]
        }

    def start_automated_ingestion(self):
        """Start automated ingestion in background thread"""
        if self.running:
            logger.warning("Automated ingestion already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler)
        self.thread.daemon = True
        self.thread.start()

        logger.info("Automated ingestion scheduler started")

    def stop_automated_ingestion(self):
        """Stop automated ingestion"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)

        logger.info("Automated ingestion scheduler stopped")

    def _run_scheduler(self):
        """Run the scheduling loop"""
        last_web_scrape = 0
        last_fact_check = 0

        while self.running:
            try:
                current_time = time.time()

                # Check web scraper schedule
                if (current_time - last_web_scrape) >= (self.schedule_config['web_scraper_interval_hours'] * 3600):
                    logger.info("Running scheduled web scraper ingestion")
                    self._run_web_scraper_ingestion()
                    last_web_scrape = current_time

                # Check fact-check schedule
                if (current_time - last_fact_check) >= (self.schedule_config['fact_check_interval_hours'] * 3600):
                    logger.info("Running scheduled fact-check ingestion")
                    self._run_fact_check_ingestion()
                    last_fact_check = current_time

                # Sleep for 5 minutes before next check
                time.sleep(300)

            except Exception as e:
                logger.error(f"Error in automated ingestion scheduler: {e}")
                time.sleep(300)  # Wait before retrying

    def _run_web_scraper_ingestion(self):
        """Run web scraper ingestion"""
        try:
            if not self.pipeline.web_scraper:
                logger.warning("Web scraper not available for scheduled ingestion")
                return

            # Calculate date from (last 7 days)
            date_from = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")

            result = self.pipeline.ingest_from_web_scraper(
                sources=self.schedule_config['sources'],
                max_articles=self.schedule_config['max_articles_per_run'],
                date_from=date_from
            )

            logger.info(f"Scheduled web scraper ingestion completed: {result}")

        except Exception as e:
            logger.error(f"Error in scheduled web scraper ingestion: {e}")

    def _run_fact_check_ingestion(self):
        """Run fact-check ingestion"""
        try:
            if not self.pipeline.fact_check_api:
                logger.warning("Fact-check API not available for scheduled ingestion")
                return

            result = self.pipeline.ingest_from_fact_check_api(
                claims=self.schedule_config['fact_check_claims']
            )

            logger.info(f"Scheduled fact-check ingestion completed: {result}")

        except Exception as e:
            logger.error(f"Error in scheduled fact-check ingestion: {e}")

def main():
    """Test the data ingestion pipeline"""
    print("Testing Data Ingestion Pipeline...")

    try:
        # Mock components for testing
        class MockEmbeddingEngine:
            def encode_text(self, text):
                # Return a simple mock embedding
                import numpy as np
                return np.random.rand(384).astype(np.float32)

        class MockVectorSearch:
            def add_vectors(self, vectors, metadata, ids=None):
                return True

        class MockEvidenceRetriever:
            def __init__(self):
                self.embedding_engine = MockEmbeddingEngine()
                self.vector_search = MockVectorSearch()

            def add_evidence(self, articles):
                return True

            def save_corpus(self, **kwargs):
                return True

        # Initialize pipeline
        retriever = MockEvidenceRetriever()
        pipeline = DataIngestionPipeline(retriever)

        # Test with mock data
        mock_articles = [
            {
                'id': f'mock_{i}',
                'title': f'Mock Article {i}',
                'content': f'This is mock content for article {i}. It contains some test information.',
                'url': f'https://example.com/article{i}',
                'source': 'Mock Source',
                'published_date': datetime.utcnow().isoformat(),
                'author': 'Mock Author',
                'tags': ['test', 'mock'],
                'credibility_score': 0.8
            }
            for i in range(10)
        ]

        print("Testing article batch processing...")
        result = pipeline._process_article_batch(mock_articles)

        print(f"Processed: {result['processed']} articles")
        print(f"Added: {result['added']} articles")

        print("\n✅ Data ingestion pipeline test completed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == '__main__':
    main()