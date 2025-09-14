#!/usr/bin/env python3
"""
WhatsApp Bot Tester and Message Sender
Send test messages and verify WhatsApp integration with MitraVerify
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
except ImportError:
    print("❌ Installing Twilio...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "twilio"])
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException

# Twilio configuration
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'your_account_sid_here')
AUTH_TOKEN = "650fd651123e465bc85b29e103661770"
WHATSAPP_FROM = "whatsapp:+14155238886"
TEST_NUMBER = "whatsapp:+919892130048"

def verify_phone_number(client, phone_number):
    """Add phone number to verified caller list for trial account"""
    try:
        print(f"📱 Adding {phone_number} to verified callers...")
        
        # For trial accounts, numbers need to be verified first
        validation_request = client.validation_requests.create(
            phone_number=phone_number.replace("whatsapp:", ""),
            friendly_name="MitraVerify Test Number"
        )
        
        print(f"✅ Verification request sent to {phone_number}")
        print(f"📝 Validation code will be sent via SMS")
        return validation_request.validation_code
        
    except Exception as e:
        print(f"⚠️  Phone verification: {e}")
        return None

def send_welcome_message(client, to_number):
    """Send welcome message to introduce MitraVerify bot"""
    try:
        welcome_text = """
🤖 *Welcome to MitraVerify!*

I'm your AI-powered misinformation detection assistant!

🔍 *What I can verify:*
📝 Text messages and news
📸 Images and photos  
🔗 URLs and links

💡 *How to use:*
• Send me any content to verify
• I'll analyze it instantly
• Get detailed verification results

🚀 *Try me now!*
Send any suspicious news, image, or link and I'll help you verify if it's true or false.

Type 'help' for more options.
        """
        
        message = client.messages.create(
            body=welcome_text.strip(),
            from_=WHATSAPP_FROM,
            to=to_number
        )
        
        print(f"✅ Welcome message sent successfully!")
        print(f"📱 Message SID: {message.sid}")
        return message
        
    except TwilioRestException as e:
        print(f"❌ Failed to send message: {e}")
        if "not a valid phone number" in str(e):
            print("💡 Note: Phone number needs to be verified for trial account")
        elif "is not a verified" in str(e):
            print("💡 Note: Add +919892130048 to verified phone numbers in Twilio Console")
        return None

def send_demo_verification(client, to_number):
    """Send a demo verification example"""
    try:
        demo_text = """
🧪 *Demo Verification Result*

📝 *Sample Content:* "Breaking: Scientists discover miracle cure that doctors don't want you to know!"

🔍 *Analysis Result:*
❌ *Status:* Likely False
📊 *Confidence:* 87%

⚠️ *Red Flags Detected:*
• Emotional manipulation language
• "Doctors don't want you to know" 
• Missing credible sources
• Urgency keywords

💡 *Educational Tip:*
Be skeptical of health claims that:
- Promise "miracle" cures
- Claim conspiracies
- Lack scientific sources
- Use emotional language

🎯 *Always verify with multiple trusted sources!*
        """
        
        message = client.messages.create(
            body=demo_text.strip(),
            from_=WHATSAPP_FROM,
            to=to_number
        )
        
        print(f"✅ Demo verification sent successfully!")
        print(f"📱 Message SID: {message.sid}")
        return message
        
    except TwilioRestException as e:
        print(f"❌ Failed to send demo: {e}")
        return None

def test_sandbox_join():
    """Test joining WhatsApp sandbox"""
    print("📱 WhatsApp Sandbox Setup:")
    print("=" * 50)
    print("To test the bot, join the sandbox first:")
    print("")
    print("1. 📱 Open WhatsApp on your phone")
    print("2. 💬 Send message to: +1 415 523 8886") 
    print("3. 📝 Message: 'join <sandbox-code>'")
    print("4. ✅ Wait for confirmation")
    print("5. 🎉 Start testing!")
    print("")
    print("💡 Find your sandbox code here:")
    print("🌐 https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn")

def check_twilio_console_setup():
    """Instructions for Twilio Console setup"""
    print("🔧 Twilio Console Setup for Trial Account:")
    print("=" * 50)
    print("Since you're using a trial account, follow these steps:")
    print("")
    print("1. 🌐 Go to: https://console.twilio.com/")
    print("2. 📱 Navigate to: Phone Numbers > Manage > Verified Caller IDs")
    print("3. ➕ Click 'Add a new number'")
    print("4. 📞 Enter: +919892130048")
    print("5. 📲 Verify via SMS/Call")
    print("6. ✅ Once verified, you can receive messages")
    print("")
    print("🔄 Alternative - Use WhatsApp Sandbox:")
    print("• No phone verification needed")
    print("• Join sandbox with your WhatsApp number")
    print("• Test immediately")

def main():
    """Main function to test WhatsApp integration"""
    print("🧪 MitraVerify WhatsApp Bot Testing")
    print("=" * 50)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📞 Target Number: +919892130048")
    print("=" * 50)
    
    try:
        # Initialize Twilio client
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        
        # Show setup instructions first
        test_sandbox_join()
        print("\n" + "=" * 50)
        check_twilio_console_setup()
        
        print("\n" + "=" * 50)
        print("🚀 TESTING OPTIONS")
        print("=" * 50)
        
        choice = input("""
Choose an option:
1. 📱 Send welcome message (requires verified number)
2. 🧪 Send demo verification 
3. 📋 Show setup instructions only
4. 🔍 Check account status

Enter choice (1-4): """).strip()
        
        if choice == "1":
            print("\n📤 Attempting to send welcome message...")
            message = send_welcome_message(client, TEST_NUMBER)
            if message:
                print("🎉 Message sent successfully!")
            else:
                print("❌ Message failed - number may need verification")
                
        elif choice == "2":
            print("\n📤 Attempting to send demo verification...")
            message = send_demo_verification(client, TEST_NUMBER)
            if message:
                print("🎉 Demo sent successfully!")
            else:
                print("❌ Demo failed - number may need verification")
                
        elif choice == "3":
            print("\n📋 Setup instructions displayed above")
            
        elif choice == "4":
            account = client.api.accounts(ACCOUNT_SID).fetch()
            print(f"\n📊 Account Status: {account.status}")
            print(f"🏷️  Account Type: {account.type}")
            print(f"💰 Account Balance: Check Twilio Console")
            
        else:
            print("❌ Invalid choice")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("💡 NEXT STEPS")
    print("=" * 50)
    print("1. ✅ Join WhatsApp sandbox OR verify phone number")
    print("2. 📱 Send messages to test the bot")
    print("3. 🧪 Try text, image, and URL verification")
    print("4. 🌐 Use the web interface: http://localhost:3000")

if __name__ == '__main__':
    main()
