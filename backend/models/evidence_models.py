"""
MitraVerify Evidence Engine
Database models and core functionality for fact-checking evidence retrieval
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class EvidenceSource(Base):
    """Model for fact-checking sources and news websites"""
    __tablename__ = 'evidence_sources'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    domain = Column(String(200), nullable=False, unique=True)
    url = Column(String(500), nullable=False)
    source_type = Column(String(50), nullable=False)  # 'fact_check', 'news', 'government', 'academic'
    credibility_score = Column(Float, default=0.5)  # 0-1 scale
    country = Column(String(100), default='India')
    language = Column(String(10), default='en')
    is_active = Column(Integer, default=1)  # 1=active, 0=inactive
    last_crawled = Column(DateTime)
    crawl_frequency_hours = Column(Integer, default=24)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    articles = relationship("EvidenceArticle", back_populates="source")

    def __repr__(self):
        return f"<EvidenceSource(name='{self.name}', domain='{self.domain}', credibility={self.credibility_score})>"

class EvidenceArticle(Base):
    """Model for storing crawled articles and fact-checks"""
    __tablename__ = 'evidence_articles'

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('evidence_sources.id'), nullable=False)
    url = Column(String(1000), nullable=False, unique=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    published_date = Column(DateTime)
    crawled_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Metadata
    author = Column(String(200))
    tags = Column(JSON)  # List of tags/categories
    language = Column(String(10), default='en')
    word_count = Column(Integer)

    # Content analysis
    sentiment_score = Column(Float)  # -1 to 1
    readability_score = Column(Float)  # Flesch reading ease
    fact_check_rating = Column(String(50))  # 'true', 'false', 'misleading', 'unverified'

    # Embeddings and search
    embedding = Column(JSON)  # Store the vector embedding
    embedding_model = Column(String(100))  # Model used for embedding
    search_tokens = Column(Text)  # Tokenized content for search

    # Relationships
    source = relationship("EvidenceSource", back_populates="articles")
    claims = relationship("EvidenceClaim", back_populates="article")

    # Indexes for performance
    __table_args__ = (
        Index('idx_source_published', 'source_id', 'published_date'),
        Index('idx_url', 'url'),
        Index('idx_published_date', 'published_date'),
        Index('idx_fact_check_rating', 'fact_check_rating'),
    )

    def __repr__(self):
        return f"<EvidenceArticle(title='{self.title[:50]}...', source='{self.source.name if self.source else None}')>"

class EvidenceClaim(Base):
    """Model for storing specific claims and their fact-check results"""
    __tablename__ = 'evidence_claims'

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('evidence_articles.id'), nullable=False)
    claim_text = Column(Text, nullable=False)
    fact_check_result = Column(String(50), nullable=False)  # 'true', 'false', 'misleading', 'unverified'
    confidence_score = Column(Float, nullable=False)  # 0-1
    explanation = Column(Text)
    fact_checker = Column(String(200))  # Name of fact-checking organization
    checked_date = Column(DateTime, default=datetime.utcnow)

    # Evidence details
    evidence_urls = Column(JSON)  # List of supporting/contradicting URLs
    categories = Column(JSON)  # Categories like 'politics', 'health', 'science'
    tags = Column(JSON)  # Specific tags

    # Relationships
    article = relationship("EvidenceArticle", back_populates="claims")

    def __repr__(self):
        return f"<EvidenceClaim(claim='{self.claim_text[:50]}...', result='{self.fact_check_result}')>"

class SearchQuery(Base):
    """Model for storing search queries and their results for analytics"""
    __tablename__ = 'search_queries'

    id = Column(Integer, primary_key=True)
    query_text = Column(Text, nullable=False)
    search_type = Column(String(50), default='semantic')  # 'semantic', 'keyword', 'fact_check'
    user_id = Column(String(100))  # For user tracking
    timestamp = Column(DateTime, default=datetime.utcnow)
    results_count = Column(Integer, default=0)
    processing_time_ms = Column(Integer)

    # Search parameters
    filters = Column(JSON)  # Applied filters
    top_results = Column(JSON)  # Top 5 results for analytics

    def __repr__(self):
        return f"<SearchQuery(query='{self.query_text[:50]}...', type='{self.search_type}')>"

class EvidenceEngineConfig(Base):
    """Configuration table for the evidence engine"""
    __tablename__ = 'evidence_engine_config'

    id = Column(Integer, primary_key=True)
    config_key = Column(String(100), nullable=False, unique=True)
    config_value = Column(JSON, nullable=False)
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<EvidenceEngineConfig(key='{self.config_key}', value='{self.config_value}')>"

def create_database_engine(database_url: str = None):
    """Create SQLAlchemy engine for the evidence database"""
    if database_url is None:
        database_url = os.getenv('EVIDENCE_DATABASE_URL', 'sqlite:///evidence_corpus.db')

    engine = create_engine(database_url, echo=False)
    return engine

def create_tables(engine):
    """Create all tables in the database"""
    Base.metadata.create_all(engine)

def get_session_factory(engine):
    """Create session factory for database operations"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal

def init_database():
    """Initialize the evidence database with default data"""
    engine = create_database_engine()
    create_tables(engine)

    SessionLocal = get_session_factory(engine)
    session = SessionLocal()

    try:
        # Add default fact-checking sources
        default_sources = [
            {
                'name': 'Alt News',
                'domain': 'altnews.in',
                'url': 'https://www.altnews.in',
                'source_type': 'fact_check',
                'credibility_score': 0.95,
                'country': 'India',
                'language': 'en'
            },
            {
                'name': 'BOOM Fact Check',
                'domain': 'boomlive.in',
                'url': 'https://www.boomlive.in',
                'source_type': 'fact_check',
                'credibility_score': 0.92,
                'country': 'India',
                'language': 'en'
            },
            {
                'name': 'Factly',
                'domain': 'factly.in',
                'url': 'https://factly.in',
                'source_type': 'fact_check',
                'credibility_score': 0.90,
                'country': 'India',
                'language': 'en'
            },
            {
                'name': 'Vishvas News',
                'domain': 'vishvasnews.com',
                'url': 'https://www.vishvasnews.com',
                'source_type': 'fact_check',
                'credibility_score': 0.88,
                'country': 'India',
                'language': 'en'
            },
            {
                'name': 'The Hindu',
                'domain': 'thehindu.com',
                'url': 'https://www.thehindu.com',
                'source_type': 'news',
                'credibility_score': 0.92,
                'country': 'India',
                'language': 'en'
            },
            {
                'name': 'PIB India',
                'domain': 'pib.gov.in',
                'url': 'https://www.pib.gov.in',
                'source_type': 'government',
                'credibility_score': 0.95,
                'country': 'India',
                'language': 'en'
            }
        ]

        for source_data in default_sources:
            # Check if source already exists
            existing = session.query(EvidenceSource).filter_by(domain=source_data['domain']).first()
            if not existing:
                source = EvidenceSource(**source_data)
                session.add(source)

        session.commit()
        print("Evidence database initialized with default sources")

    except Exception as e:
        session.rollback()
        print(f"Error initializing database: {e}")
    finally:
        session.close()

if __name__ == '__main__':
    init_database()