# MitraVerify - AI-Powered Misinformation Detection Platform

![MitraVerify Logo](docs/assets/logo.png)

## 🎯 Project Overview

MitraVerify is an innovative AI-powered platform designed to combat misinformation in India through real-time content verification, educational tools, and multi-platform integration. Built for the Google Cloud hackathon, it provides comprehensive misinformation detection across text, images, and multimedia content.

## 🚀 Features

### Core Verification Engine
- **Real-time Content Analysis**: Instant verification of text, images, and multimedia
- **Cultural Context Awareness**: India-specific misinformation pattern recognition
- **Multi-language Support**: Hindi, English, Tamil, Bengali, Marathi, and more
- **Source Credibility Scoring**: Advanced algorithms to assess information reliability
- **Deepfake Detection**: Basic computer vision for manipulated media identification

### Educational Platform
- **Digital Literacy Dashboard**: Gamified learning experience
- **Personalized Content**: Tailored educational modules based on user behavior
- **Progress Tracking**: Visual charts showing improvement over time
- **Achievement System**: Badges and rewards for learning milestones

### Multi-Platform Access
- **Web Application**: Responsive React-based interface
- **WhatsApp Bot**: Instant verification through messaging
- **Browser Extension**: Real-time social media content scanning
- **Progressive Web App**: Offline capabilities for basic verification

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask (Python 3.9+)
- **Database**: SQLite (development), PostgreSQL (production)
- **AI/ML**: scikit-learn, spaCy, OpenCV, PIL
- **APIs**: Google Fact Check Tools, Twilio WhatsApp Business
- **Security**: JWT authentication, Flask-Limiter for rate limiting

### Frontend
- **Framework**: React 18 with hooks
- **Styling**: Material-UI with custom themes
- **State Management**: Redux Toolkit
- **Internationalization**: react-i18next
- **PWA**: Service workers for offline functionality

### Infrastructure
- **Deployment**: Heroku (backend), Vercel (frontend)
- **Cloud Services**: Google Cloud Platform integration points
- **Monitoring**: Comprehensive logging and error tracking

## 📋 Quick Start Guide

### Prerequisites
- Python 3.9 or higher
- Node.js 16+ and npm
- Git

### Backend Setup

1. **Clone and navigate to backend**:
```bash
cd backend
```

2. **Create virtual environment**:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set environment variables**:
```bash
# Create .env file
echo FLASK_ENV=development > .env
echo SECRET_KEY=your-secret-key-here >> .env
echo DATABASE_URL=sqlite:///mitraverify.db >> .env
```

5. **Initialize database**:
```bash
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

6. **Run backend server**:
```bash
python app.py
```

Backend will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**:
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Set environment variables**:
```bash
# Create .env file
echo REACT_APP_API_URL=http://localhost:5000 > .env
echo REACT_APP_VERSION=1.0.0 >> .env
```

4. **Start development server**:
```bash
npm start
```

Frontend will be available at `http://localhost:3000`

### WhatsApp Bot Setup

1. **Navigate to WhatsApp bot directory**:
```bash
cd whatsapp-bot
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure Twilio credentials**:
```bash
# Add to .env file
echo TWILIO_ACCOUNT_SID=your-account-sid >> .env
echo TWILIO_AUTH_TOKEN=your-auth-token >> .env
echo TWILIO_PHONE_NUMBER=your-twilio-number >> .env
```

4. **Run WhatsApp bot**:
```bash
python bot.py
```

### Browser Extension Setup

1. **Navigate to browser extension directory**:
```bash
cd browser-extension
```

2. **Open Chrome and go to**:
   - `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `browser-extension` folder

## 🧪 Testing

### Run Backend Tests
```bash
cd backend
python -m pytest tests/ -v
```

### Run Frontend Tests
```bash
cd frontend
npm test
```

### Run Integration Tests
```bash
python tests/test_integration.py
```

## 📊 API Documentation

### Authentication
All API requests require authentication via JWT token:
```bash
Authorization: Bearer <your-jwt-token>
```

### Core Endpoints

#### Verify Content
```bash
POST /api/verify
Content-Type: application/json

{
  "content": "Text content to verify",
  "content_type": "text|image|url",
  "user_id": "user123",
  "language": "en|hi|ta|bn|mr"
}
```

#### Analyze Image
```bash
POST /api/analyze-image
Content-Type: multipart/form-data

image: <image-file>
user_id: user123
```

#### Get User Statistics
```bash
GET /api/user-stats/{user_id}
```

#### Submit Feedback
```bash
POST /api/report-feedback
Content-Type: application/json

{
  "verification_id": "ver123",
  "user_rating": 5,
  "accuracy_rating": 4,
  "comments": "Helpful verification"
}
```

## 🌐 Deployment

### Backend Deployment (Heroku)

1. **Install Heroku CLI** and login:
```bash
heroku login
```

2. **Create Heroku app**:
```bash
heroku create mitraverify-backend
```

3. **Set environment variables**:
```bash
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-production-secret
heroku config:set DATABASE_URL=postgresql://...
```

4. **Deploy**:
```bash
git push heroku main
```

### Frontend Deployment (Vercel)

1. **Install Vercel CLI**:
```bash
npm i -g vercel
```

2. **Deploy**:
```bash
cd frontend
vercel --prod
```

### Database Migration (Production)

```bash
heroku run python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///mitraverify.db
JWT_SECRET_KEY=your-jwt-secret
GOOGLE_FACTCHECK_API_KEY=your-google-api-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
REDIS_URL=redis://localhost:6379
```

#### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:5000
REACT_APP_VERSION=1.0.0
REACT_APP_GOOGLE_ANALYTICS_ID=your-ga-id
REACT_APP_SENTRY_DSN=your-sentry-dsn
```

## 📱 Mobile App (Future Enhancement)

React Native mobile application is planned for Phase 2:
- Native iOS and Android apps
- Offline verification capabilities
- Camera integration for real-time image verification
- Push notifications for misinformation alerts

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint for JavaScript code
- Write comprehensive tests for new features
- Update documentation for API changes
- Ensure accessibility compliance

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Cloud Platform for hosting infrastructure
- Twilio for WhatsApp Business API
- Material-UI for React components
- Open source community for various libraries and tools

## 📞 Support

- **Email**: support@mitraverify.com
- **Documentation**: [docs.mitraverify.com](docs.mitraverify.com)
- **Issues**: [GitHub Issues](https://github.com/your-username/mitraverify/issues)
- **Discord**: [Community Server](https://discord.gg/mitraverify)

## 🗺️ Roadmap

### Phase 1 (Current) ✅
- ✅ Core verification engine
- ✅ Web application
- ✅ WhatsApp bot integration
- ✅ Browser extension
- ✅ Basic educational modules

### Phase 2 (Q2 2024)
- 📱 Mobile applications (iOS/Android)
- 🤖 Advanced AI models
- 🌍 Regional language expansion
- 📊 Advanced analytics dashboard
- 🎓 University partnerships

### Phase 3 (Q3 2024)
- 🏛️ Government integration
- 📺 TV/Radio content monitoring
- 🔗 Social platform APIs
- 🎯 Targeted misinformation campaigns
- 🌐 International expansion

---

**Built with ❤️ for a misinformation-free India**

For detailed technical documentation, see [docs/](docs/) directory.
