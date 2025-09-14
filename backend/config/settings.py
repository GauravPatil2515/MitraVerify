"""
MitraVerify Configuration Settings
Environment-based configuration management for the application

This module provides centralized configuration management with support for
different environments (development, testing, production) and secure
handling of sensitive information.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class with common settings."""
    
    # Basic Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///mitraverify.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    
    # File upload configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'tiff'}
    
    # Rate limiting configuration
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
    RATELIMIT_DEFAULT = "1000 per day, 100 per hour"
    
    # API Keys and External Services
    GOOGLE_FACTCHECK_API_KEY = os.environ.get('GOOGLE_FACTCHECK_API_KEY')
    GOOGLE_CLOUD_VISION_API_KEY = os.environ.get('GOOGLE_CLOUD_VISION_API_KEY')
    GOOGLE_CLOUD_LANGUAGE_API_KEY = os.environ.get('GOOGLE_CLOUD_LANGUAGE_API_KEY')
    GOOGLE_CLOUD_TRANSLATE_API_KEY = os.environ.get('GOOGLE_CLOUD_TRANSLATE_API_KEY')
    
    # Twilio WhatsApp Configuration
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
    TWILIO_WHATSAPP_NUMBER = os.environ.get('TWILIO_WHATSAPP_NUMBER')
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@mitraverify.com'
    
    # Redis configuration
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # Celery configuration
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or REDIS_URL
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or REDIS_URL
    
    # Application configuration
    APP_NAME = 'MitraVerify'
    APP_VERSION = '1.0.0'
    API_VERSION = 'v1'
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s %(message)s'
    LOG_FILE = os.environ.get('LOG_FILE') or 'mitraverify.log'
    
    # Security configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    CSRF_ENABLED = True
    CSRF_SESSION_KEY = "csrf_token"
    
    # Content verification settings
    MAX_TEXT_LENGTH = 10000  # Maximum text length for verification
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    SUPPORTED_LANGUAGES = ['en', 'hi', 'ta', 'bn', 'mr', 'te', 'gu', 'kn', 'ml', 'pa']
    
    # AI/ML Model configuration
    MODEL_CACHE_TIMEOUT = 3600  # 1 hour
    MODEL_CONFIDENCE_THRESHOLD = 0.7
    BATCH_PROCESSING_SIZE = 100
    
    # External API timeouts
    API_TIMEOUT = 30  # seconds
    REVERSE_IMAGE_SEARCH_TIMEOUT = 60  # seconds
    
    # Monitoring and analytics
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID')
    MIXPANEL_TOKEN = os.environ.get('MIXPANEL_TOKEN')
    
    # Feature flags
    ENABLE_REAL_TIME_PROCESSING = os.environ.get('ENABLE_REAL_TIME_PROCESSING', 'true').lower() == 'true'
    ENABLE_CACHING = os.environ.get('ENABLE_CACHING', 'true').lower() == 'true'
    ENABLE_BACKGROUND_TASKS = os.environ.get('ENABLE_BACKGROUND_TASKS', 'true').lower() == 'true'
    ENABLE_USER_ANALYTICS = os.environ.get('ENABLE_USER_ANALYTICS', 'true').lower() == 'true'
    
    # Social media integration
    FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')
    FACEBOOK_APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET')
    TWITTER_API_KEY = os.environ.get('TWITTER_API_KEY')
    TWITTER_API_SECRET = os.environ.get('TWITTER_API_SECRET')
    
    # WhatsApp Business API
    WHATSAPP_BUSINESS_ACCOUNT_ID = os.environ.get('WHATSAPP_BUSINESS_ACCOUNT_ID')
    WHATSAPP_ACCESS_TOKEN = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    WHATSAPP_WEBHOOK_VERIFY_TOKEN = os.environ.get('WHATSAPP_WEBHOOK_VERIFY_TOKEN')
    
    # Database connection pool settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.environ.get('DB_POOL_SIZE', 10)),
        'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', 3600)),
        'pool_pre_ping': True
    }
    
    @staticmethod
    def init_app(app):
        """Initialize app with configuration."""
        # Create upload directory
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Setup logging
        import logging
        logging.basicConfig(
            level=getattr(logging, app.config['LOG_LEVEL']),
            format=app.config['LOG_FORMAT']
        )

