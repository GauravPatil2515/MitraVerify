"""
MitraVerify Cross-Encoder Reranker
Uses cross-encoder models for better passage ranking
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CrossEncoderReranker:
    """Cross-encoder reranker for improved passage ranking"""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize cross-encoder reranker

        Args:
            model_name: HuggingFace model name for cross-encoder
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None

        # Initialize model
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the cross-encoder model"""
        try:
            from sentence_transformers import CrossEncoder
            logger.info(f"Loading cross-encoder model: {self.model_name}")
            self.model = CrossEncoder(self.model_name)
            logger.info("Cross-encoder model loaded successfully")
        except ImportError:
            logger.error("SentenceTransformers not installed. Install with: pip install sentence-transformers")
            self.model = None
        except Exception as e:
            logger.error(f"Error loading cross-encoder model: {e}")
            self.model = None

    def rerank(self, query: str, passages: List[Dict[str, Any]],
               top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Rerank passages based on relevance to query

        Args:
            query: Search query
            passages: List of passage dictionaries with content and metadata
            top_k: Number of top results to return (None = return all)

        Returns:
            Reranked list of passages with updated scores
        """
        if not self.model:
            logger.warning("Cross-encoder model not available, returning original ranking")
            return passages

        if not passages:
            return []

        try:
            # Prepare input pairs for cross-encoder
            query_passage_pairs = []

            for passage in passages:
                # Use title + content for better ranking
                title = passage.get('title', '')
                content = passage.get('content', '')

                # Truncate content if too long (cross-encoders have token limits)
                if len(content) > 500:
                    content = content[:500] + "..."

                # Combine title and content
                passage_text = f"{title} {content}".strip()
                query_passage_pairs.append([query, passage_text])

            # Get relevance scores from cross-encoder
            logger.info(f"Reranking {len(query_passage_pairs)} passages")
            scores = self.model.predict(query_passage_pairs)

            # Add scores to passages and sort
            reranked_passages = []
            for i, passage in enumerate(passages):
                passage_copy = passage.copy()
                passage_copy['rerank_score'] = float(scores[i])
                passage_copy['combined_score'] = self._combine_scores(
                    passage_copy.get('similarity_score', 0.0),
                    passage_copy['rerank_score']
                )
                reranked_passages.append(passage_copy)

            # Sort by combined score (descending)
            reranked_passages.sort(key=lambda x: x['combined_score'], reverse=True)

            # Return top-k results
            if top_k:
                reranked_passages = reranked_passages[:top_k]

            logger.info(f"Reranked {len(reranked_passages)} passages")
            return reranked_passages

        except Exception as e:
            logger.error(f"Error in reranking: {e}")
            return passages

    def _combine_scores(self, similarity_score: float, rerank_score: float,
                       similarity_weight: float = 0.3, rerank_weight: float = 0.7) -> float:
        """
        Combine similarity and rerank scores

        Args:
            similarity_score: Original similarity score (0-1)
            rerank_score: Cross-encoder score (typically -10 to 10)
            similarity_weight: Weight for similarity score
            rerank_weight: Weight for rerank score

        Returns:
            Combined score (0-1)
        """
        try:
            # Normalize rerank score to 0-1 range
            # Cross-encoder scores are typically in range [-10, 10]
            # Convert to 0-1 using sigmoid function
            normalized_rerank = 1 / (1 + np.exp(-rerank_score))

            # Combine scores
            combined = (similarity_weight * similarity_score) + (rerank_weight * normalized_rerank)

            # Ensure result is in 0-1 range
            return max(0.0, min(1.0, combined))

        except Exception as e:
            logger.error(f"Error combining scores: {e}")
            return similarity_score

    def batch_rerank(self, queries: List[str], passage_lists: List[List[Dict[str, Any]]],
                    top_k: Optional[int] = None) -> List[List[Dict[str, Any]]]:
        """
        Rerank multiple queries with their passage lists

        Args:
            queries: List of queries
            passage_lists: List of passage lists (one per query)
            top_k: Number of top results per query

        Returns:
            List of reranked passage lists
        """
        if len(queries) != len(passage_lists):
            logger.error("Number of queries must match number of passage lists")
            return passage_lists

        reranked_results = []

        for query, passages in zip(queries, passage_lists):
            reranked = self.rerank(query, passages, top_k)
            reranked_results.append(reranked)

        return reranked_results

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the cross-encoder model"""
        return {
            'model_name': self.model_name,
            'model_loaded': self.model is not None,
            'model_type': 'cross_encoder'
        }

class HybridRetriever:
    """Combines dense retrieval with cross-encoder reranking"""

    def __init__(self, evidence_retriever, cross_encoder_reranker: CrossEncoderReranker):
        """
        Initialize hybrid retriever

        Args:
            evidence_retriever: EvidenceRetriever instance
            cross_encoder_reranker: CrossEncoderReranker instance
        """
        self.evidence_retriever = evidence_retriever
        self.cross_encoder = cross_encoder_reranker

    def retrieve_and_rerank(self, query: str, initial_top_k: int = 50,
                           final_top_k: int = 10, min_similarity: float = 0.0) -> List[Dict[str, Any]]:
        """
        Retrieve evidence and rerank with cross-encoder

        Args:
            query: Search query
            initial_top_k: Number of candidates to retrieve initially
            final_top_k: Number of final results to return
            min_similarity: Minimum similarity threshold

        Returns:
            Reranked evidence results
        """
        try:
            # Step 1: Initial retrieval with dense embeddings
            logger.info(f"Initial retrieval for query: {query[:50]}...")
            candidates = self.evidence_retriever.retrieve_evidence(
                query, top_k=initial_top_k, min_similarity=min_similarity
            )

            if not candidates:
                logger.info("No candidates found in initial retrieval")
                return []

            # Step 2: Rerank with cross-encoder
            logger.info(f"Reranking {len(candidates)} candidates...")
            reranked = self.cross_encoder.rerank(query, candidates, top_k=final_top_k)

            # Step 3: Add ranking metadata
            for i, result in enumerate(reranked):
                result['final_rank'] = i + 1
                result['ranking_method'] = 'hybrid_dense_crossencoder'

            logger.info(f"Hybrid retrieval completed: {len(reranked)} final results")
            return reranked

        except Exception as e:
            logger.error(f"Error in hybrid retrieval: {e}")
            # Fallback to dense retrieval only
            return self.evidence_retriever.retrieve_evidence(
                query, top_k=final_top_k, min_similarity=min_similarity
            )

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            'evidence_retriever': self.evidence_retriever.get_corpus_stats(),
            'cross_encoder': self.cross_encoder.get_model_info(),
            'retrieval_method': 'hybrid'
        }

