"""
MitraVerify Text Embedding System
Uses SentenceTransformers for encoding passages and claims
"""

import os
import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import pickle
from datetime import datetime
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextEmbeddingEngine:
    """Text embedding engine using SentenceTransformers"""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the embedding engine

        Args:
            model_name: HuggingFace model name for sentence transformers
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.embedding_dim = 384  # Default for MiniLM

        # Cache for embeddings
        self.embedding_cache = {}
        self.cache_file = "embedding_cache.pkl"

        # Load cache if exists
        self._load_cache()

        # Initialize model
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the SentenceTransformer model"""
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading SentenceTransformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Model loaded successfully. Embedding dimension: {self.embedding_dim}")
        except ImportError:
            logger.error("SentenceTransformers not installed. Install with: pip install sentence-transformers")
            self.model = None
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None

    def _load_cache(self):
        """Load embedding cache from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'rb') as f:
                    self.embedding_cache = pickle.load(f)
                logger.info(f"Loaded {len(self.embedding_cache)} cached embeddings")
        except Exception as e:
            logger.warning(f"Could not load embedding cache: {e}")
            self.embedding_cache = {}

    def _save_cache(self):
        """Save embedding cache to file"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.embedding_cache, f)
            logger.info(f"Saved {len(self.embedding_cache)} embeddings to cache")
        except Exception as e:
            logger.error(f"Could not save embedding cache: {e}")

    def _get_text_hash(self, text: str) -> str:
        """Generate hash for text caching"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def encode_text(self, text: str, use_cache: bool = True) -> Optional[np.ndarray]:
        """
        Encode text into vector embedding

        Args:
            text: Text to encode
            use_cache: Whether to use cached embeddings

        Returns:
            Numpy array of embedding vector, or None if failed
        """
        if not self.model:
            logger.error("Model not initialized")
            return None

        if not text or not text.strip():
            return np.zeros(self.embedding_dim)

        # Check cache
        text_hash = self._get_text_hash(text)
        if use_cache and text_hash in self.embedding_cache:
            return self.embedding_cache[text_hash]

        try:
            # Encode text
            embedding = self.model.encode(text, convert_to_numpy=True, normalize_embeddings=True)

            # Cache the result
            if use_cache:
                self.embedding_cache[text_hash] = embedding

                # Save cache periodically (every 100 new embeddings)
                if len(self.embedding_cache) % 100 == 0:
                    self._save_cache()

            return embedding

        except Exception as e:
            logger.error(f"Error encoding text: {e}")
            return None

    def encode_batch(self, texts: List[str], batch_size: int = 32, use_cache: bool = True) -> List[Optional[np.ndarray]]:
        """
        Encode multiple texts in batch

        Args:
            texts: List of texts to encode
            batch_size: Batch size for encoding
            use_cache: Whether to use cached embeddings

        Returns:
            List of embedding vectors
        """
        if not self.model:
            logger.error("Model not initialized")
            return [None] * len(texts)

        embeddings = []
        uncached_texts = []
        uncached_indices = []

        # Check cache first
        for i, text in enumerate(texts):
            if not text or not text.strip():
                embeddings.append(np.zeros(self.embedding_dim))
                continue

            text_hash = self._get_text_hash(text)
            if use_cache and text_hash in self.embedding_cache:
                embeddings.append(self.embedding_cache[text_hash])
            else:
                embeddings.append(None)
                uncached_texts.append(text)
                uncached_indices.append(i)

        # Encode uncached texts in batch
        if uncached_texts:
            try:
                logger.info(f"Encoding {len(uncached_texts)} uncached texts in batch")
                batch_embeddings = self.model.encode(
                    uncached_texts,
                    batch_size=batch_size,
                    convert_to_numpy=True,
                    normalize_embeddings=True
                )

                # Store in cache and update results
                for i, (text, embedding) in enumerate(zip(uncached_texts, batch_embeddings)):
                    original_index = uncached_indices[i]
                    embeddings[original_index] = embedding

                    if use_cache:
                        text_hash = self._get_text_hash(text)
                        self.embedding_cache[text_hash] = embedding

            except Exception as e:
                logger.error(f"Error in batch encoding: {e}")
                # Fill failed encodings with zeros
                for i in uncached_indices:
                    if embeddings[i] is None:
                        embeddings[i] = np.zeros(self.embedding_dim)

        # Save cache if we added new embeddings
        if uncached_texts and use_cache:
            self._save_cache()

        return embeddings

    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score (0-1)
        """
        try:
            # Cosine similarity
            dot_product = np.dot(embedding1, embedding2)
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)
            return max(0.0, min(1.0, similarity))  # Clamp to [0, 1]

        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return 0.0

    def find_similar_texts(self, query_embedding: np.ndarray,
                          text_embeddings: List[np.ndarray],
                          top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Find most similar texts to query

        Args:
            query_embedding: Query embedding vector
            text_embeddings: List of text embeddings to search
            top_k: Number of top results to return

        Returns:
            List of (index, similarity_score) tuples
        """
        similarities = []

        for i, text_embedding in enumerate(text_embeddings):
            if text_embedding is not None:
                similarity = self.compute_similarity(query_embedding, text_embedding)
                similarities.append((i, similarity))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]

    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for embedding

        Args:
            text: Raw text

        Returns:
            Preprocessed text
        """
        if not text:
            return ""

        # Basic preprocessing
        text = text.strip()

        # Remove excessive whitespace
        text = ' '.join(text.split())

        # Limit length (SentenceTransformers works better with shorter texts)
        if len(text) > 512:
            text = text[:512] + "..."

        return text

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            'model_name': self.model_name,
            'embedding_dimension': self.embedding_dim,
            'model_loaded': self.model is not None,
            'cache_size': len(self.embedding_cache),
            'cache_file': self.cache_file
        }

class EvidenceEmbedder:
    """High-level interface for embedding evidence corpus"""

    def __init__(self, embedding_engine: TextEmbeddingEngine):
        self.embedding_engine = embedding_engine

    def embed_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Embed a single article

        Args:
            article_data: Article data dictionary

        Returns:
            Article data with embedding added
        """
        try:
            # Combine title and content for embedding
            title = article_data.get('title', '')
            content = article_data.get('content', '')

            # Create embedding text
            embedding_text = f"{title} {content}"
            embedding_text = self.embedding_engine.preprocess_text(embedding_text)

            # Generate embedding
            embedding = self.embedding_engine.encode_text(embedding_text)

            if embedding is not None:
                article_data['embedding'] = embedding.tolist()
                article_data['embedding_model'] = self.embedding_engine.model_name
                article_data['embedding_date'] = datetime.now().isoformat()

            return article_data

        except Exception as e:
            logger.error(f"Error embedding article: {e}")
            return article_data

    def embed_corpus(self, articles: List[Dict[str, Any]], batch_size: int = 32) -> List[Dict[str, Any]]:
        """
        Embed multiple articles in batch

        Args:
            articles: List of article data dictionaries
            batch_size: Batch size for processing

        Returns:
            List of articles with embeddings added
        """
        logger.info(f"Embedding {len(articles)} articles")

        # Prepare texts for batch embedding
        texts = []
        for article in articles:
            title = article.get('title', '')
            content = article.get('content', '')
            embedding_text = f"{title} {content}"
            embedding_text = self.embedding_engine.preprocess_text(embedding_text)
            texts.append(embedding_text)

        # Generate embeddings in batch
        embeddings = self.embedding_engine.encode_batch(texts, batch_size=batch_size)

        # Add embeddings to articles
        for i, (article, embedding) in enumerate(zip(articles, embeddings)):
            if embedding is not None:
                article['embedding'] = embedding.tolist()
                article['embedding_model'] = self.embedding_engine.model_name
                article['embedding_date'] = datetime.now().isoformat()

            if (i + 1) % 50 == 0:
                logger.info(f"Embedded {i + 1}/{len(articles)} articles")

        logger.info(f"Completed embedding {len(articles)} articles")
        return articles

    def embed_query(self, query: str) -> Optional[np.ndarray]:
        """
        Embed a search query

        Args:
            query: Search query text

        Returns:
            Query embedding vector
        """
        try:
            processed_query = self.embedding_engine.preprocess_text(query)
            return self.embedding_engine.encode_text(processed_query)
        except Exception as e:
            logger.error(f"Error embedding query: {e}")
            return None

