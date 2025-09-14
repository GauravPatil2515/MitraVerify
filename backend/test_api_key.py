#!/usr/bin/env python3
"""
Google Cloud API Key Tester
Test the provided API key against various Google Cloud services
"""

import requests
import json
import sys

API_KEY = "AIzaSyBja_KRb6sVsP6LFa8ZR0MjGI3a1XCUe3I"

def test_translation_api():
    """Test Google Cloud Translation API"""
    print("🌍 Testing Google Cloud Translation API...")
    try:
        url = f"https://translation.googleapis.com/language/translate/v2/languages?key={API_KEY}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            languages_count = len(data.get('data', {}).get('languages', []))
            print(f"✅ Translation API: WORKING - {languages_count} languages supported")
            return True
        else:
            print(f"❌ Translation API: ERROR - {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Translation API: ERROR - {e}")
        return False

def test_language_api():
    """Test Google Cloud Natural Language API"""
    print("📝 Testing Google Cloud Natural Language API...")
    try:
        url = f"https://language.googleapis.com/v1/documents:analyzeSentiment?key={API_KEY}"
        
        payload = {
            "document": {
                "content": "MitraVerify is a great application for detecting misinformation!",
                "type": "PLAIN_TEXT"
            }
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            sentiment = data.get('documentSentiment', {})
            score = sentiment.get('score', 0)
            magnitude = sentiment.get('magnitude', 0)
            print(f"✅ Natural Language API: WORKING - Sentiment: {score:.2f}, Magnitude: {magnitude:.2f}")
            return True
        else:
            print(f"❌ Natural Language API: ERROR - {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Natural Language API: ERROR - {e}")
        return False

def test_vision_api():
    """Test Google Cloud Vision API"""
    print("👁️ Testing Google Cloud Vision API...")
    try:
        url = f"https://vision.googleapis.com/v1/images:annotate?key={API_KEY}"
        
        # Use a simple base64 encoded 1x1 pixel image for testing
        test_image_b64 = "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
        
        payload = {
            "requests": [
                {
                    "image": {
                        "content": test_image_b64
                    },
                    "features": [
                        {
                            "type": "LABEL_DETECTION",
                            "maxResults": 5
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            responses = data.get('responses', [])
            if responses and not responses[0].get('error'):
                print("✅ Vision API: WORKING - Image analysis successful")
                return True
            else:
                print("❌ Vision API: ERROR - Image analysis failed")
                return False
        else:
            print(f"❌ Vision API: ERROR - {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Vision API: ERROR - {e}")
        return False

def test_fact_check_api():
    """Test Google Fact Check Tools API"""
    print("🔍 Testing Google Fact Check Tools API...")
    try:
        url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?key={API_KEY}"
        params = {
            'query': 'climate change'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            claims = data.get('claims', [])
            print(f"✅ Fact Check API: WORKING - Found {len(claims)} fact-check results")
            return True
        else:
            print(f"❌ Fact Check API: ERROR - {response.status_code}")
            if response.status_code == 403:
                print("   Note: Fact Check API might not be enabled for this key")
            return False
    except Exception as e:
        print(f"❌ Fact Check API: ERROR - {e}")
        return False

def main():
    """Run all API tests"""
    print("🧪 Google Cloud API Key Testing")
    print("=" * 50)
    print(f"🔑 API Key: {API_KEY[:20]}...")
    print("=" * 50)
    
    results = []
    results.append(test_translation_api())
    results.append(test_language_api())
    results.append(test_vision_api())
    results.append(test_fact_check_api())
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    services = [
        "Translation API",
        "Natural Language API", 
        "Vision API",
        "Fact Check API"
    ]
    
    working_count = 0
    for i, (service, working) in enumerate(zip(services, results)):
        status = "✅ WORKING" if working else "❌ NOT WORKING"
        print(f"{service}: {status}")
        if working:
            working_count += 1
    
    print(f"\n🎯 Result: {working_count}/{len(services)} APIs are working")
    
    if working_count >= 2:
        print("\n🎉 Your API key is ready for MitraVerify!")
        print("💡 Tip: You can start using the app with the working APIs")
    else:
        print("\n⚠️  Limited functionality - consider enabling more APIs")
    
    return working_count

if __name__ == '__main__':
    main()
