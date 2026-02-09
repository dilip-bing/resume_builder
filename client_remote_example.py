"""
Remote API Client Example
Use this to call your deployed API from anywhere
"""

import requests
import base64
import time
from pathlib import Path

# ============================================================
# CONFIGURATION - Update this with your deployed API URL
# ============================================================

# After deploying to Render, replace this with your actual URL
API_URL = "https://resume-optimizer-api.onrender.com"

# Or use local API for testing
# API_URL = "http://localhost:8000"

# API Secret Key - Get this from start_api.py or your deployment settings
# This protects your API from unauthorized use
API_SECRET_KEY = "your-api-secret-key-here"  # UPDATE THIS!

# ============================================================

def check_api_status():
    """Check if remote API is online"""
    
    print(f"\n🔍 Checking API status: {API_URL}")
    
    try:
        start = time.time()
        response = requests.get(f"{API_URL}/health", timeout=60)
        elapsed = time.time() - start
        
        response.raise_for_status()
        health = response.json()
        
        print(f"✅ API is {health['status']} (responded in {elapsed:.1f}s)")
        
        if elapsed > 10:
            print("   ⚠️  Note: Slow response = API was sleeping (cold start)")
            print("   Next requests will be faster!")
        
        checks = health.get('checks', {})
        for check, status in checks.items():
            icon = "✅" if status else "❌"
            print(f"   {icon} {check}")
        
        return True
        
    except requests.exceptions.Timeout:
        print("❌ API timeout - might be waking up from sleep")
        print("   Try again in 30 seconds")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {API_URL}")
        print("   Make sure API is deployed or running locally")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def optimize_resume_remote(job_description: str, output_filename: str = None):
    """
    Optimize resume using remote API
    
    Args:
        job_description: Full job posting text
        output_filename: Where to save resume (optional)
    
    Returns:
        dict: Optimization results
    """
    
    print(f"\n{'='*70}")
    print("Remote Resume Optimization")
    print('='*70)
    print(f"API: {API_URL}")
    print(f"Job description: {len(job_description)} characters")
    print('='*70)
    
    # Make request
    print("\n⏳ Sending request to remote API...")
    print("   (This may take 10-40 seconds including AI processing)")
    
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{API_URL}/api/v1/optimize",
            json={
                "job_description": job_description,
                "return_format": "base64"
            },
            headers={
                "X-API-Key": API_SECRET_KEY
            },
            timeout=120  # 2 minute timeout
        )
        response.raise_for_status()
        
        elapsed = time.time() - start_time
        result = response.json()
        
        print(f"✅ Optimization complete in {elapsed:.1f} seconds")
        print(f"\n📊 Results:")
        print(f"   Match Score: {result.get('match_score', 'N/A')}")
        print(f"   Keywords Added: {result.get('keywords_added', 0)}")
        print(f"   Filename: {result.get('filename', 'N/A')}")
        
        # Save resume
        if 'resume_base64' in result:
            resume_data = base64.b64decode(result['resume_base64'])
            
            if not output_filename:
                output_filename = f"resume_optimized_{int(time.time())}.docx"
            
            with open(output_filename, 'wb') as f:
                f.write(resume_data)
            
            print(f"\n💾 Resume saved: {output_filename}")
            print(f"   File size: {len(resume_data):,} bytes")
        
        print('='*70 + "\n")
        
        return result
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out (>120 seconds)")
        print("   Job description might be too long")
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("❌ Authentication error: Missing API key")
            print("   Update API_SECRET_KEY in this file")
        elif e.response.status_code == 403:
            print("❌ Authentication error: Invalid API key")
            print("   Get the correct key from your API deployment")
        else:
            print(f"❌ API error: {e}")
            try:
                error = response.json()
                print(f"   Detail: {error.get('detail', 'Unknown error')}")
            except:
                pass
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def batch_optimize_remote(jobs: list):
    """
    Optimize resumes for multiple jobs using remote API
    
    Args:
        jobs: List of dicts with 'company', 'role', 'description' keys
    
    Returns:
        list: Results for each job
    """
    
    print(f"\n{'='*70}")
    print(f"Batch Optimization - {len(jobs)} Jobs")
    print('='*70)
    
    results = []
    
    for i, job in enumerate(jobs, 1):
        print(f"\n📌 Job {i}/{len(jobs)}: {job['company']} - {job['role']}")
        
        output_file = f"resume_{job['company'].replace(' ', '_')}_{job['role'].replace(' ', '_')}.docx"
        
        result = optimize_resume_remote(
            job_description=job['description'],
            output_filename=output_file
        )
        
        if result:
            results.append({
                'company': job['company'],
                'role': job['role'],
                'file': output_file,
                'match_score': result.get('match_score'),
                'keywords_added': result.get('keywords_added'),
                'success': True
            })
        else:
            results.append({
                'company': job['company'],
                'role': job['role'],
                'file': None,
                'success': False
            })
        
        # Small delay between requests
        if i < len(jobs):
            time.sleep(2)
    
    # Summary
    print(f"\n{'='*70}")
    print("Batch Processing Summary")
    print('='*70)
    
    successful = sum(1 for r in results if r['success'])
    print(f"\n✅ Successful: {successful}/{len(jobs)}")
    
    for r in results:
        if r['success']:
            print(f"\n✅ {r['company']} - {r['role']}")
            print(f"   File: {r['file']}")
            print(f"   Match: {r['match_score']}")
            print(f"   Keywords: {r['keywords_added']}")
        else:
            print(f"\n❌ {r['company']} - {r['role']} - FAILED")
    
    print('='*70 + "\n")
    
    return results