def main():
    """Test the embedding system"""
    print("Testing Text Embedding Engine...")

    # Initialize embedding engine
    engine = TextEmbeddingEngine()

    if not engine.model:
        print("SentenceTransformers model not loaded. Install with: pip install sentence-transformers")
        return

    # Test single text embedding
    test_text = "This is a test article about misinformation detection in India."
    embedding = engine.encode_text(test_text)

    if embedding is not None:
        print(f"Successfully embedded text. Vector dimension: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")

    # Test batch embedding
    test_texts = [
        "COVID-19 vaccine is safe and effective.",
        "Government plans to ban social media platforms.",
        "New education policy focuses on digital literacy.",
        "Fact-checking helps combat misinformation."
    ]

    embeddings = engine.encode_batch(test_texts)
    print(f"Successfully embedded {len(embeddings)} texts in batch")

    # Test similarity
    if len(embeddings) >= 2:
        similarity = engine.compute_similarity(embeddings[0], embeddings[1])
        print(f"Similarity between first two texts: {similarity:.3f}")

    # Test evidence embedder
    embedder = EvidenceEmbedder(engine)

    test_article = {
        'title': 'Test Article',
        'content': 'This is a test article about fact-checking and misinformation detection.',
        'url': 'https://example.com/test'
    }

    embedded_article = embedder.embed_article(test_article)
    print(f"Article embedding completed: {'embedding' in embedded_article}")

    print("Embedding system test completed!")

if __name__ == '__main__':
    main()