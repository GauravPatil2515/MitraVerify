#!/usr/bin/env python3
"""
Simple Database Initialization for MitraVerify
"""

import sqlite3
from pathlib import Path
import hashlib
import os

def create_database():
    """Create a clean database with all required tables"""
    db_path = Path("mitraverify_dev.db")
    
    # Remove existing database
    if db_path.exists():
        os.remove(db_path)
        print("🗑️ Removed existing database")
    
    # Create new database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(128) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            media_literacy_score FLOAT DEFAULT 50.0,
            total_verifications INTEGER DEFAULT 0,
            correct_verifications INTEGER DEFAULT 0,
            user_level VARCHAR(20) DEFAULT 'Beginner'
        )
    ''')
    
    # Create verification_records table
    cursor.execute('''
        CREATE TABLE verification_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            content TEXT NOT NULL,
            content_type VARCHAR(20) NOT NULL,
            result VARCHAR(20) NOT NULL,
            confidence_score FLOAT,
            analysis_details TEXT,
            evidence TEXT,
            processing_time FLOAT,
            language VARCHAR(10) DEFAULT 'en',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create educational_progress table
    cursor.execute('''
        CREATE TABLE educational_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            module_name VARCHAR(100) NOT NULL,
            completion_percentage FLOAT DEFAULT 0.0,
            quiz_scores TEXT,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_time_spent INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create feedback table
    cursor.execute('''
        CREATE TABLE feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            verification_id INTEGER,
            feedback_type VARCHAR(50),
            rating INTEGER,
            comments TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (verification_id) REFERENCES verification_records (id)
        )
    ''')
    
    # Create misinformation_trends table
    cursor.execute('''
        CREATE TABLE misinformation_trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_hash VARCHAR(64) UNIQUE,
            content_snippet TEXT,
            category VARCHAR(50),
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_reports INTEGER DEFAULT 1,
            confidence_score FLOAT,
            status VARCHAR(20) DEFAULT 'active'
        )
    ''')
    
    print("✅ Created all database tables")
    
    # Insert sample users
    sample_users = [
        ('admin', 'admin@mitraverify.com', 'admin123'),
        ('demo_user', 'demo@example.com', 'demo123'),
        ('test_user', 'test@example.com', 'test123')
    ]
    
    for username, email, password in sample_users:
        # Simple password hashing (in production, use bcrypt)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, media_literacy_score, user_level)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, password_hash, 50.0, 'Beginner'))
    
    print("✅ Inserted sample users (admin/admin123, demo_user/demo123, test_user/test123)")
    
    # Insert sample verification records
    cursor.execute('''
        INSERT INTO verification_records 
        (user_id, content, content_type, result, confidence_score, analysis_details, language)
        VALUES (1, 'Sample content for testing verification', 'text', 'verified', 0.8, 
                '{"suspicious_words": 0, "credibility_score": 0.9}', 'en')
    ''')
    
    print("✅ Inserted sample verification records")
    
    # Insert sample educational progress
    cursor.execute('''
        INSERT INTO educational_progress 
        (user_id, module_name, completion_percentage)
        VALUES (1, 'Media Literacy Basics', 75.0)
    ''')
    
    print("✅ Inserted sample educational progress")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database created successfully: {db_path.absolute()}")
    return True

def verify_database():
    """Verify the database was created correctly"""
    db_path = Path("mitraverify_dev.db")
    
    if not db_path.exists():
        print("❌ Database file not found")
        return False
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    required_tables = ['users', 'verification_records', 'educational_progress', 'feedback', 'misinformation_trends']
    
    for table in required_tables:
        if table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"✅ Table '{table}': {count} records")
        else:
            print(f"❌ Table '{table}': Missing")
            return False
    
    conn.close()
    return True

if __name__ == "__main__":
    print("🔧 INITIALIZING MITRAVERIFY DATABASE")
    print("=" * 40)
    
    if create_database():
        print("\n🔍 VERIFYING DATABASE")
        print("=" * 25)
        verify_database()
        print("\n🎉 Database initialization completed successfully!")
    else:
        print("❌ Database initialization failed")
