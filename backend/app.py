"""
MitraVerify Backend Application
AI-Powered Misinformation Detection Platform

Main Flask application with comprehensive API endpoints for content verification,
user management, educational features, and analytics.
"""

import os
import logging
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify, current_app
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import redis

from models.verification_engine import VerificationEngine
from models.education_engine import EducationEngine
from utils.text_analyzer import TextAnalyzer
from utils.image_analyzer import ImageAnalyzer
from utils.cultural_context import CulturalContextAnalyzer
from config.settings import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db = SQLAlchemy(app)
cors = CORS(app)
jwt = JWTManager(app)

# Initialize Redis for rate limiting (fallback to memory if Redis unavailable)
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()  # Test connection
    storage_uri = "redis://localhost:6379"
except:
    storage_uri = "memory://"

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per day", "100 per hour"],
    storage_uri=storage_uri
)
limiter.init_app(app)

# Initialize AI engines
verification_engine = VerificationEngine()
education_engine = EducationEngine()
text_analyzer = TextAnalyzer()
image_analyzer = ImageAnalyzer()
cultural_analyzer = CulturalContextAnalyzer()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger(__name__)

# Database Models
class User(db.Model):
    """User model for authentication and tracking"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    literacy_score = db.Column(db.Float, default=0.0)
    preferred_language = db.Column(db.String(10), default='en')
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    verifications = db.relationship('Verification', backref='user', lazy=True)
    progress = db.relationship('EducationalProgress', backref='user', lazy=True)
    feedback = db.relationship('Feedback', backref='user', lazy=True)

class Verification(db.Model):
    """Content verification records"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content_hash = db.Column(db.String(64), nullable=False)
    content_type = db.Column(db.String(20), nullable=False)  # text, image, url, video
    original_content = db.Column(db.Text)
    result = db.Column(db.String(20), nullable=False)  # verified, questionable, false
    confidence_score = db.Column(db.Float, nullable=False)
    analysis_details = db.Column(db.JSON)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    processing_time = db.Column(db.Float)  # in seconds

class EducationalProgress(db.Model):
    """User's learning progress tracking"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    module_id = db.Column(db.String(50), nullable=False)
    module_name = db.Column(db.String(200), nullable=False)
    completion_status = db.Column(db.String(20), default='not_started')
    score = db.Column(db.Float, default=0.0)
    completed_at = db.Column(db.DateTime)
    time_spent = db.Column(db.Integer)  # in minutes

class Feedback(db.Model):
    """User feedback on verification accuracy"""
    id = db.Column(db.Integer, primary_key=True)
    verification_id = db.Column(db.Integer, db.ForeignKey('verification.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    accuracy_rating = db.Column(db.Integer, nullable=False)  # 1-5 accuracy
    comments = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class MisinformationTrend(db.Model):
    """Tracking misinformation trends"""
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    keywords = db.Column(db.JSON)
    frequency = db.Column(db.Integer, default=1)
    severity = db.Column(db.String(20), default='medium')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Authentication decorator
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != app.config.get('API_KEY'):
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Helper functions
def calculate_user_literacy_score(user_id):
    """Calculate user's digital literacy score based on verification history"""
    try:
        verifications = Verification.query.filter_by(user_id=user_id).all()
        if not verifications:
            return 0.0
        
        correct_verifications = 0
        total_verifications = len(verifications)
        
        for verification in verifications:
            feedback = Feedback.query.filter_by(verification_id=verification.id).first()
            if feedback and feedback.accuracy_rating >= 4:
                correct_verifications += 1
        
        base_score = (correct_verifications / total_verifications) * 100
        
        # Bonus for educational progress
        completed_modules = EducationalProgress.query.filter_by(
            user_id=user_id, 
            completion_status='completed'
        ).count()
        
        education_bonus = min(completed_modules * 5, 20)  # Max 20 points bonus
        
        final_score = min(base_score + education_bonus, 100)
        return round(final_score, 2)
    
    except Exception as e:
        logger.error(f"Error calculating literacy score: {e}")
        return 0.0

# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': app.config.get('VERSION', '1.0.0')
    })

