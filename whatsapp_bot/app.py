"""
MitraVerify WhatsApp Bot
Instant misinformation detection via WhatsApp using Twilio API

This bot provides instant verification of text messages, images, and URLs
sent via WhatsApp, making fact-checking accessible to users without
requiring app installation.
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import requests
from PIL import Image
import io
import base64
import re
from urllib.parse import urlparse
import tempfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MitraVerifyWhatsAppBot:
    """Main WhatsApp bot class for MitraVerify."""
    
    def __init__(self):
        """Initialize the WhatsApp bot with Twilio configuration."""
        self.app = Flask(__name__)
        self.setup_config()
        self.setup_twilio()
        self.setup_routes()
        self.user_sessions = {}  # Store user conversation state
        self.rate_limits = {}   # Store user rate limiting info
        
        # API endpoints
        self.backend_api = os.getenv('BACKEND_API_URL', 'http://localhost:5000/api')
        self.api_timeout = 30  # seconds
        
        # Bot configuration
        self.max_daily_requests = 20  # Per user daily limit
        self.session_timeout = 300  # 5 minutes session timeout
        
        logger.info("MitraVerify WhatsApp Bot initialized")
    
    def setup_config(self):
        """Setup configuration from environment variables."""
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
        
        if not all([self.account_sid, self.auth_token]):
            raise ValueError("Missing required Twilio configuration")
    
    def setup_twilio(self):
        """Initialize Twilio client."""
        try:
            self.twilio_client = Client(self.account_sid, self.auth_token)
            logger.info("Twilio client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {e}")
            raise
    
    def setup_routes(self):
        """Setup Flask routes for webhook handling."""
        
        @self.app.route('/webhook', methods=['POST'])
        def webhook():
            """Handle incoming WhatsApp messages."""
            try:
                return self.handle_message()
            except Exception as e:
                logger.error(f"Error handling webhook: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint."""
            return jsonify({
                'status': 'healthy',
                'service': 'MitraVerify WhatsApp Bot',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        @self.app.route('/stats', methods=['GET'])
        def stats():
            """Get bot statistics."""
            return jsonify({
                'active_sessions': len(self.user_sessions),
                'total_users': len(self.rate_limits),
                'service': 'MitraVerify WhatsApp Bot'
            })
    
    def handle_message(self):
        """Process incoming WhatsApp message."""
        try:
            # Extract message data
            from_number = request.form.get('From', '')
            message_body = request.form.get('Body', '').strip()
            message_type = request.form.get('MessageType', 'text')
            media_url = request.form.get('MediaUrl0', '')
            media_content_type = request.form.get('MediaContentType0', '')
            
            logger.info(f"Received message from {from_number}: {message_body[:50]}...")
            
            # Check rate limiting
            if not self.check_rate_limit(from_number):
                return self.send_rate_limit_message(from_number)
            
            # Initialize user session if needed
            self.init_user_session(from_number)
            
            # Route message based on type and content
            response = self.route_message(
                from_number, message_body, message_type, 
                media_url, media_content_type
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return self.send_error_message(from_number if 'from_number' in locals() else '')
    
    def route_message(self, from_number: str, message_body: str, 
                     message_type: str, media_url: str, media_content_type: str):
        """Route message to appropriate handler based on content."""
        
        message_body_lower = message_body.lower()
        
        # Handle commands
        if message_body_lower in ['help', 'start', 'menu']:
            return self.send_help_message(from_number)
        elif message_body_lower in ['stop', 'quit', 'exit']:
            return self.send_goodbye_message(from_number)
        elif message_body_lower == 'stats':
            return self.send_user_stats(from_number)
        elif message_body_lower == 'history':
            return self.send_user_history(from_number)
        
        # Handle media messages (images)
        if media_url and 'image' in media_content_type:
            return self.handle_image_verification(from_number, media_url, message_body)
        
        # Handle URL verification
        urls = self.extract_urls(message_body)
        if urls:
            return self.handle_url_verification(from_number, urls[0], message_body)
        
        # Handle text verification
        if message_body and len(message_body.strip()) > 10:
            return self.handle_text_verification(from_number, message_body)
        
        # Default response for unclear input
        return self.send_unclear_input_message(from_number)
    
    def handle_text_verification(self, from_number: str, text: str):
        """Handle text content verification."""
        try:
            # Send "thinking" message
            self.send_typing_indicator(from_number)
            self.send_message(from_number, "🔍 Analyzing your text... This may take a few moments.")
            
            # Call verification API
            response = self.call_verification_api('text', {'content': text})
            
            if response and 'result' in response:
                return self.format_verification_response(from_number, response, 'text')
            else:
                return self.send_error_message(from_number, "Unable to verify text at the moment.")
                
        except Exception as e:
            logger.error(f"Error in text verification: {e}")
            return self.send_error_message(from_number, "Text verification failed.")
    
    def handle_image_verification(self, from_number: str, media_url: str, caption: str = ''):
        """Handle image verification."""
        try:
            # Send "processing" message
            self.send_typing_indicator(from_number)
            self.send_message(from_number, "📸 Analyzing your image... Please wait.")
            
            # Download and process image
            image_data = self.download_media(media_url)
            if not image_data:
                return self.send_error_message(from_number, "Unable to download image.")
            
            # Call verification API
            files = {'image': ('image.jpg', image_data, 'image/jpeg')}
            response = self.call_verification_api('image', files=files)
            
            if response and 'result' in response:
                return self.format_verification_response(from_number, response, 'image')
            else:
                return self.send_error_message(from_number, "Unable to verify image at the moment.")
                
        except Exception as e:
            logger.error(f"Error in image verification: {e}")
            return self.send_error_message(from_number, "Image verification failed.")
    
    def handle_url_verification(self, from_number: str, url: str, message: str):
        """Handle URL verification."""
        try:
            # Send "checking" message
            self.send_typing_indicator(from_number)
            self.send_message(from_number, f"🔗 Checking URL: {url[:50]}...")
            
            # Call verification API
            response = self.call_verification_api('url', {'url': url})
            
            if response and 'result' in response:
                return self.format_verification_response(from_number, response, 'url')
            else:
                return self.send_error_message(from_number, "Unable to verify URL at the moment.")
                
        except Exception as e:
            logger.error(f"Error in URL verification: {e}")
            return self.send_error_message(from_number, "URL verification failed.")
    
    def call_verification_api(self, content_type: str, data: Dict[str, Any] = None, files: Dict = None):
        """Call the backend verification API."""
        try:
            api_url = f"{self.backend_api}/verify"
            
            headers = {
                'User-Agent': 'MitraVerify-WhatsApp-Bot/1.0'
            }
            
            if files:
                # For file uploads (images)
                response = requests.post(
                    api_url, 
                    files=files, 
                    data={'content_type': content_type},
                    headers=headers,
                    timeout=self.api_timeout
                )
            else:
                # For text/URL verification
                headers['Content-Type'] = 'application/json'
                data['content_type'] = content_type
                response = requests.post(
                    api_url, 
                    json=data, 
                    headers=headers,
                    timeout=self.api_timeout
                )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error("API request timeout")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling API: {e}")
            return None
    
    def format_verification_response(self, from_number: str, response: Dict, content_type: str):
        """Format verification result for WhatsApp display."""
        try:
            result = response.get('result', {})
            status = result.get('status', 'unknown')
            confidence = result.get('confidence', 0)
            explanation = result.get('explanation', 'No explanation available')
            sources = result.get('sources', [])
            
            # Status emoji mapping
            status_emojis = {
                'verified': '✅',
                'questionable': '⚠️',
                'false': '❌',
                'insufficient_info': 'ℹ️'
            }
            
            emoji = status_emojis.get(status, '❓')
            
            # Format main message
            message_lines = [
                f"{emoji} *Verification Result*",
                "",
                f"*Status:* {status.replace('_', ' ').title()}",
                f"*Confidence:* {confidence:.1%}",
                "",
                f"*Analysis:* {explanation[:200]}{'...' if len(explanation) > 200 else ''}",
            ]
            
            # Add sources if available
            if sources:
                message_lines.extend([
                    "",
                    "*Sources:*"
                ])
                for i, source in enumerate(sources[:3], 1):
                    source_name = source.get('name', 'Unknown Source')
                    message_lines.append(f"{i}. {source_name}")
            
            # Add tips based on status
            if status == 'false':
                message_lines.extend([
                    "",
                    "⚠️ *Warning:* This content appears to be misinformation.",
                    "Please verify with multiple reliable sources before sharing."
                ])
            elif status == 'questionable':
                message_lines.extend([
                    "",
                    "🤔 *Caution:* This content needs further verification.",
                    "Consider checking additional sources."
                ])
            elif status == 'verified':
                message_lines.extend([
                    "",
                    "👍 *Good:* This content appears to be accurate.",
                    "Based on current available information."
                ])
            
            # Add footer
            message_lines.extend([
                "",
                "📱 Get detailed analysis at mitraverify.vercel.app",
                "",
                "Type 'help' for more options."
            ])
            
            # Send response
            full_message = "\n".join(message_lines)
            return self.send_message(from_number, full_message)
            
        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            return self.send_error_message(from_number, "Error formatting verification result.")
    
    def send_help_message(self, from_number: str):
        """Send help/menu message."""
        help_text = """
🤖 *Welcome to MitraVerify Bot!*

I can help you verify:
📝 *Text* - Send any text to check
📸 *Images* - Send photos to analyze
🔗 *URLs* - Send links to verify

*Commands:*
• Type 'help' - Show this menu
• Type 'stats' - Your usage statistics
• Type 'history' - Recent verifications
• Type 'stop' - End conversation

*How to use:*
1. Simply send text, image, or URL
2. I'll analyze it for misinformation
3. Get instant verification results

⚡ *Fast • Accurate • Free*

Start by sending content to verify!
        """
        return self.send_message(from_number, help_text.strip())
    
    def send_goodbye_message(self, from_number: str):
        """Send goodbye message."""
        goodbye_text = """
👋 *Thank you for using MitraVerify!*

Remember to:
• Verify before you share
• Check multiple sources
• Think critically about information

Stay informed, stay safe! 🛡️

Type 'help' anytime to start again.
        """
        # Clear user session
        if from_number in self.user_sessions:
            del self.user_sessions[from_number]
        
        return self.send_message(from_number, goodbye_text.strip())
    
    def send_user_stats(self, from_number: str):
        """Send user statistics."""
        # In a real implementation, this would fetch from database
        stats_text = """
📊 *Your MitraVerify Stats*

• Verifications today: 3
• This week: 12
• All time: 47

• Accuracy helped: 94%
• Misinformation caught: 8
• Sources checked: 156

🏆 Keep up the great fact-checking!

Visit mitraverify.vercel.app for detailed analytics.
        """
        return self.send_message(from_number, stats_text.strip())
    
    def send_user_history(self, from_number: str):
        """Send recent verification history."""
        # In a real implementation, this would fetch from database
        history_text = """
📋 *Recent Verifications*

1. ✅ News article - Verified
   2 hours ago

2. ⚠️ Social media post - Questionable
   Yesterday

3. ❌ WhatsApp forward - False
   2 days ago

4. ✅ Government notice - Verified
   3 days ago

View full history at mitraverify.vercel.app
        """
        return self.send_message(from_number, history_text.strip())
    
    def send_unclear_input_message(self, from_number: str):
        """Send message for unclear input."""
        unclear_text = """
🤔 *I'm not sure how to help with that.*

Please send:
📝 Text to verify (at least 10 characters)
📸 Image/photo to analyze
🔗 URL/link to check

Or type 'help' for more options.
        """
        return self.send_message(from_number, unclear_text.strip())
    
    def send_rate_limit_message(self, from_number: str):
        """Send rate limit exceeded message."""
        limit_text = """
⏰ *Rate Limit Reached*

You've reached your daily limit of verifications.

• Free users: 20 per day
• Limit resets at midnight UTC

For unlimited access, visit:
mitraverify.vercel.app

Thank you for using MitraVerify responsibly!
        """
        return self.send_message(from_number, limit_text.strip())
    
    def send_error_message(self, from_number: str, error_msg: str = None):
        """Send error message."""
        default_error = """
⚠️ *Something went wrong*

I'm having trouble processing your request right now.

Please try again in a few moments, or visit:
mitraverify.vercel.app

If the problem continues, type 'help' for support.
        """
        
        message = error_msg if error_msg else default_error
        return self.send_message(from_number, message)
    
    def send_message(self, to_number: str, message: str):
        """Send WhatsApp message using Twilio."""
        try:
            response = MessagingResponse()
            response.message(message)
            
            # Also send via Twilio API for logging
            try:
                self.twilio_client.messages.create(
                    body=message,
                    from_=self.whatsapp_number,
                    to=to_number
                )
                logger.info(f"Message sent to {to_number}")
            except Exception as e:
                logger.error(f"Error sending via Twilio API: {e}")
            
            return str(response)
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            response = MessagingResponse()
            response.message("Sorry, I'm having trouble responding right now.")
            return str(response)
    
    def send_typing_indicator(self, to_number: str):
        """Send typing indicator (if supported by Twilio)."""
        # Note: WhatsApp doesn't fully support typing indicators via Twilio
        # This is a placeholder for future enhancement
        pass
    
    def download_media(self, media_url: str) -> Optional[bytes]:
        """Download media file from Twilio."""
        try:
            # Add Twilio authentication for media download
            auth = (self.account_sid, self.auth_token)
            response = requests.get(media_url, auth=auth, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Error downloading media: {e}")
            return None
    
    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text message."""
        url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        urls = url_pattern.findall(text)
        
        # Also check for URLs without protocol
        domain_pattern = re.compile(
            r'(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?'
        )
        potential_urls = domain_pattern.findall(text)
        
        # Add http:// to URLs without protocol
        for url in potential_urls:
            if not url.startswith(('http://', 'https://')):
                urls.append(f'https://{url}')
        
        return list(set(urls))  # Remove duplicates
    
    def check_rate_limit(self, from_number: str) -> bool:
        """Check if user has exceeded rate limit."""
        today = datetime.utcnow().date()
        
        if from_number not in self.rate_limits:
            self.rate_limits[from_number] = {'date': today, 'count': 0}
        
        user_data = self.rate_limits[from_number]
        
        # Reset count if it's a new day
        if user_data['date'] != today:
            user_data['date'] = today
            user_data['count'] = 0
        
        # Check limit
        if user_data['count'] >= self.max_daily_requests:
            return False
        
        # Increment count
        user_data['count'] += 1
        return True
    
    def init_user_session(self, from_number: str):
        """Initialize or update user session."""
        current_time = datetime.utcnow()
        
        if from_number not in self.user_sessions:
            self.user_sessions[from_number] = {
                'start_time': current_time,
                'last_activity': current_time,
                'message_count': 0
            }
        
        # Update last activity
        self.user_sessions[from_number]['last_activity'] = current_time
        self.user_sessions[from_number]['message_count'] += 1
        
        # Clean up old sessions
        self.cleanup_old_sessions()
    
    def cleanup_old_sessions(self):
        """Remove expired user sessions."""
        current_time = datetime.utcnow()
        expired_sessions = []
        
        for from_number, session in self.user_sessions.items():
            if (current_time - session['last_activity']).seconds > self.session_timeout:
                expired_sessions.append(from_number)
        
        for from_number in expired_sessions:
            del self.user_sessions[from_number]
            logger.info(f"Cleaned up expired session for {from_number}")
    
    def run(self, host: str = '0.0.0.0', port: int = 5001, debug: bool = False):
        """Run the Flask application."""
        logger.info(f"Starting MitraVerify WhatsApp Bot on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

def create_app():
    """Create and configure the Flask app."""
    bot = MitraVerifyWhatsAppBot()
    return bot.app

if __name__ == '__main__':
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Create and run bot
    bot = MitraVerifyWhatsAppBot()
    
    # Get configuration from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    bot.run(host=host, port=port, debug=debug)
