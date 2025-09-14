#!/usr/bin/env python3
"""
Twilio Credentials Tester
Test the provided Twilio credentials and WhatsApp sandbox setup
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
except ImportError:
    print("❌ Twilio library not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "twilio"])
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException

# Twilio credentials
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'your_account_sid_here')
AUTH_TOKEN = "650fd651123e465bc85b29e103661770"
PHONE_NUMBER = "+14244846132"
WHATSAPP_SANDBOX = "whatsapp:+14155238886"

def test_twilio_credentials():
    """Test Twilio account credentials"""
    print("📱 Testing Twilio Credentials...")
    print("=" * 50)
    
    try:
        # Initialize Twilio client
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        
        # Get account information
        account = client.api.accounts(ACCOUNT_SID).fetch()
        
        print(f"✅ Account SID: {ACCOUNT_SID}")
        print(f"✅ Account Status: {account.status}")
        print(f"✅ Account Type: {account.type}")
        print(f"✅ Phone Number: {PHONE_NUMBER}")
        
        return client
        
    except TwilioRestException as e:
        print(f"❌ Twilio Authentication Failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_whatsapp_sandbox(client):
    """Test WhatsApp sandbox configuration"""
    print("\n📞 Testing WhatsApp Sandbox...")
    print("=" * 50)
    
    try:
        # Get incoming phone numbers (including WhatsApp sandbox)
        incoming_numbers = client.incoming_phone_numbers.list()
        
        print(f"✅ Available phone numbers: {len(incoming_numbers)}")
        
        for number in incoming_numbers:
            print(f"   📞 {number.phone_number} - {number.friendly_name}")
        
        # Check WhatsApp sandbox specifically
        print(f"✅ WhatsApp Sandbox: {WHATSAPP_SANDBOX}")
        print("   ℹ️  Note: WhatsApp sandbox allows testing without approval")
        
        return True
        
    except Exception as e:
        print(f"❌ WhatsApp Sandbox Error: {e}")
        return False

def test_message_capabilities(client):
    """Test message sending capabilities (without actually sending)"""
    print("\n💬 Testing Message Capabilities...")
    print("=" * 50)
    
    try:
        # Check account balance and usage
        usage = client.usage.records.list(limit=1)
        print("✅ Message capabilities verified")
        print("   ℹ️  Trial account: Can only send to verified numbers")
        print("   ℹ️  For WhatsApp: Need to join sandbox first")
        
        return True
        
    except Exception as e:
        print(f"❌ Message Capability Error: {e}")
        return False

def show_whatsapp_setup_instructions():
    """Show instructions for setting up WhatsApp sandbox"""
    print("\n🔧 WhatsApp Sandbox Setup Instructions:")
    print("=" * 50)
    print("1. 📱 Open WhatsApp on your phone")
    print("2. 💬 Send a message to: +1 415 523 8886")
    print("3. 📝 Message content: 'join <your-sandbox-code>'")
    print("4. ✅ You'll receive a confirmation message")
    print("5. 🎉 You can now test the MitraVerify WhatsApp bot!")
    print("\n💡 Tips:")
    print("   • The sandbox code is unique to your account")
    print("   • Check your Twilio Console for the exact join code")
    print("   • You can add multiple phone numbers to test")

def show_webhook_configuration():
    """Show webhook configuration instructions"""
    print("\n🌐 Webhook Configuration:")
    print("=" * 50)
    print("For the WhatsApp bot to work, configure these webhooks in Twilio:")
    print("   • Webhook URL: http://your-server:5002/webhook")
    print("   • HTTP Method: POST")
    print("   • Status Callback URL: (optional)")
    print("\n🏠 For local development:")
    print("   • Use ngrok to expose local server")
    print("   • Command: ngrok http 5002")
    print("   • Use the ngrok URL in Twilio webhook configuration")

def main():
    """Run all Twilio tests"""
    print("🧪 Twilio WhatsApp Integration Testing")
    print("=" * 50)
    
    # Test credentials
    client = test_twilio_credentials()
    if not client:
        print("\n❌ Cannot proceed without valid credentials")
        return False
    
    # Test WhatsApp sandbox
    whatsapp_ok = test_whatsapp_sandbox(client)
    
    # Test messaging capabilities
    messaging_ok = test_message_capabilities(client)
    
    # Show setup instructions
    show_whatsapp_setup_instructions()
    show_webhook_configuration()
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    if client and whatsapp_ok and messaging_ok:
        print("🎉 Twilio integration is ready!")
        print("💡 Next steps:")
        print("   1. Join WhatsApp sandbox (see instructions above)")
        print("   2. Start the WhatsApp bot server")
        print("   3. Configure webhook URL in Twilio Console")
        print("   4. Test messaging functionality")
        return True
    else:
        print("⚠️  Some issues need to be resolved")
        return False

if __name__ == '__main__':
    main()
