"""
Test script for Cover Letter API endpoint
Tests both file and base64 return formats
"""

import requests
import json
import base64
from pathlib import Path

# API Configuration
API_BASE_URL = "http://localhost:8000"
API_KEY = "nFDqvbuNJb4dwsoL9E6HfyTaPC-O2oeHvK-y1RWDSGU"

# Sample job description for testing
JOB_DESCRIPTION = """
Software Engineer Position at Google

We are seeking a talented Software Engineer to join our Cloud Platform team. 

Responsibilities:
- Design and develop scalable cloud infrastructure
- Build RESTful APIs using Python and FastAPI
- Collaborate with cross-functional teams
- Implement CI/CD pipelines

Requirements:
- 3+ years of Python development experience
- Experience with cloud platforms (AWS, GCP, Azure)
- Strong knowledge of Docker and Kubernetes
- Bachelor's degree in Computer Science or related field

Nice to have:
- Experience with machine learning frameworks
- Knowledge of microservices architecture
- Open-source contributions

Contact: hiring@google.com
Hiring Manager: Sarah Johnson
"""

def test_file_format():
    """Test cover letter generation with file download format"""
    print("\n" + "="*80)
    print("TEST 1: Cover Letter Generation (file format)")
    print("="*80)
    
    url = f"{API_BASE_URL}/api/v1/generate-cover-letter"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "job_description": JOB_DESCRIPTION,
        "resume_text": "Passionate software engineer with experience in cloud computing",
        "context": "Enthusiastic about Google's innovative culture",
        "return_format": "file"
    }
    
    print(f"\n📤 Sending POST request to: {url}")
    print(f"📝 Job description length: {len(JOB_DESCRIPTION)} characters")
    
    response = requests.post(url, headers=headers, json=payload)
    
    print(f"\n📥 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Status: {result['status']}")
        print(f"📄 Message: {result['message']}")
        print(f"📁 Filename: {result['filename']}")
        print(f"🏢 Company: {result['company_name']}")
        print(f"🔗 Download URL: {result.get('download_url', 'N/A')}")
        
        # Check if file exists
        if result.get('download_url'):
            file_path = Path("output/api_generated") / result['filename']
            if file_path.exists():
                print(f"✅ File created successfully: {file_path}")
                print(f"📊 File size: {file_path.stat().st_size} bytes")
            else:
                print(f"❌ File not found at: {file_path}")
    else:
        print(f"❌ Error: {response.text}")


def test_base64_format():
    """Test cover letter generation with base64 format"""
    print("\n" + "="*80)
    print("TEST 2: Cover Letter Generation (base64 format)")
    print("="*80)
    
    url = f"{API_BASE_URL}/api/v1/generate-cover-letter"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "job_description": JOB_DESCRIPTION,
        "context": "Excited about machine learning and cloud technologies",
        "return_format": "base64"
    }
    
    print(f"\n📤 Sending POST request to: {url}")
    
    response = requests.post(url, headers=headers, json=payload)
    
    print(f"\n📥 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Status: {result['status']}")
        print(f"📄 Message: {result['message']}")
        print(f"📁 Filename: {result['filename']}")
        print(f"🏢 Company: {result['company_name']}")
        
        if result.get('cover_letter_base64'):
            # Decode and save base64 content
            base64_content = result['cover_letter_base64']
            print(f"📊 Base64 length: {len(base64_content)} characters")
            
            # Save to file
            output_dir = Path("output/api_tests")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"base64_{result['filename']}"
            
            file_bytes = base64.b64decode(base64_content)
            with open(output_file, 'wb') as f:
                f.write(file_bytes)
            
            print(f"✅ Base64 decoded and saved to: {output_file}")
            print(f"📊 DOCX size: {output_file.stat().st_size} bytes")
    else:
        print(f"❌ Error: {response.text}")


def test_minimal_request():
    """Test with minimal required fields only"""
    print("\n" + "="*80)
    print("TEST 3: Minimal Request (job_description only)")
    print("="*80)
    
    url = f"{API_BASE_URL}/api/v1/generate-cover-letter"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "job_description": "Looking for a Python developer with FastAPI experience."
    }
    
    print(f"\n📤 Sending POST request to: {url}")
    print(f"📝 Minimal payload (only job_description)")
    
    response = requests.post(url, headers=headers, json=payload)
    
    print(f"\n📥 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Status: {result['status']}")
        print(f"📄 Message: {result['message']}")
        print(f"📁 Filename: {result['filename']}")
        print(f"🏢 Company: {result['company_name']}")
    else:
        print(f"❌ Error: {response.text}")


def test_api_health():
    """Test API health endpoint"""
    print("\n" + "="*80)
    print("TEST 0: API Health Check")
    print("="*80)
    
    url = f"{API_BASE_URL}/health"
    
    print(f"\n📤 Sending GET request to: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API Status: {result['status']}")
            print(f"� Checks: {result.get('checks', {})}")
            print(f"🔐 Authentication: {result.get('authentication', 'unknown')}")
            return True
        else:
            print(f"❌ Unexpected response: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: API server not running")
        print("💡 Start the API server with: python api_server.py")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 COVER LETTER API TESTING SUITE")
    print("="*80)
    print(f"📍 API Base URL: {API_BASE_URL}")
    print(f"🔑 API Key: {API_KEY[:20]}...")
    
    # Check if API is running
    if not test_api_health():
        print("\n⚠️  API server not running. Please start it first:")
        print("   python api_server.py")
        exit(1)
    
    # Run all tests
    test_file_format()
    test_base64_format()
    test_minimal_request()
    
    print("\n" + "="*80)
    print("✅ ALL TESTS COMPLETED")
    print("="*80)
    print("\n📁 Check output directories:")
    print("   - output/api_generated/ (file format outputs)")
    print("   - output/api_tests/ (base64 decoded outputs)")
    print("\n")