class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    DEVELOPMENT = True
    
    # Use SQLite for development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///mitraverify_dev.db'
    
    # Relaxed rate limiting for development
    RATELIMIT_DEFAULT = "10000 per day, 1000 per hour"
    
    # Enable detailed logging
    LOG_LEVEL = 'DEBUG'
    SQLALCHEMY_ECHO = True
    
    # Disable some security features for easier development
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Development-specific initialization
        print('Starting MitraVerify in DEVELOPMENT mode')

class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    DEBUG = True
    
    # Use in-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Fast token expiration for testing
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    
    # Disable external API calls in testing
    ENABLE_REAL_TIME_PROCESSING = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Testing-specific initialization
        import logging
        logging.disable(logging.CRITICAL)

class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    TESTING = False
    
    # Use PostgreSQL for production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://username:password@localhost/mitraverify'
    
    # Strict rate limiting for production
    RATELIMIT_DEFAULT = "1000 per day, 100 per hour"
    
    # Enhanced security
    CSRF_ENABLED = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Production logging
    LOG_LEVEL = 'WARNING'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Production-specific initialization
        # Setup error logging to email
        if not app.debug and not app.testing:
            if cls.MAIL_SERVER:
                import logging
                from logging.handlers import SMTPHandler
                mail_handler = SMTPHandler(
                    mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
                    fromaddr=cls.MAIL_DEFAULT_SENDER,
                    toaddrs=['admin@mitraverify.com'],
                    subject='MitraVerify Application Error',
                    credentials=(cls.MAIL_USERNAME, cls.MAIL_PASSWORD),
                    secure=() if cls.MAIL_USE_TLS else None
                )
                mail_handler.setLevel(logging.ERROR)
                app.logger.addHandler(mail_handler)
            
            # Setup file logging
            import logging
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                cls.LOG_FILE, maxBytes=10485760, backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('MitraVerify startup')

class StagingConfig(ProductionConfig):
    """Staging environment configuration."""
    DEBUG = True
    
    # Staging-specific database
    SQLALCHEMY_DATABASE_URI = os.environ.get('STAGING_DATABASE_URL') or \
        'postgresql://username:password@localhost/mitraverify_staging'
    
    # Relaxed rate limiting for staging
    RATELIMIT_DEFAULT = "5000 per day, 500 per hour"
    
    # More verbose logging for staging
    LOG_LEVEL = 'INFO'
    
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)
        
        # Staging-specific initialization
        print('Starting MitraVerify in STAGING mode')

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'staging': StagingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration class based on environment."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config.get(config_name, DevelopmentConfig)

# Application constants
class Constants:
    """Application-wide constants."""
    
    # Content types
    CONTENT_TYPES = {
        'TEXT': 'text',
        'IMAGE': 'image',
        'VIDEO': 'video',
        'AUDIO': 'audio',
        'URL': 'url',
        'DOCUMENT': 'document'
    }
    
    # Verification results
    VERIFICATION_RESULTS = {
        'VERIFIED': 'verified',
        'QUESTIONABLE': 'questionable',
        'FALSE': 'false',
        'INSUFFICIENT_INFO': 'insufficient_info',
        'ERROR': 'error'
    }
    
    # User roles
    USER_ROLES = {
        'USER': 'user',
        'MODERATOR': 'moderator',
        'ADMIN': 'admin',
        'SUPER_ADMIN': 'super_admin'
    }
    
    # Educational modules
    EDUCATION_LEVELS = {
        'BEGINNER': 'beginner',
        'INTERMEDIATE': 'intermediate',
        'ADVANCED': 'advanced',
        'EXPERT': 'expert'
    }
    
    # Notification types
    NOTIFICATION_TYPES = {
        'VERIFICATION_COMPLETE': 'verification_complete',
        'EDUCATION_REMINDER': 'education_reminder',
        'ACHIEVEMENT_EARNED': 'achievement_earned',
        'WEEKLY_SUMMARY': 'weekly_summary',
        'SECURITY_ALERT': 'security_alert'
    }
    
    # API response codes
    API_CODES = {
        'SUCCESS': 200,
        'CREATED': 201,
        'BAD_REQUEST': 400,
        'UNAUTHORIZED': 401,
        'FORBIDDEN': 403,
        'NOT_FOUND': 404,
        'RATE_LIMITED': 429,
        'SERVER_ERROR': 500
    }

