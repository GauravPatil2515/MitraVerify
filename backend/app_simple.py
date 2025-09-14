"""
Simple test version of MitraVerify Backend
"""

import os
import logging
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Basic configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///mitraverify_test.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
cors = CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Simple Verification model
class Verification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    result = db.Column(db.String(20), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    content_type = db.Column(db.String(20), default='text')
    analysis_details = db.Column(db.Text, default='{}')

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/verify', methods=['POST'])
def verify_content():
    """Simple content verification endpoint"""
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'error': 'Content is required'}), 400
        
        content = data['content']
        
        # Simple verification logic
        # Check for obvious spam/misinformation patterns
        suspicious_words = ['urgent', 'breaking', 'secret', 'conspiracy', 'leaked']
        suspicious_count = sum(1 for word in suspicious_words if word.lower() in content.lower())
        
        if suspicious_count >= 2:
            result = 'questionable'
            confidence = 0.8
        elif suspicious_count == 1:
            result = 'questionable'
            confidence = 0.6
        else:
            result = 'verified'
            confidence = 0.7
        
        # Save verification
        verification = Verification(
            content=content[:500],  # Store first 500 chars
            result=result,
            confidence_score=confidence,
            content_type='text',
            analysis_details=str({
                'suspicious_words_found': suspicious_count,
                'content_length': len(content)
            })
        )
        db.session.add(verification)
        db.session.commit()
        
        return jsonify({
            'verification_id': verification.id,
            'result': result,
            'confidence_score': confidence,
            'analysis_details': {
                'suspicious_words_found': suspicious_count,
                'content_length': len(content)
            }
        })
    
    except Exception as e:
        logger.error(f"Verification error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        if not data or not all(key in data for key in ['username', 'email', 'password']):
            return jsonify({'error': 'Username, email, and password are required'}), 400
        
        # Check if user exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 409
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password'])
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user.id,
            'username': user.username
        }), 201
    
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users (for testing)"""
    users = User.query.all()
    return jsonify({
        'users': [{'id': u.id, 'username': u.username, 'email': u.email} for u in users],
        'count': len(users)
    })

@app.route('/api/verifications', methods=['GET'])
def get_verifications():
    """Get all verifications (for testing)"""
    verifications = Verification.query.order_by(Verification.timestamp.desc()).limit(10).all()
    return jsonify({
        'verifications': [{
            'id': v.id,
            'content': v.content,
            'result': v.result,
            'confidence_score': v.confidence_score,
            'timestamp': v.timestamp.isoformat()
        } for v in verifications],
        'count': len(verifications)
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get basic statistics"""
    total_users = User.query.count()
    total_verifications = Verification.query.count()
    verified_count = Verification.query.filter_by(result='verified').count()
    questionable_count = Verification.query.filter_by(result='questionable').count()
    false_count = Verification.query.filter_by(result='false').count()
    
    return jsonify({
        'total_users': total_users,
        'total_verifications': total_verifications,
        'verification_breakdown': {
            'verified': verified_count,
            'questionable': questionable_count,
            'false': false_count
        }
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

# Initialize database
def create_tables():
    """Create database tables"""
    with app.app_context():
        db.create_all()
        logger.info("Database tables created successfully")

if __name__ == '__main__':
    create_tables()
    logger.info("Starting MitraVerify Test Server...")
    app.run(debug=True, host='0.0.0.0', port=5001)
