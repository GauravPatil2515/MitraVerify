"""
Test script for MitraVerify Cross-Encoder Reranker
Tests the hybrid retrieval system with cross-encoder reranking
"""

import sys
import os
import logging

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_cross_encoder_reranker():
    """Test the cross-encoder reranker functionality"""
    print("=" * 60)
    print("Testing Cross-Encoder Reranker")
    print("=" * 60)

    try:
        from models.reranker import CrossEncoderReranker

        # Initialize cross-encoder
        reranker = CrossEncoderReranker()

        if not reranker.model:
            print("❌ Cross-encoder model not loaded")
            print("   Install with: pip install sentence-transformers")
            return False

        print("✅ Cross-encoder model loaded successfully")

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

        print(f"\nOriginal passages (ranked by similarity):")
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

        print("\n✅ Cross-encoder reranker test completed successfully!")
        return True

    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("   Install required packages:")
        print("   pip install sentence-transformers numpy")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_hybrid_retriever():
    """Test the hybrid retriever with FAISS and cross-encoder"""
    print("\n" + "=" * 60)
    print("Testing Hybrid Retriever")
    print("=" * 60)

    try:
        from models.vector_search import HybridRetriever, EvidenceRetriever, FAISSVectorSearch
        from models.embedding_engine import TextEmbeddingEngine

        # Initialize components
        embedding_engine = TextEmbeddingEngine()
        vector_search = FAISSVectorSearch(dimension=384)
        retriever = EvidenceRetriever(embedding_engine, vector_search)
        hybrid_retriever = HybridRetriever(retriever)

        if not embedding_engine.model or not vector_search.index:
            print("❌ Required dependencies not available")
            print("   Install with: pip install sentence-transformers faiss-cpu numpy")
            return False

        print("✅ Hybrid retriever components initialized")

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
        print(f"✅ Added {len(embedded_articles)} test articles to corpus: {success}")

        # Test hybrid retrieval
        query = "vaccine safety and misinformation"
        results = hybrid_retriever.retrieve_and_rerank(query, initial_top_k=10, final_top_k=3)

        print(f"\nQuery: '{query}'")
        print(f"Found {len(results)} relevant articles:")

        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   Similarity: {result.get('similarity_score', 'N/A')}")
            print(f"   Rerank Score: {result.get('rerank_score', 'N/A')}")
            print(f"   Combined: {result.get('combined_score', 'N/A')}")
            print(f"   Source: {result['source']}")

        # Test stats
        stats = hybrid_retriever.get_performance_stats()
        print(f"\nCorpus Stats:")
        print(f"   Total vectors: {stats.get('total_vectors', 'N/A')}")
        print(f"   Cross-encoder loaded: {stats.get('cross_encoder', {}).get('model_loaded', False)}")

        print("\n✅ Hybrid retriever test completed successfully!")
        return True

    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("   Install required packages:")
        print("   pip install sentence-transformers faiss-cpu numpy")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_flask_integration():
    """Test Flask app integration with hybrid retriever"""
    print("\n" + "=" * 60)
    print("Testing Flask Integration")
    print("=" * 60)

    try:
        # Import Flask app
        from app_simple import app, get_hybrid_retriever, get_evidence_retriever

        with app.app_context():
            # Test retriever initialization
            base_retriever = get_evidence_retriever()
            hybrid_retriever = get_hybrid_retriever()

            if base_retriever:
                print("✅ Base evidence retriever initialized")
            else:
                print("❌ Base evidence retriever not available")

            if hybrid_retriever:
                print("✅ Hybrid retriever with cross-encoder initialized")
            else:
                print("❌ Hybrid retriever not available")

            # Test stats endpoint
            with app.test_client() as client:
                # Mock authentication (in a real test, you'd set up proper auth)
                # For now, we'll just test the initialization
                print("✅ Flask app context test completed")

        return True

    except ImportError as e:
        print(f"❌ Missing Flask dependencies: {e}")
        return False
    except Exception as e:
        print(f"❌ Flask integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("MitraVerify Cross-Encoder Reranker Test Suite")
    print("============================================")

    test_results = []

    # Test cross-encoder reranker
    test_results.append(("Cross-Encoder Reranker", test_cross_encoder_reranker()))

    # Test hybrid retriever
    test_results.append(("Hybrid Retriever", test_hybrid_retriever()))

    # Test Flask integration
    test_results.append(("Flask Integration", test_flask_integration()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Cross-encoder reranker is ready.")
    else:
        print("⚠️  Some tests failed. Check dependencies and configuration.")

    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)