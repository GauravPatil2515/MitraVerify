"""
MitraVerify FAISS Vector Search with Cross-Encoder Reranking
Efficient similarity search over text embeddings using FAISS and cross-encoder reranking
"""

import os
import json
import logging
import numpy as np
import pickle
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import tempfile
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FAISSVectorSearch:
    """FAISS-based vector search for evidence retrieval"""

    def __init__(self, dimension: int = 384, index_file: str = "faiss_index.idx",
                 metadata_file: str = "faiss_metadata.pkl"):
        """
        Initialize FAISS vector search

        Args:
            dimension: Dimension of embedding vectors
            index_file: File path for saving/loading FAISS index
            metadata_file: File path for saving/loading metadata
        """
        self.dimension = dimension
        self.index_file = index_file
        self.metadata_file = metadata_file
        self.index = None
        self.metadata = []  # List of metadata for each vector
        self.id_to_idx = {}  # Mapping from document IDs to FAISS indices

        # Initialize FAISS
        self._initialize_faiss()

    def _initialize_faiss(self):
        """Initialize FAISS index"""
        try:
            import faiss

            # Use HNSW index for efficient similarity search
            self.index = faiss.IndexHNSWFlat(self.dimension, 32)  # 32 is the number of neighbors

            # Set search parameters for better performance
            self.index.hnsw.efConstruction = 200  # Higher = better quality, slower build
            self.index.hnsw.efSearch = 128       # Higher = better search quality, slower search

            logger.info(f"Initialized FAISS HNSW index with dimension {self.dimension}")

        except ImportError:
            logger.error("FAISS not installed. Install with: pip install faiss-cpu")
            self.index = None
        except Exception as e:
            logger.error(f"Error initializing FAISS: {e}")
            self.index = None

    def add_vectors(self, vectors: np.ndarray, metadata: List[Dict[str, Any]],
                   ids: Optional[List[str]] = None) -> bool:
        """
        Add vectors to the FAISS index

        Args:
            vectors: Numpy array of shape (n, dimension)
            metadata: List of metadata dictionaries for each vector
            ids: Optional list of document IDs

        Returns:
            True if successful, False otherwise
        """
        if not self.index:
            logger.error("FAISS index not initialized")
            return False

        if len(vectors) != len(metadata):
            logger.error("Number of vectors must match number of metadata entries")
            return False

        try:
            # Convert to float32 if needed
            if vectors.dtype != np.float32:
                vectors = vectors.astype(np.float32)

            # Add vectors to index
            self.index.add(vectors)

            # Store metadata
            start_idx = len(self.metadata)
            self.metadata.extend(metadata)

            # Update ID mapping
            if ids:
                for i, doc_id in enumerate(ids):
                    self.id_to_idx[doc_id] = start_idx + i

            logger.info(f"Added {len(vectors)} vectors to FAISS index")
            return True

        except Exception as e:
            logger.error(f"Error adding vectors to FAISS: {e}")
            return False

    def search(self, query_vector: np.ndarray, top_k: int = 10) -> List[Tuple[int, float, Dict[str, Any]]]:
        """
        Search for similar vectors

        Args:
            query_vector: Query embedding vector
            top_k: Number of top results to return

        Returns:
            List of (index, distance, metadata) tuples
        """
        if not self.index:
            logger.error("FAISS index not initialized")
            return []

        try:
            # Ensure query vector is correct shape and type
            if query_vector.ndim == 1:
                query_vector = query_vector.reshape(1, -1)

            if query_vector.dtype != np.float32:
                query_vector = query_vector.astype(np.float32)

            # Search
            distances, indices = self.index.search(query_vector, top_k)

            # Format results
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.metadata):  # Valid index
                    distance = float(distances[0][i])
                    # Convert distance to similarity score (lower distance = higher similarity)
                    similarity = 1.0 / (1.0 + distance)
                    results.append((int(idx), similarity, self.metadata[idx]))

            return results

        except Exception as e:
            logger.error(f"Error searching FAISS index: {e}")
            return []

    def save_index(self, index_path: Optional[str] = None,
                  metadata_path: Optional[str] = None) -> bool:
        """
        Save FAISS index and metadata to disk

        Args:
            index_path: Path to save index (uses self.index_file if None)
            metadata_path: Path to save metadata (uses self.metadata_file if None)

        Returns:
            True if successful, False otherwise
        """
        if not self.index:
            logger.error("No index to save")
            return False

        index_path = index_path or self.index_file
        metadata_path = metadata_path or self.metadata_file

        try:
            import faiss

            # Save FAISS index
            faiss.write_index(self.index, index_path)

            # Save metadata
            with open(metadata_path, 'wb') as f:
                pickle.dump({
                    'metadata': self.metadata,
                    'id_to_idx': self.id_to_idx,
                    'dimension': self.dimension
                }, f)

            logger.info(f"Saved FAISS index to {index_path} and metadata to {metadata_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
            return False

    def load_index(self, index_path: Optional[str] = None,
                  metadata_path: Optional[str] = None) -> bool:
        """
        Load FAISS index and metadata from disk

        Args:
            index_path: Path to load index from (uses self.index_file if None)
            metadata_path: Path to load metadata from (uses self.metadata_file if None)

        Returns:
            True if successful, False otherwise
        """
        index_path = index_path or self.index_file
        metadata_path = metadata_path or self.metadata_file

        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            logger.warning(f"Index files not found: {index_path}, {metadata_path}")
            return False

        try:
            import faiss

            # Load FAISS index
            self.index = faiss.read_index(index_path)

            # Load metadata
            with open(metadata_path, 'rb') as f:
                data = pickle.load(f)
                self.metadata = data.get('metadata', [])
                self.id_to_idx = data.get('id_to_idx', {})
                self.dimension = data.get('dimension', self.dimension)

            logger.info(f"Loaded FAISS index with {len(self.metadata)} vectors")
            return True

        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the FAISS index"""
        if not self.index:
            return {'status': 'not_initialized'}

        try:
            import faiss

            return {
                'status': 'loaded',
                'total_vectors': self.index.ntotal,
                'dimension': self.dimension,
                'metadata_count': len(self.metadata),
                'index_type': type(self.index).__name__,
                'is_trained': self.index.is_trained
            }

        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def clear_index(self):
        """Clear the FAISS index and metadata"""
        if self.index:
            try:
                import faiss
                # Create new empty index
                self.index = faiss.IndexHNSWFlat(self.dimension, 32)
                self.index.hnsw.efConstruction = 200
                self.index.hnsw.efSearch = 128
            except:
                self.index = None

        self.metadata = []
        self.id_to_idx = {}
        logger.info("Cleared FAISS index")

class EvidenceRetriever:
    """High-level interface for evidence retrieval using FAISS"""

    def __init__(self, embedding_engine, vector_search: FAISSVectorSearch):
        """
        Initialize evidence retriever

        Args:
            embedding_engine: TextEmbeddingEngine instance
            vector_search: FAISSVectorSearch instance
        """
        self.embedding_engine = embedding_engine
        self.vector_search = vector_search

    def add_evidence(self, articles: List[Dict[str, Any]]) -> bool:
        """
        Add articles to the evidence corpus

        Args:
            articles: List of article dictionaries with embeddings

        Returns:
            True if successful, False otherwise
        """
        try:
            vectors = []
            metadata = []
            ids = []

            for article in articles:
                embedding = article.get('embedding')
                if embedding:
                    # Convert to numpy array
                    vector = np.array(embedding, dtype=np.float32)
                    vectors.append(vector)

                    # Create metadata
                    meta = {
                        'id': article.get('id', article.get('url', '')),
                        'title': article.get('title', ''),
                        'content': article.get('content', ''),
                        'url': article.get('url', ''),
                        'source': article.get('source', ''),
                        'published_date': article.get('published_date'),
                        'author': article.get('author'),
                        'tags': article.get('tags', []),
                        'credibility_score': article.get('credibility_score', 0.5)
                    }
                    metadata.append(meta)
                    ids.append(article.get('id', article.get('url', '')))

            if vectors:
                vectors_array = np.array(vectors)
                success = self.vector_search.add_vectors(vectors_array, metadata, ids)

                if success:
                    logger.info(f"Added {len(articles)} articles to evidence corpus")
                    return True

            return False

        except Exception as e:
            logger.error(f"Error adding evidence: {e}")
            return False

    def retrieve_evidence(self, query: str, top_k: int = 10,
                         min_similarity: float = 0.0) -> List[Dict[str, Any]]:
        """
        Retrieve relevant evidence for a query

        Args:
            query: Search query
            top_k: Number of top results to return
            min_similarity: Minimum similarity threshold

        Returns:
            List of relevant evidence with metadata
        """
        try:
            # Embed query
            query_embedding = self.embedding_engine.encode_text(query)
            if query_embedding is None:
                logger.error("Failed to embed query")
                return []

            # Search for similar vectors
            results = self.vector_search.search(query_embedding, top_k=top_k)

            # Filter by similarity and format results
            evidence = []
            for idx, similarity, metadata in results:
                if similarity >= min_similarity:
                    evidence.append({
                        'id': metadata.get('id'),
                        'title': metadata.get('title'),
                        'content': metadata.get('content'),
                        'url': metadata.get('url'),
                        'source': metadata.get('source'),
                        'published_date': metadata.get('published_date'),
                        'author': metadata.get('author'),
                        'tags': metadata.get('tags', []),
                        'credibility_score': metadata.get('credibility_score', 0.5),
                        'similarity_score': similarity,
                        'faiss_index': idx
                    })

            logger.info(f"Retrieved {len(evidence)} evidence items for query: {query[:50]}...")
            return evidence

        except Exception as e:
            logger.error(f"Error retrieving evidence: {e}")
            return []

    def get_evidence_by_id(self, evidence_id: str) -> Optional[Dict[str, Any]]:
        """
        Get evidence by ID

        Args:
            evidence_id: Evidence document ID

        Returns:
            Evidence metadata or None if not found
        """
        try:
            if evidence_id in self.vector_search.id_to_idx:
                idx = self.vector_search.id_to_idx[evidence_id]
                if idx < len(self.vector_search.metadata):
                    metadata = self.vector_search.metadata[idx]
                    return {
                        'id': evidence_id,
                        'title': metadata.get('title'),
                        'content': metadata.get('content'),
                        'url': metadata.get('url'),
                        'source': metadata.get('source'),
                        'published_date': metadata.get('published_date'),
                        'author': metadata.get('author'),
                        'tags': metadata.get('tags', []),
                        'credibility_score': metadata.get('credibility_score', 0.5)
                    }
            return None

        except Exception as e:
            logger.error(f"Error getting evidence by ID: {e}")
            return None

    def save_corpus(self, index_path: str = "evidence_index.idx",
                   metadata_path: str = "evidence_metadata.pkl") -> bool:
        """
        Save the evidence corpus to disk

        Args:
            index_path: Path to save FAISS index
            metadata_path: Path to save metadata

        Returns:
            True if successful, False otherwise
        """
        return self.vector_search.save_index(index_path, metadata_path)

    def load_corpus(self, index_path: str = "evidence_index.idx",
                   metadata_path: str = "evidence_metadata.pkl") -> bool:
        """
        Load the evidence corpus from disk

        Args:
            index_path: Path to load FAISS index from
            metadata_path: Path to load metadata from

        Returns:
            True if successful, False otherwise
        """
        return self.vector_search.load_index(index_path, metadata_path)

    def get_corpus_stats(self) -> Dict[str, Any]:
        """Get statistics about the evidence corpus"""
        stats = self.vector_search.get_stats()
        stats['embedding_engine'] = self.embedding_engine.get_model_info()
        return stats

class HybridRetriever:
    """Combines dense retrieval with cross-encoder reranking"""

    def __init__(self, evidence_retriever: EvidenceRetriever,
                 cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize hybrid retriever

        Args:
            evidence_retriever: EvidenceRetriever instance
            cross_encoder_model: HuggingFace model name for cross-encoder
        """
        self.evidence_retriever = evidence_retriever
        self.cross_encoder = None
        self.cross_encoder_model = cross_encoder_model

        # Initialize cross-encoder
        self._initialize_cross_encoder()

    def _initialize_cross_encoder(self):
        """Initialize the cross-encoder model"""
        try:
            from sentence_transformers import CrossEncoder
            logger.info(f"Loading cross-encoder model: {self.cross_encoder_model}")
            self.cross_encoder = CrossEncoder(self.cross_encoder_model)
            logger.info("Cross-encoder model loaded successfully")
        except ImportError:
            logger.error("SentenceTransformers not installed. Install with: pip install sentence-transformers")
            self.cross_encoder = None
        except Exception as e:
            logger.error(f"Error loading cross-encoder model: {e}")
            self.cross_encoder = None

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

            # Step 2: Rerank with cross-encoder if available
            if self.cross_encoder:
                logger.info(f"Reranking {len(candidates)} candidates...")
                reranked = self._rerank_with_cross_encoder(query, candidates, final_top_k)
            else:
                logger.warning("Cross-encoder not available, using similarity ranking only")
                reranked = candidates[:final_top_k]

            # Step 3: Add ranking metadata
            for i, result in enumerate(reranked):
                result['final_rank'] = i + 1
                result['ranking_method'] = 'hybrid_dense_crossencoder' if self.cross_encoder else 'dense_only'

            logger.info(f"Hybrid retrieval completed: {len(reranked)} final results")
            return reranked

        except Exception as e:
            logger.error(f"Error in hybrid retrieval: {e}")
            # Fallback to dense retrieval only
            return self.evidence_retriever.retrieve_evidence(
                query, top_k=final_top_k, min_similarity=min_similarity
            )

    def _rerank_with_cross_encoder(self, query: str, passages: List[Dict[str, Any]],
                                  top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Rerank passages using cross-encoder

        Args:
            query: Search query
            passages: List of passage dictionaries
            top_k: Number of top results to return

        Returns:
            Reranked list of passages
        """
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
            scores = self.cross_encoder.predict(query_passage_pairs)

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

            return reranked_passages

        except Exception as e:
            logger.error(f"Error in cross-encoder reranking: {e}")
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

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = self.evidence_retriever.get_corpus_stats()
        stats['cross_encoder'] = {
            'model_name': self.cross_encoder_model,
            'model_loaded': self.cross_encoder is not None,
            'model_type': 'cross_encoder'
        }
        stats['retrieval_method'] = 'hybrid'
        return stats

def main():
    """Test the FAISS vector search system with cross-encoder reranking"""
    print("Testing FAISS Vector Search with Cross-Encoder Reranking...")

    try:
        # Initialize components
        from embedding_engine import TextEmbeddingEngine

        embedding_engine = TextEmbeddingEngine()
        vector_search = FAISSVectorSearch(dimension=384)
        retriever = EvidenceRetriever(embedding_engine, vector_search)
        hybrid_retriever = HybridRetriever(retriever)

        if not embedding_engine.model or not vector_search.index:
            print("Required dependencies not available. Install with:")
            print("pip install sentence-transformers faiss-cpu numpy")
            return

        # Test data
        test_articles = [
            {
                'id': '1',
                'title': 'COVID-19 Vaccine Safety',
                'content': 'COVID-19 vaccines are safe and effective according to health experts.',
                'url': 'https://example.com/vaccine-safety',
                'source': 'Health Ministry'
            },
            {
                'id': '2',
                'title': 'Government Digital Initiative',
                'content': 'The government launched a new digital literacy program for citizens.',
                'url': 'https://example.com/digital-initiative',
                'source': 'PIB'
            },
            {
                'id': '3',
                'title': 'Misinformation on Social Media',
                'content': 'Social media platforms are working to combat misinformation and fake news.',
                'url': 'https://example.com/misinformation',
                'source': 'FactCheck'
            }
        ]

        # Embed articles
        embedded_articles = []
        for article in test_articles:
            embedding = embedding_engine.encode_text(article['content'])
            if embedding is not None:
                article_copy = article.copy()
                article_copy['embedding'] = embedding.tolist()
                embedded_articles.append(article_copy)

        # Add to vector search
        success = retriever.add_evidence(embedded_articles)
        print(f"Added test articles to corpus: {success}")

        # Test hybrid retrieval
        query = "vaccine safety and misinformation"
        results = hybrid_retriever.retrieve_and_rerank(query, initial_top_k=10, final_top_k=3)

        print(f"\nQuery: {query}")
        print(f"Found {len(results)} relevant articles:")

        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   Similarity: {result.get('similarity_score', 'N/A')}")
            print(f"   Rerank Score: {result.get('rerank_score', 'N/A')}")
            print(f"   Combined: {result.get('combined_score', 'N/A')}")
            print(f"   Source: {result['source']}")

        # Test stats
        stats = hybrid_retriever.get_performance_stats()
        print(f"\nCorpus Stats: {stats}")

        print("\nHybrid retrieval test completed successfully!")

    except ImportError as e:
        print(f"Missing dependencies: {e}")
        print("Install required packages:")
        print("pip install sentence-transformers faiss-cpu numpy")
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == '__main__':
    main()