# ============================================================
# Example Usage
# ============================================================

if __name__ == "__main__":
    
    print("\n" + "="*70)
    print("Resume Optimizer - Remote API Client")
    print("="*70)
    print(f"\n🌐 Using API: {API_URL}")
    print("\n💡 Use case: Call API from anywhere to get optimized resumes")
    print("="*70)
    
    # Check if API key is configured
    if not API_SECRET_KEY or API_SECRET_KEY == "your-api-secret-key-here":
        print("\n❌ ERROR: API_SECRET_KEY not configured!")
        print("\nSteps to fix:")
        print("1. If using local API:")
        print("   - Run: python start_api.py")
        print("   - Copy the 'Your API Secret Key' value")
        print("2. If using remote API (Render):")
        print("   - Check your Render dashboard")
        print("   - Look for API_SECRET_KEY environment variable")
        print("3. Update API_SECRET_KEY in this file (line 22)")
        print("="*70)
        exit(1)
    
    # Step 1: Check if API is online
    if not check_api_status():
        print("\n⚠️  API is not responding. Please check:")
        print("   1. Is the API deployed on Render?")
        print("   2. Is the URL correct in this file?")
        print("   3. Try again in 30 seconds (cold start)")
        exit(1)
    
    # Wait a moment after cold start
    time.sleep(2)
    
    # Step 2: Example 1 - Single Job Application
    print("\n" + "="*70)
    print("Example 1: Single Job Application")
    print("="*70)
    
    job_description = """
    Senior Full Stack Developer
    
    We're looking for a talented Senior Full Stack Developer to join our team.
    
    Requirements:
    - 5+ years of experience in full stack development
    - Strong proficiency in Python, JavaScript, React, and Node.js
    - Experience with AWS cloud services and Docker containerization
    - Solid understanding of MongoDB and database design
    - Experience with REST APIs and microservices architecture
    - Strong problem-solving skills and attention to detail
    
    Responsibilities:
    - Design and develop scalable web applications
    - Lead technical architecture decisions
    - Mentor junior developers
    - Collaborate with product and design teams
    - Ensure code quality through testing and reviews
    
    Nice to have:
    - Experience with mobile app development (iOS/Android)
    - DevOps and CI/CD pipeline experience
    - Machine learning or AI background
    """
    
    result = optimize_resume_remote(
        job_description=job_description,
        output_filename="resume_fullstack_developer.docx"
    )
    
    if result:
        print("✅ Resume ready to use for job application!")
    
    # Step 3: Example 2 - Batch Processing
    print("\n" + "="*70)
    print("Example 2: Batch Processing Multiple Jobs")
    print("="*70)
    
    job_list = [
        {
            "company": "TechCorp",
            "role": "Backend Developer",
            "description": """
            Backend Developer position. Looking for Python expertise with Django/Flask.
            Experience with AWS, Docker, PostgreSQL required.
            Microservices architecture, REST APIs, CI/CD.
            """
        },
        {
            "company": "DataInc",
            "role": "Data Engineer",
            "description": """
            Data Engineer role. Need experience with Python, SQL, and ETL pipelines.
            AWS services (S3, Redshift, Glue), Apache Airflow, data warehousing.
            Big data technologies, data modeling, and optimization.
            """
        },
        {
            "company": "StartupXYZ",
            "role": "Mobile Developer",
            "description": """
            Mobile Developer position. iOS and Android development required.
            Swift, Kotlin, React Native experience preferred.
            App architecture, testing, App Store deployment.
            """
        }
    ]
    
    print("\n⚠️  Note: Processing 3 jobs will take ~1-2 minutes")
    print("Press Ctrl+C to skip batch processing\n")
    
    try:
        input("Press Enter to continue with batch processing...")
        
        batch_results = batch_optimize_remote(job_list)
        
        print("\n🎉 Batch processing complete!")
        print("   You now have tailored resumes for each job")
        
    except KeyboardInterrupt:
        print("\n\n⏭️  Skipped batch processing")
    
    # Done
    print("\n" + "="*70)
    print("✅ Examples Complete")
    print("="*70)
    print("\n💡 Next Steps:")
    print("   1. Use optimized resumes for job applications")
    print("   2. Integrate into your automation workflow")
    print("   3. Call API from any script, any location!")
    print("\n📚 Documentation:")
    print("   - API Docs: " + API_URL + "/docs")
    print("   - Deployment: See DEPLOY_RENDER.md")
    print("="*70 + "\n")