@app.route('/api/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 409
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            preferred_language=data.get('preferred_language', 'en')
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'literacy_score': user.literacy_score,
                'preferred_language': user.preferred_language
            }
        }), 201
    
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            access_token = create_access_token(identity=user.id)
            
            return jsonify({
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'literacy_score': user.literacy_score,
                    'preferred_language': user.preferred_language
                }
            })
        
        return jsonify({'error': 'Invalid credentials'}), 401
    
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """Get user statistics and analytics"""
    try:
        user_id = get_jwt_identity()
        
        # Get user verification stats
        verifications = Verification.query.filter_by(user_id=user_id).all()
        total_verifications = len(verifications)
        
        # Count by result
        true_count = sum(1 for v in verifications if v.result_summary.get('credibility_score', 0) > 0.7)
        false_count = sum(1 for v in verifications if v.result_summary.get('credibility_score', 0) < 0.3)
        uncertain_count = total_verifications - true_count - false_count
        
        # Get educational progress
        completed_modules = EducationalProgress.query.filter_by(
            user_id=user_id,
            completion_status='completed'
        ).count()
        
        # Get recent activity (last 30 days)
        recent_verifications = Verification.query.filter(
            Verification.user_id == user_id,
            Verification.timestamp > datetime.utcnow() - timedelta(days=30)
        ).count()
        
        # Calculate accuracy score
        user = User.query.get(user_id)
        literacy_score = calculate_user_literacy_score(user_id)
        
        stats = {
            'total_verifications': total_verifications,
            'true_content': true_count,
            'false_content': false_count,
            'uncertain_content': uncertain_count,
            'completed_modules': completed_modules,
            'recent_activity': recent_verifications,
            'literacy_score': literacy_score,
            'accuracy_rate': round((true_count / total_verifications * 100) if total_verifications > 0 else 0, 1),
            'user_level': 'Beginner' if literacy_score < 30 else 'Intermediate' if literacy_score < 70 else 'Expert'
        }
        
        return jsonify(stats)
    
    except Exception as e:
        logger.error(f"User stats error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/profile', methods=['GET', 'PUT'])
@jwt_required()
def user_profile():
    """Get or update user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if request.method == 'GET':
            return jsonify({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'preferred_language': user.preferred_language,
                    'literacy_score': user.literacy_score,
                    'created_at': user.created_at.isoformat(),
                    'last_login': user.last_login.isoformat() if user.last_login else None
                }
            })
        
        elif request.method == 'PUT':
            data = request.get_json()
            
            # Update allowed fields
            if 'preferred_language' in data:
                user.preferred_language = data['preferred_language']
            
            db.session.commit()
            
            return jsonify({
                'message': 'Profile updated successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'preferred_language': user.preferred_language,
                    'literacy_score': user.literacy_score
                }
            })
    
    except Exception as e:
        logger.error(f"Profile error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/verify', methods=['POST'])
@limiter.limit("50 per minute")
@jwt_required()
def verify_content():
    """Main content verification endpoint"""
    start_time = datetime.utcnow()
    
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        content = data.get('content')
        content_type = data.get('content_type', 'text')
        language = data.get('language', 'en')
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        # Generate content hash for deduplication
        import hashlib
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Check if content was recently verified
        recent_verification = Verification.query.filter_by(
            content_hash=content_hash
        ).filter(
            Verification.timestamp > datetime.utcnow() - timedelta(hours=24)
        ).first()
        
        if recent_verification:
            logger.info(f"Using cached verification for content hash: {content_hash}")
            return jsonify({
                'verification_id': recent_verification.id,
                'result': recent_verification.result,
                'confidence_score': recent_verification.confidence_score,
                'analysis_details': recent_verification.analysis_details,
                'cached': True
            })
        
        # Perform verification
        verification_result = verification_engine.verify_content(
            content=content,
            content_type=content_type,
            language=language,
            user_context={'user_id': user_id}
        )
        
        # Enhance with cultural context
        cultural_analysis = cultural_analyzer.analyze_cultural_context(
            content, language
        )
        
        # Combine results
        analysis_details = {
            **verification_result.get('analysis_details', {}),
            'cultural_context': cultural_analysis,
            'processing_metadata': {
                'language': language,
                'content_type': content_type,
                'timestamp': datetime.utcnow().isoformat()
            }
        }
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Save verification record
        verification = Verification(
            user_id=user_id,
            content_hash=content_hash,
            content_type=content_type,
            original_content=content[:1000],  # Store first 1000 chars
            result=verification_result['result'],
            confidence_score=verification_result['confidence_score'],
            analysis_details=analysis_details,
            processing_time=processing_time
        )
        
        db.session.add(verification)
        db.session.commit()
        
        # Update user literacy score
        user = User.query.get(user_id)
        user.literacy_score = calculate_user_literacy_score(user_id)
        db.session.commit()
        
        return jsonify({
            'verification_id': verification.id,
            'result': verification_result['result'],
            'confidence_score': verification_result['confidence_score'],
            'analysis_details': analysis_details,
            'processing_time': processing_time,
            'educational_tip': verification_result.get('educational_tip'),
            'sources': verification_result.get('sources', [])
        })
    
    except Exception as e:
        logger.error(f"Verification error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/analyze-image', methods=['POST'])
@limiter.limit("20 per minute")
@jwt_required()
def analyze_image():
    """Image verification endpoint"""
    try:
        user_id = get_jwt_identity()
        
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
        if not file.filename.lower().split('.')[-1] in allowed_extensions:
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Save temporary file
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        try:
            # Analyze image
            analysis_result = image_analyzer.analyze_image(temp_path)
            
            # Extract text from image if present
            extracted_text = image_analyzer.extract_text(temp_path)
            
            # If text found, also verify the text content
            text_verification = None
            if extracted_text:
                text_verification = verification_engine.verify_content(
                    content=extracted_text,
                    content_type='text',
                    language='auto-detect'
                )
            
            # Generate content hash
            import hashlib
            with open(temp_path, 'rb') as f:
                image_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Save verification record
            verification = Verification(
                user_id=user_id,
                content_hash=image_hash,
                content_type='image',
                original_content=f"Image: {filename}",
                result=analysis_result['result'],
                confidence_score=analysis_result['confidence_score'],
                analysis_details={
                    **analysis_result,
                    'extracted_text': extracted_text,
                    'text_verification': text_verification
                }
            )
            
            db.session.add(verification)
            db.session.commit()
            
            return jsonify({
                'verification_id': verification.id,
                'result': analysis_result['result'],
                'confidence_score': analysis_result['confidence_score'],
                'analysis_details': verification.analysis_details,
                'extracted_text': extracted_text,
                'manipulation_indicators': analysis_result.get('manipulation_indicators', []),
                'metadata_analysis': analysis_result.get('metadata_analysis', {}),
                'reverse_search_results': analysis_result.get('reverse_search_results', [])
            })
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/history', methods=['GET'])
@jwt_required()
def get_verification_history():
    """Get user's verification history"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        content_type = request.args.get('content_type')
        
        # Build query
        query = Verification.query.filter_by(user_id=user_id)
        
        if content_type:
            query = query.filter_by(content_type=content_type)
        
        # Paginate results
        verifications = query.order_by(Verification.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        history_data = []
        for verification in verifications.items:
            history_data.append({
                'id': verification.id,
                'content_type': verification.content_type,
                'original_content': verification.original_content[:200] + '...' if len(verification.original_content) > 200 else verification.original_content,
                'result': verification.result,
                'confidence_score': verification.confidence_score,
                'timestamp': verification.timestamp.isoformat(),
                'processing_time': verification.processing_time,
                'analysis_summary': {
                    'credibility_score': verification.analysis_details.get('credibility_score', 0),
                    'main_indicators': verification.analysis_details.get('indicators', [])[:3],
                    'sentiment': verification.analysis_details.get('sentiment_analysis', {}).get('compound', 0)
                }
            })
        
        return jsonify({
            'history': history_data,
            'pagination': {
                'current_page': page,
                'total_pages': verifications.pages,
                'total_items': verifications.total,
                'has_next': verifications.has_next,
                'has_prev': verifications.has_prev
            }
        })
    
    except Exception as e:
        logger.error(f"History retrieval error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/education/modules', methods=['GET'])
@jwt_required()
def get_education_modules():
    """Get available educational modules"""
    try:
        user_id = get_jwt_identity()
        difficulty = request.args.get('difficulty', 'all')
        language = request.args.get('language', 'en')
        
        # Get modules from education engine
        modules = education_engine.get_available_modules(
            language=language,
            difficulty_filter=difficulty if difficulty != 'all' else None
        )
        
        # Get user progress for each module
        user_progress = {}
        for module in modules:
            progress = EducationalProgress.query.filter_by(
                user_id=user_id,
                module_id=module['id']
            ).first()
            
            user_progress[module['id']] = {
                'status': progress.completion_status if progress else 'not_started',
                'score': progress.score if progress else 0.0,
                'completed_at': progress.completed_at.isoformat() if progress and progress.completed_at else None
            }
        
        return jsonify({
            'modules': modules,
            'user_progress': user_progress,
            'total_modules': len(modules),
            'completed_modules': sum(1 for p in user_progress.values() if p['status'] == 'completed')
        })
    
    except Exception as e:
        logger.error(f"Education modules error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/education/progress', methods=['POST'])
@jwt_required()
def track_education_progress():
    """Track user progress in educational modules"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        module_id = data.get('module_id')
        score = data.get('score', 0.0)
        completion_status = data.get('status', 'in_progress')
        time_spent = data.get('time_spent', 0)
        
        if not module_id:
            return jsonify({'error': 'Module ID is required'}), 400
        
        # Update or create progress record
        progress = EducationalProgress.query.filter_by(
            user_id=user_id,
            module_id=module_id
        ).first()
        
        if progress:
            progress.score = max(progress.score, score)  # Keep best score
            progress.completion_status = completion_status
            progress.time_spent = (progress.time_spent or 0) + time_spent
            if completion_status == 'completed' and not progress.completed_at:
                progress.completed_at = datetime.utcnow()
        else:
            progress = EducationalProgress(
                user_id=user_id,
                module_id=module_id,
                module_name=data.get('module_name', f'Module {module_id}'),
                score=score,
                completion_status=completion_status,
                time_spent=time_spent,
                completed_at=datetime.utcnow() if completion_status == 'completed' else None
            )
            db.session.add(progress)
        
        db.session.commit()
        
        # Update user literacy score
        user = User.query.get(user_id)
        user.literacy_score = calculate_user_literacy_score(user_id)
        db.session.commit()
        
        return jsonify({
            'message': 'Progress updated successfully',
            'progress': {
                'module_id': module_id,
                'score': progress.score,
                'status': progress.completion_status,
                'time_spent': progress.time_spent,
                'completed_at': progress.completed_at.isoformat() if progress.completed_at else None
            },
            'updated_literacy_score': user.literacy_score
        })
    
    except Exception as e:
        logger.error(f"Progress tracking error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/user-stats/<int:user_id>', methods=['GET'])
@jwt_required()
def get_specific_user_stats(user_id):
    """Get user statistics and progress"""
    try:
        current_user_id = get_jwt_identity()
        
        # Users can only access their own stats
        if current_user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        user = User.query.get_or_404(user_id)
        
        # Get verification statistics
        total_verifications = Verification.query.filter_by(user_id=user_id).count()
        recent_verifications = Verification.query.filter_by(user_id=user_id).filter(
            Verification.timestamp > datetime.utcnow() - timedelta(days=30)
        ).count()
        
        # Get accuracy statistics
        accurate_verifications = db.session.query(Verification).join(Feedback).filter(
            Verification.user_id == user_id,
            Feedback.accuracy_rating >= 4
        ).count()
        
        accuracy_rate = (accurate_verifications / total_verifications * 100) if total_verifications > 0 else 0
        
        # Get educational progress
        completed_modules = EducationalProgress.query.filter_by(
            user_id=user_id,
            completion_status='completed'
        ).count()
        
        total_modules = EducationalProgress.query.filter_by(user_id=user_id).count()
        
        # Get recent activity
        recent_activity = []
        recent_verifications_data = Verification.query.filter_by(user_id=user_id).order_by(
            Verification.timestamp.desc()
        ).limit(10).all()
        
        for verification in recent_verifications_data:
            recent_activity.append({
                'id': verification.id,
                'content_type': verification.content_type,
                'result': verification.result,
                'confidence_score': verification.confidence_score,
                'timestamp': verification.timestamp.isoformat()
            })
        
        return jsonify({
            'user_id': user_id,
            'username': user.username,
            'literacy_score': user.literacy_score,
            'statistics': {
                'total_verifications': total_verifications,
                'recent_verifications': recent_verifications,
                'accuracy_rate': round(accuracy_rate, 2),
                'completed_modules': completed_modules,
                'total_modules': total_modules,
                'join_date': user.created_at.isoformat(),
                'last_activity': recent_verifications_data[0].timestamp.isoformat() if recent_verifications_data else None
            },
            'recent_activity': recent_activity,
            'achievements': education_engine.get_user_achievements(user_id),
            'recommendations': education_engine.get_personalized_recommendations(user_id)
        })
    
    except Exception as e:
        logger.error(f"User stats error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/report-feedback', methods=['POST'])
@limiter.limit("30 per minute")
@jwt_required()
def report_feedback():
    """Submit feedback on verification accuracy"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        verification_id = data.get('verification_id')
        user_rating = data.get('user_rating')
        accuracy_rating = data.get('accuracy_rating')
        comments = data.get('comments', '')
        
        # Validation
        if not verification_id or not user_rating or not accuracy_rating:
            return jsonify({'error': 'verification_id, user_rating, and accuracy_rating are required'}), 400
        
        if not (1 <= user_rating <= 5) or not (1 <= accuracy_rating <= 5):
            return jsonify({'error': 'Ratings must be between 1 and 5'}), 400
        
        # Check if verification exists and belongs to user
        verification = Verification.query.filter_by(id=verification_id, user_id=user_id).first()
        if not verification:
            return jsonify({'error': 'Verification not found'}), 404
        
        # Check if feedback already exists
        existing_feedback = Feedback.query.filter_by(
            verification_id=verification_id,
            user_id=user_id
        ).first()
        
        if existing_feedback:
            # Update existing feedback
            existing_feedback.user_rating = user_rating
            existing_feedback.accuracy_rating = accuracy_rating
            existing_feedback.comments = comments
            existing_feedback.timestamp = datetime.utcnow()
        else:
            # Create new feedback
            feedback = Feedback(
                verification_id=verification_id,
                user_id=user_id,
                user_rating=user_rating,
                accuracy_rating=accuracy_rating,
                comments=comments
            )
            db.session.add(feedback)
        
        db.session.commit()
        
        # Update user literacy score
        user = User.query.get(user_id)
        user.literacy_score = calculate_user_literacy_score(user_id)
        db.session.commit()
        
        return jsonify({
            'message': 'Feedback submitted successfully',
            'updated_literacy_score': user.literacy_score
        })
    
    except Exception as e:
        logger.error(f"Feedback submission error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/trends', methods=['GET'])
@limiter.limit("100 per hour")
def get_trends():
    """Get current misinformation trends"""
    try:
        region = request.args.get('region', 'india')
        days = int(request.args.get('days', 7))
        
        # Get trends from last N days
        trends = MisinformationTrend.query.filter(
            MisinformationTrend.region == region,
            MisinformationTrend.timestamp > datetime.utcnow() - timedelta(days=days)
        ).order_by(MisinformationTrend.frequency.desc()).limit(20).all()
        
        trend_data = []
        for trend in trends:
            trend_data.append({
                'id': trend.id,
                'category': trend.category,
                'keywords': trend.keywords,
                'frequency': trend.frequency,
                'severity': trend.severity,
                'timestamp': trend.timestamp.isoformat()
            })
        
        # Get verification statistics for trends
        verification_stats = {
            'total_verifications_today': Verification.query.filter(
                Verification.timestamp > datetime.utcnow() - timedelta(days=1)
            ).count(),
            'false_content_percentage': 0,  # Calculate based on results
            'most_common_types': []  # Most common content types
        }
        
        return jsonify({
            'trends': trend_data,
            'statistics': verification_stats,
            'region': region,
            'period_days': days,
            'last_updated': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Trends error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/educational-content', methods=['POST'])
@limiter.limit("50 per minute")
@jwt_required()
def get_educational_content():
    """Get personalized educational content"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        content_type = data.get('content_type', 'module')
        difficulty_level = data.get('difficulty_level', 'beginner')
        topics = data.get('topics', [])
        
        # Get personalized content from education engine
        educational_content = education_engine.get_educational_content(
            user_id=user_id,
            content_type=content_type,
            difficulty_level=difficulty_level,
            topics=topics
        )
        
        return jsonify({
            'content': educational_content,
            'user_level': education_engine.get_user_level(user_id),
            'progress': education_engine.get_user_progress(user_id),
            'recommendations': education_engine.get_personalized_recommendations(user_id)
        })
    
    except Exception as e:
        logger.error(f"Educational content error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded', 'retry_after': str(e.retry_after)}), 429

# Initialize database
def create_tables():
    """Create database tables"""
    with app.app_context():
        db.create_all()
        
        # Create upload directory
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

if __name__ == '__main__':
    create_tables()
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)
