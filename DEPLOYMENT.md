# MitraVerify Deployment Guide
Complete deployment instructions for all components of the MitraVerify platform

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Backend Deployment (Heroku)](#backend-deployment-heroku)
3. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
4. [WhatsApp Bot Deployment](#whatsapp-bot-deployment)
5. [Browser Extension Deployment](#browser-extension-deployment)
6. [Database Setup](#database-setup)
7. [Environment Configuration](#environment-configuration)
8. [Production Optimization](#production-optimization)
9. [Monitoring and Analytics](#monitoring-and-analytics)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Accounts
- **Heroku** account for backend deployment
- **Vercel** account for frontend deployment  
- **Google Cloud Platform** account for AI services
- **Twilio** account for WhatsApp integration
- **PostgreSQL** database (Heroku Postgres or external)
- **Redis** instance for caching (Heroku Redis or external)

### Required API Keys
- Google Cloud Vision API key
- Google Cloud Language API key
- Google Cloud Translate API key
- Google Fact Check Tools API key
- Twilio Account SID and Auth Token
- Sentry DSN (optional, for error tracking)

### Development Tools
- **Node.js** 18+ and npm
- **Python** 3.9+ and pip
- **Git** for version control
- **Chrome** browser for extension testing

## Backend Deployment (Heroku)

### 1. Prepare the Backend

```bash
cd backend
```

### 2. Create Heroku App

```bash
# Install Heroku CLI if not already installed
# Login to Heroku
heroku login

# Create new Heroku app
heroku create mitraverify-backend

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:standard-0

# Add Redis addon
heroku addons:create heroku-redis:premium-0

# Set Python buildpack
heroku buildpacks:set heroku/python
```

### 3. Configure Environment Variables

```bash
# Set all required environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-super-secret-key-here
heroku config:set JWT_SECRET_KEY=your-jwt-secret-key

# Google Cloud APIs
heroku config:set GOOGLE_FACTCHECK_API_KEY=your-factcheck-api-key
heroku config:set GOOGLE_CLOUD_VISION_API_KEY=your-vision-api-key
heroku config:set GOOGLE_CLOUD_LANGUAGE_API_KEY=your-language-api-key
heroku config:set GOOGLE_CLOUD_TRANSLATE_API_KEY=your-translate-api-key

# Twilio Configuration
heroku config:set TWILIO_ACCOUNT_SID=your-twilio-account-sid
heroku config:set TWILIO_AUTH_TOKEN=your-twilio-auth-token
heroku config:set TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Email Configuration
heroku config:set MAIL_SERVER=smtp.gmail.com
heroku config:set MAIL_PORT=587
heroku config:set MAIL_USE_TLS=true
heroku config:set MAIL_USERNAME=your-email@gmail.com
heroku config:set MAIL_PASSWORD=your-app-password

# CORS Configuration
heroku config:set CORS_ORIGINS=https://mitraverify.vercel.app

# Optional: Monitoring
heroku config:set SENTRY_DSN=your-sentry-dsn
```

### 4. Create Procfile

```bash
echo "web: gunicorn app:app" > Procfile
echo "worker: celery -A app.celery worker --loglevel=info" >> Procfile
```

### 5. Deploy to Heroku

```bash
# Initialize git repository if not already done
git init
git add .
git commit -m "Initial commit"

# Add Heroku remote
heroku git:remote -a mitraverify-backend

# Deploy
git push heroku main

# Run database migrations
heroku run python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

### 6. Verify Deployment

```bash
# Check app status
heroku ps

# View logs
heroku logs --tail

# Test API endpoint
curl https://mitraverify-backend.herokuapp.com/api/health
```

## Frontend Deployment (Vercel)

### 1. Prepare Frontend

```bash
cd frontend
```

### 2. Install Vercel CLI

```bash
npm install -g vercel
```

### 3. Configure Environment Variables

Create `.env.local` file:

```env
REACT_APP_API_URL=https://mitraverify-backend.herokuapp.com/api
REACT_APP_ENVIRONMENT=production
REACT_APP_GOOGLE_ANALYTICS_ID=your-ga-id
REACT_APP_SENTRY_DSN=your-sentry-dsn
```

### 4. Deploy to Vercel

```bash
# Login to Vercel
vercel login

# Deploy
vercel

# Follow prompts:
# - Link to existing project? No
# - Project name: mitraverify-frontend
# - Directory: ./
# - Override settings? No

# Set environment variables in Vercel dashboard or via CLI
vercel env add REACT_APP_API_URL production
# Enter: https://mitraverify-backend.herokuapp.com/api

# Deploy to production
vercel --prod
```

### 5. Configure Custom Domain (Optional)

```bash
# Add custom domain
vercel domains add mitraverify.com

# Configure DNS records as instructed by Vercel
```

## WhatsApp Bot Deployment

### 1. Deploy WhatsApp Bot to Heroku

```bash
cd whatsapp_bot

# Create separate Heroku app for WhatsApp bot
heroku create mitraverify-whatsapp-bot

# Set environment variables
heroku config:set TWILIO_ACCOUNT_SID=your-twilio-account-sid
heroku config:set TWILIO_AUTH_TOKEN=your-twilio-auth-token
heroku config:set TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
heroku config:set BACKEND_API_URL=https://mitraverify-backend.herokuapp.com/api

# Create Procfile
echo "web: gunicorn app:app" > Procfile

# Deploy
git init
git add .
git commit -m "WhatsApp bot deployment"
heroku git:remote -a mitraverify-whatsapp-bot
git push heroku main
```

### 2. Configure Twilio Webhook

```bash
# Set webhook URL in Twilio Console
# Webhook URL: https://mitraverify-whatsapp-bot.herokuapp.com/webhook
# HTTP Method: POST
```

### 3. Test WhatsApp Bot

1. Send a message to your Twilio WhatsApp number
2. Bot should respond with help menu
3. Test text, image, and URL verification

## Browser Extension Deployment

### 1. Prepare Extension for Chrome Web Store

```bash
cd browser_extension

# Create icons directory and add required icon sizes
mkdir -p icons
# Add icon-16.png, icon-32.png, icon-48.png, icon-128.png

# Update manifest.json with production URLs
# Change localhost URLs to production URLs
```

### 2. Package Extension

```bash
# Create ZIP file for Chrome Web Store
zip -r mitraverify-extension.zip . -x "*.git*" "*.DS_Store*" "node_modules/*"
```

### 3. Submit to Chrome Web Store

1. Go to [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole/)
2. Pay one-time $5 developer registration fee
3. Upload ZIP file
4. Fill out store listing details:
   - **Name**: MitraVerify - Misinformation Detection
   - **Description**: Real-time misinformation detection for social media and news sites
   - **Category**: Productivity
   - **Language**: English (and others as needed)
5. Add screenshots and promotional images
6. Submit for review (takes 1-3 business days)

### 4. Test Extension Locally

```bash
# Load unpacked extension in Chrome
# 1. Open Chrome and go to chrome://extensions/
# 2. Enable "Developer mode"
# 3. Click "Load unpacked"
# 4. Select browser_extension directory
```

## Database Setup

### 1. PostgreSQL Configuration

```sql
-- Connect to your PostgreSQL database
-- Create database (if not using Heroku Postgres)
CREATE DATABASE mitraverify;

-- Create user and grant permissions
CREATE USER mitraverify_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE mitraverify TO mitraverify_user;

-- Enable required extensions
\c mitraverify
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```

### 2. Redis Configuration

```bash
# If using external Redis, ensure it's configured for:
# - Persistence (RDB snapshots)
# - Memory optimization
# - SSL/TLS encryption for production

# Redis connection string format:
# redis://username:password@hostname:port/database
```

### 3. Database Migrations

```bash
# Run from backend directory
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# Or if using Flask-Migrate
flask db upgrade
```

## Environment Configuration

### Production Environment Variables

Create comprehensive `.env` file for production:

```env
# Application
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-super-secret-production-key
JWT_SECRET_KEY=your-jwt-secret-production-key

# Database
DATABASE_URL=postgresql://user:password@host:port/database
REDIS_URL=redis://user:password@host:port/database

# Google Cloud APIs
GOOGLE_FACTCHECK_API_KEY=your-factcheck-api-key
GOOGLE_CLOUD_VISION_API_KEY=your-vision-api-key
GOOGLE_CLOUD_LANGUAGE_API_KEY=your-language-api-key
GOOGLE_CLOUD_TRANSLATE_API_KEY=your-translate-api-key

# Twilio
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@mitraverify.com

# Security
CORS_ORIGINS=https://mitraverify.vercel.app,https://mitraverify.com
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true

# Monitoring
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=WARNING

# Rate Limiting
RATELIMIT_STORAGE_URL=redis://user:password@host:port/database
```

## Production Optimization

### 1. Backend Optimization

```python
# In app.py, ensure production settings:
# - Debug mode disabled
# - Proper logging configuration
# - Database connection pooling
# - Caching enabled
# - Rate limiting configured
```

### 2. Frontend Optimization

```bash
# Build optimized production bundle
npm run build

# Verify bundle size
npm run analyze

# Enable gzip compression in Vercel
# (Vercel does this automatically)
```

### 3. Performance Monitoring

```bash
# Add performance monitoring to frontend
npm install @sentry/react @sentry/tracing

# Configure in src/index.js
import * as Sentry from "@sentry/react";
import { Integrations } from "@sentry/tracing";

Sentry.init({
  dsn: process.env.REACT_APP_SENTRY_DSN,
  integrations: [
    new Integrations.BrowserTracing(),
  ],
  tracesSampleRate: 1.0,
});
```

## Monitoring and Analytics

### 1. Application Monitoring

```bash
# Heroku monitoring
heroku addons:create newrelic:wayne

# Custom health checks
curl https://mitraverify-backend.herokuapp.com/api/health
curl https://mitraverify-whatsapp-bot.herokuapp.com/health
```

### 2. Analytics Setup

```javascript
// Google Analytics 4 configuration
// Add to frontend public/index.html:
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

### 3. Error Tracking

```bash
# Sentry configuration already included in code
# Just set SENTRY_DSN environment variable
```

## Troubleshooting

### Common Issues

1. **Backend not starting**
   ```bash
   # Check logs
   heroku logs --tail -a mitraverify-backend
   
   # Check environment variables
   heroku config -a mitraverify-backend
   ```

2. **Database connection errors**
   ```bash
   # Reset database
   heroku pg:reset DATABASE_URL -a mitraverify-backend
   
   # Run migrations again
   heroku run python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()" -a mitraverify-backend
   ```

3. **Frontend API connection issues**
   ```bash
   # Check CORS configuration
   # Verify API URL in environment variables
   # Check network tab in browser dev tools
   ```

4. **WhatsApp bot not responding**
   ```bash
   # Check Twilio webhook configuration
   # Verify webhook URL is accessible
   # Check bot logs
   heroku logs --tail -a mitraverify-whatsapp-bot
   ```

5. **Extension not working**
   ```bash
   # Check manifest.json permissions
   # Verify content script injection
   # Check browser console for errors
   ```

### Performance Issues

1. **Slow API responses**
   - Enable Redis caching
   - Optimize database queries
   - Use CDN for static assets

2. **High memory usage**
   - Monitor with `heroku ps -a app-name`
   - Optimize image processing
   - Implement proper garbage collection

3. **Rate limiting errors**
   - Increase Redis memory
   - Optimize rate limiting rules
   - Implement request queuing

## Security Checklist

- [ ] All environment variables set securely
- [ ] HTTPS enabled on all endpoints
- [ ] API rate limiting configured
- [ ] Input validation implemented
- [ ] SQL injection protection enabled
- [ ] CORS properly configured
- [ ] Security headers set
- [ ] Regular dependency updates
- [ ] Backup strategy implemented
- [ ] Monitoring alerts configured

## Maintenance

### Regular Tasks

1. **Weekly**
   - Monitor application performance
   - Check error rates and logs
   - Review user feedback

2. **Monthly**
   - Update dependencies
   - Backup database
   - Review analytics data
   - Update AI models if needed

3. **Quarterly**
   - Security audit
   - Performance optimization
   - Feature usage analysis
   - Cost optimization review

### Scaling Considerations

1. **Backend Scaling**
   ```bash
   # Scale up dynos
   heroku ps:scale web=2 worker=1 -a mitraverify-backend
   
   # Upgrade database
   heroku addons:upgrade heroku-postgresql:standard-2 -a mitraverify-backend
   ```

2. **CDN Implementation**
   - Use Cloudflare or AWS CloudFront
   - Cache static assets and API responses
   - Implement edge computing for better performance

3. **Load Balancing**
   - Use Heroku's automatic load balancing
   - Consider microservices architecture for high scale
   - Implement caching strategies

---

This deployment guide covers all aspects of deploying MitraVerify to production. For specific issues or additional configuration needs, refer to the documentation of individual services (Heroku, Vercel, Twilio, etc.).
