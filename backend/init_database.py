#!/usr/bin/env python3
"""
Database Initialization Script for MitraVerify
This script creates all necessary database tables and populates initial data.
"""

import os
import sys
import logging
from datetime import datetime
from werkzeug.security import generate_password_hash

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config.settings import DevelopmentConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create Flask application for database initialization."""
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    
    # Ensure upload directory exists
    upload_dir = app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    return app

def initialize_database():
    """Initialize database with all tables and sample data."""
    try:
        app = create_app()
        
        with app.app_context():
            # Import all models to ensure they're registered
            from app import db, User, Verification, EducationalProgress, Feedback, MisinformationTrend
            
            logger.info("Creating database tables...")
            
            # Drop all tables first (for clean initialization)
            db.drop_all()
            
            # Create all tables
            db.create_all()
            
            logger.info("Database tables created successfully!")
            
            # Create sample admin user
            admin_user = User(
                username='admin',
                email='admin@mitraverify.com',
                password_hash=generate_password_hash('admin123'),
                literacy_score=95.0,
                preferred_language='en'
            )
            
            # Create sample regular user
            demo_user = User(
                username='demo_user',
                email='demo@mitraverify.com',
                password_hash=generate_password_hash('demo123'),
                literacy_score=65.0,
                preferred_language='en'
            )
            
            db.session.add(admin_user)
            db.session.add(demo_user)
            db.session.commit()
            
            logger.info("Sample users created:")
            logger.info("- Admin: admin@mitraverify.com / admin123")
            logger.info("- Demo: demo@mitraverify.com / demo123")
            
            # Create sample verification records
            sample_verification = Verification(
                user_id=demo_user.id,
                content_hash='sample_hash_123',
                content_type='text',
                original_content='This is a sample text for testing verification system.',
                result='verified',
                confidence_score=0.85,
                analysis_details={
                    'credibility_score': 0.85,
                    'misinformation_indicators': [],
                    'sentiment_analysis': {'polarity': 0.1, 'subjectivity': 0.3}
                },
                processing_time=1.2
            )
            
            db.session.add(sample_verification)
            
            # Create sample educational progress
            sample_progress = EducationalProgress(
                user_id=demo_user.id,
                module_id='basic_fact_checking',
                module_name='Basic Fact Checking',
                completion_status='completed',
                score=85.0,
                completed_at=datetime.utcnow(),
                time_spent=45
            )
            
            db.session.add(sample_progress)
            
            # Create sample feedback
            sample_feedback = Feedback(
                verification_id=1,  # Will be the sample verification
                user_id=demo_user.id,
                user_rating=4,
                accuracy_rating=4,
                comments='The verification was helpful and accurate.'
            )
            
            db.session.add(sample_feedback)
            
            # Create sample misinformation trend
            sample_trend = MisinformationTrend(
                region='india',
                category='health',
                keywords=['covid', 'vaccine', 'cure'],
                frequency=15,
                severity='medium'
            )
            
            db.session.add(sample_trend)
            
            db.session.commit()
            
            logger.info("Sample data inserted successfully!")
            
            # Verify database
            user_count = User.query.count()
            verification_count = Verification.query.count()
            
            logger.info(f"Database verification:")
            logger.info(f"- Users: {user_count}")
            logger.info(f"- Verifications: {verification_count}")
            
            logger.info("Database initialization completed successfully!")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

if __name__ == '__main__':
    initialize_database()