# Environment-specific settings
class EnvironmentConfig:
    """Environment-specific configuration helper."""
    
    @staticmethod
    def is_development():
        """Check if running in development mode."""
        return os.environ.get('FLASK_ENV') == 'development'
    
    @staticmethod
    def is_production():
        """Check if running in production mode."""
        return os.environ.get('FLASK_ENV') == 'production'
    
    @staticmethod
    def is_testing():
        """Check if running in testing mode."""
        return os.environ.get('FLASK_ENV') == 'testing'
    
    @staticmethod
    def get_environment():
        """Get current environment name."""
        return os.environ.get('FLASK_ENV', 'development')

# Security configuration
class SecurityConfig:
    """Security-related configuration."""
    
    # Password requirements
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_SPECIAL_CHARS = True
    
    # Session configuration
    SESSION_TIMEOUT = 3600  # 1 hour
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION = 300  # 5 minutes
    
    # CORS configuration
    CORS_ALLOW_CREDENTIALS = True
    CORS_MAX_AGE = 86400  # 24 hours
    
    # Content Security Policy
    CSP_DIRECTIVES = {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline' https://apis.google.com",
        'style-src': "'self' 'unsafe-inline' https://fonts.googleapis.com",
        'font-src': "'self' https://fonts.gstatic.com",
        'img-src': "'self' data: https:",
        'connect-src': "'self' https://api.mitraverify.com"
    }

# Feature flags configuration
class FeatureFlags:
    """Feature flags for enabling/disabling functionality."""
    
    # Core features
    ENABLE_USER_REGISTRATION = True
    ENABLE_SOCIAL_LOGIN = True
    ENABLE_EMAIL_VERIFICATION = True
    
    # Verification features
    ENABLE_TEXT_VERIFICATION = True
    ENABLE_IMAGE_VERIFICATION = True
    ENABLE_VIDEO_VERIFICATION = False  # Coming soon
    ENABLE_AUDIO_VERIFICATION = False  # Coming soon
    
    # Educational features
    ENABLE_EDUCATION_MODULES = True
    ENABLE_GAMIFICATION = True
    ENABLE_ACHIEVEMENTS = True
    ENABLE_LEADERBOARDS = True
    
    # Social features
    ENABLE_SHARING = True
    ENABLE_COMMENTS = False  # Future feature
    ENABLE_USER_PROFILES = True
    
    # Advanced features
    ENABLE_API_ACCESS = True
    ENABLE_WEBHOOK_NOTIFICATIONS = False  # Enterprise feature
    ENABLE_BULK_PROCESSING = False  # Enterprise feature
    ENABLE_WHITE_LABEL = False  # Enterprise feature

# Monitoring configuration
class MonitoringConfig:
    """Monitoring and analytics configuration."""
    
    # Performance monitoring
    ENABLE_PERFORMANCE_MONITORING = True
    SLOW_QUERY_THRESHOLD = 1.0  # seconds
    
    # Error tracking
    ENABLE_ERROR_TRACKING = True
    ERROR_SAMPLE_RATE = 1.0
    
    # User analytics
    ENABLE_USER_ANALYTICS = True
    ANALYTICS_SAMPLE_RATE = 0.1  # 10% of users
    
    # Health checks
    HEALTH_CHECK_INTERVAL = 60  # seconds
    HEALTH_CHECK_TIMEOUT = 10  # seconds