def main():
    """Test the cross-encoder reranker"""
    print("Testing Cross-Encoder Reranker...")

    try:
        # Initialize cross-encoder
        reranker = CrossEncoderReranker()

        if not reranker.model:
            print("Cross-encoder model not loaded. Install with: pip install sentence-transformers")
            return

        # Test data
        query = "COVID-19 vaccine safety and effectiveness"

        passages = [
            {
                'title': 'COVID-19 Vaccine Safety Study',
                'content': 'A comprehensive study shows that COVID-19 vaccines are safe and effective in preventing severe illness.',
                'similarity_score': 0.85,
                'source': 'WHO'
            },
            {
                'title': 'Government Health Guidelines',
                'content': 'The government recommends COVID-19 vaccination for all eligible citizens to protect public health.',
                'similarity_score': 0.75,
                'source': 'Health Ministry'
            },
            {
                'title': 'Economic Impact of Pandemic',
                'content': 'The COVID-19 pandemic has significantly impacted global economies and supply chains.',
                'similarity_score': 0.60,
                'source': 'World Bank'
            },
            {
                'title': 'Weather Forecast Today',
                'content': 'Today will be partly cloudy with a chance of rain in the afternoon.',
                'similarity_score': 0.20,
                'source': 'Weather Service'
            }
        ]

        print(f"Original passages (ranked by similarity):")
        for i, p in enumerate(passages, 1):
            print(f"{i}. {p['title']} (similarity: {p['similarity_score']:.3f})")

        # Rerank passages
        reranked_passages = reranker.rerank(query, passages, top_k=3)

        print(f"\nReranked passages (hybrid scoring):")
        for i, p in enumerate(reranked_passages, 1):
            print(f"{i}. {p['title']}")
            print(f"   Similarity: {p['similarity_score']:.3f}")
            print(f"   Rerank Score: {p.get('rerank_score', 'N/A')}")
            print(f"   Combined: {p['combined_score']:.3f}")

        print("\nCross-encoder reranker test completed!")

    except ImportError as e:
        print(f"Missing dependencies: {e}")
        print("Install required packages:")
        print("pip install sentence-transformers numpy")
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == '__main__':
    main()