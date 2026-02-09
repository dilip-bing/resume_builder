"""
Simple API Test Script
Test your deployed Render API quickly
"""

import requests
import json

# ============================================================
# PASTE YOUR VALUES HERE
# ============================================================

# Your Render URL (after deployment)
API_URL = "https://resume-optimizer-api-fvpd.onrender.com"  # ← PASTE YOUR RENDER URL HERE

# Your API Secret Key (from Render environment variables)
API_SECRET_KEY = "nFDqvbuNJb4dwsoL9E6HfyTaPC-O2oeHvK-y1RWDSGU"  # ← PASTE YOUR API KEY HERE

# ============================================================

print("\n" + "="*70)
print("Testing Remote API")
print("="*70)
print(f"URL: {API_URL}")
print(f"API Key: {API_SECRET_KEY[:20]}..." if len(API_SECRET_KEY) > 20 else f"API Key: {API_SECRET_KEY}")
print("="*70)

# Check if values are set
if "PASTE_YOUR" in API_URL or "PASTE_YOUR" in API_SECRET_KEY:
    print("\n❌ ERROR: Please update the script first!")
    print("   1. Paste your Render URL (line 12)")
    print("   2. Paste your API Secret Key (line 15)")
    exit(1)

# Test 1: Health Check
print("\n[1/2] Testing health endpoint...")
print("⏳ If this is the first request, it may take 30-60 seconds (cold start)...")
try:
    response = requests.get(f"{API_URL}/health", timeout=60)
    print(f"✅ Status: {response.status_code}")
    
    health = response.json()
    print(f"✅ Health: {health.get('status')}")
    print(f"✅ Authentication: {health.get('authentication')}")
    
except Exception as e:
    print(f"❌ Health check failed: {e}")
    print("\nPossible issues:")
    print("  - Wrong Render URL")
    print("  - API not deployed yet")
    print("  - API is sleeping (wait 30 seconds and try again)")
    exit(1)

# Test 2: Optimize Resume
print("\n[2/2] Testing optimization endpoint...")
print("⏳ This will take 10-60 seconds (AI processing + possible cold start)...")

test_job = "Software Engineer with Python, React, and AWS experience required."

try:
    response = requests.post(
        f"{API_URL}/api/v1/optimize",
        json={
            "job_description": test_job,
            "return_format": "base64"
        },
        headers={
            "X-API-Key": API_SECRET_KEY
        },
        timeout=120
    )
    
    if response.status_code == 401:
        print("❌ Authentication failed: Missing API key")
        print("   Make sure API_SECRET_KEY is correct")
        exit(1)
    elif response.status_code == 403:
        print("❌ Authentication failed: Invalid API key")
        print("   Check your API_SECRET_KEY value")
        print("   It should match the one in Render environment variables")
        exit(1)
    
    response.raise_for_status()
    result = response.json()
    
    print(f"✅ Optimization successful!")
    print(f"   Match Score: {result.get('match_score')}")
    print(f"   Keywords Added: {result.get('keywords_added')}")
    print(f"   Filename: {result.get('filename')}")
    
    if 'resume_base64' in result:
        print(f"   Resume received: {len(result['resume_base64'])} characters (base64)")
    
except requests.exceptions.Timeout:
    print("❌ Timeout (>120 seconds)")
    print("   API might be slow or job description too long")
except Exception as e:
    print(f"❌ Optimization failed: {e}")
    exit(1)

# Success!
print("\n" + "="*70)
print("✅ ALL TESTS PASSED!")
print("="*70)
print("\n🎉 Your API is working correctly!")
print("\nNext steps:")
print("  1. Update automate_applications.py with these values")
print("  2. Add job descriptions to the JOBS list")
print("  3. Run: python automate_applications.py")
print("="*70 + "\n")
