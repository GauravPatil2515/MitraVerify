#!/usr/bin/env python3
"""
Production-ready MitraVerify Backend Server
Stable version without debug mode
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

# Set environment variables for production
os.environ['FLASK_ENV'] = 'production'
os.environ['DEBUG'] = 'False'

# Import and run the app
from backend.app_simple import app

if __name__ == '__main__':
    print("🚀 Starting MitraVerify Backend (Production Mode)")
    print("=" * 50)
    print("✅ Debug mode: DISABLED")
    print("✅ Auto-reload: DISABLED") 
    print("✅ Port: 5000")
    print("✅ CORS: Enabled for frontend")
    print()
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,  # Disable debug mode
        use_reloader=False,  # Disable auto-reload
        threaded=True  # Enable threading for better performance
    )
