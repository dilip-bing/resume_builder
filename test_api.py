"""
Quick Test Script for Resume Optimizer API
Run this to verify the API is working correctly
"""

import requests
import time
import base64

API_URL = "http://localhost:8000"

def test_api():
    """Test the Resume Optimizer API"""
    
    print("\n" + "=" * 70)
    print("Resume Optimizer API - Quick Test")
    print("=" * 70)
    
    # Test 1: Root endpoint
    print("\n[Test 1/4] Testing root endpoint...")
    try:
        response = requests.get(API_URL, timeout=5)
        response.raise_for_status()
        print("✅ Root endpoint working")
        print(f"   Response: {response.json()['service']}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        print("\n⚠️  Make sure the API server is running:")
        print("   python start_api.py")
        return False
    
    # Test 2: Health check
    print("\n[Test 2/4] Testing health check...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        response.raise_for_status()
        health = response.json()
        
        print(f"✅ Health check: {health['status']}")
        
        # Check all components
        checks = health.get('checks', {})
        all_good = True
        for check, status in checks.items():
            icon = "✅" if status else "❌"
            print(f"   {icon} {check}")
            if not status:
                all_good = False
        
        if not all_good:
            print("\n⚠️  Some components are not healthy. Please fix before proceeding.")
            return False
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 3: Get template
    print("\n[Test 3/4] Testing template endpoint...")
    try:
        response = requests.get(f"{API_URL}/api/v1/template", timeout=5)
        response.raise_for_status()
        template = response.json()
        
        print("✅ Template retrieved successfully")
        print(f"   Name: {template['template']['personal']['name']['value']}")
        print(f"   Skills: {len(template['template'].get('skills', {}))} categories")
        
    except Exception as e:
        print(f"❌ Template endpoint failed: {e}")
        return False
    
    # Test 4: Optimize resume
    print("\n[Test 4/4] Testing resume optimization...")
    print("   (This may take 10-30 seconds...)")
    
    test_job_description = """
    Senior Software Engineer - Full Stack
    
    Requirements:
    - 5+ years of experience with Python and JavaScript
    - Strong experience with React.js and modern frontend frameworks
    - Experience with AWS cloud services
    - Proficiency in MongoDB or other NoSQL databases
    - Experience with Docker and containerization
    - Strong problem-solving and communication skills
    
    Responsibilities:
    - Design and implement scalable web applications
    - Lead technical decisions and mentor junior developers
    """
    
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{API_URL}/api/v1/optimize",
            json={
                "job_description": test_job_description,
                "return_format": "base64"
            },
            timeout=120
        )
        response.raise_for_status()
        result = response.json()
        
        elapsed = time.time() - start_time
        
        print(f"✅ Optimization complete in {elapsed:.1f} seconds")
        print(f"   Match Score: {result.get('match_score', 'N/A')}")
        print(f"   Keywords Added: {result.get('keywords_added', 0)}")
        print(f"   Filename: {result.get('filename', 'N/A')}")
        
        # Save test resume
        if 'resume_base64' in result:
            resume_data = base64.b64decode(result['resume_base64'])
            test_output = "test_resume.docx"
            with open(test_output, 'wb') as f:
                f.write(resume_data)
            print(f"   💾 Test resume saved: {test_output}")
            print(f"   File size: {len(resume_data):,} bytes")
        
    except requests.exceptions.Timeout:
        print("❌ Optimization timed out (>120 seconds)")
        return False
    except Exception as e:
        print(f"❌ Optimization failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # All tests passed
    print("\n" + "=" * 70)
    print("✅ All tests passed! API is working correctly.")
    print("=" * 70)
    print("\n📚 Next steps:")
    print("   1. Check API documentation: http://localhost:8000/docs")
    print("   2. See client_example.py for usage examples")
    print("   3. Read API_README.md for full documentation")
    print("=" * 70 + "\n")
    
    return True

if __name__ == "__main__":
    success = test_api()
    exit(0 if success else 1)
