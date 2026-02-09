"""
Automated Job Application Script
Use this to apply to multiple jobs with tailored resumes

WORKFLOW:
1. Add job descriptions to jobs list below
2. Run this script
3. Get optimized resume for each job
4. Use resumes to apply (manual or automated)
"""

import requests
import base64
import time
from datetime import datetime
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

# API URL - Update after deploying to Render
API_URL = "http://localhost:8000"  # Local
# API_URL = "https://resume-optimizer-api.onrender.com"  # Remote (uncomment after deploy)

# API Secret Key - Get this from start_api.py output or .streamlit/secrets.toml
# This protects your API from unauthorized use
API_SECRET_KEY = "your-api-secret-key-here"  # UPDATE THIS!

# Output directory for resumes
OUTPUT_DIR = "generated_resumes"

# ============================================================
# JOB DESCRIPTIONS
# ============================================================

# Add your job descriptions here
JOBS = [
    {
        "company": "Example Company 1",
        "role": "Software Engineer",
        "job_url": "https://example.com/job1",
        "description": """
        Paste the full job description here...
        
        Requirements:
        - ...
        
        Responsibilities:
        - ...
        """
    },
    {
        "company": "Example Company 2",
        "role": "Backend Developer",
        "job_url": "https://example.com/job2",
        "description": """
        Paste another job description here...
        """
    },
    # Add more jobs here...
]

# ============================================================
# Main Functions
# ============================================================

def optimize_resume(job_description: str, timeout: int = 120):
    """
    Call API to optimize resume
    
    Args:
        job_description: Full job posting text
        timeout: Request timeout in seconds
    
    Returns:
        dict: API response with resume and match info
    """
    
    try:
        response = requests.post(
            f"{API_URL}/api/v1/optimize",
            json={
                "job_description": job_description,
                "return_format": "base64"
            },
            headers={
                "X-API-Key": API_SECRET_KEY
            },
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.Timeout:
        print("   ❌ Timeout - job description too long or API slow")
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("   ❌ Authentication failed - API key missing")
            print("   Update API_SECRET_KEY in this file")
        elif e.response.status_code == 403:
            print("   ❌ Authentication failed - Invalid API key")
            print("   Get the correct key from start_api.py output")
        else:
            print(f"   ❌ HTTP Error: {e}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Cannot connect to {API_URL}")
        print(f"   Make sure API is running!")
        return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def save_resume(resume_base64: str, filename: str):
    """
    Save base64-encoded resume to file
    
    Args:
        resume_base64: Base64-encoded DOCX file
        filename: Output filename
    
    Returns:
        str: Full path to saved file
    """
    
    # Create output directory
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    
    # Decode and save
    resume_data = base64.b64decode(resume_base64)
    filepath = Path(OUTPUT_DIR) / filename
    
    with open(filepath, 'wb') as f:
        f.write(resume_data)
    
    return str(filepath)

def process_jobs(jobs: list):
    """
    Process all jobs and generate optimized resumes
    
    Args:
        jobs: List of job dicts
    
    Returns:
        list: Results for each job
    """
    
    print("\n" + "="*80)
    print(f"🚀 Automated Job Application - Processing {len(jobs)} Jobs")
    print("="*80)
    
    # Check API key is set
    if not API_SECRET_KEY or API_SECRET_KEY == "your-api-secret-key-here":
        print("\n❌ ERROR: API_SECRET_KEY not configured!")
        print("\nSteps to fix:")
        print("1. Run: python start_api.py")
        print("2. Copy the 'Your API Secret Key' value")
        print("3. Update API_SECRET_KEY in this file (line 22)")
        return []
    
    # Check API first
    print(f"\n🔍 Checking API: {API_URL}")
    try:
        health = requests.get(f"{API_URL}/health", timeout=10).json()
        if health.get('status') != 'healthy':
            print("❌ API is not healthy!")
            return []
        if health.get('authentication') == 'enabled':
            print("✅ API is ready (authentication enabled)")
        else:
            print("⚠️  API is ready (authentication disabled - not secure!)")
    except Exception as e:
        print(f"❌ API check failed: {e}")
        print("\nMake sure API is running:")
        print("  Local: python start_api.py")
        print("  Remote: Check Render dashboard")
        return []
    
    results = []
    
    # Process each job
    for i, job in enumerate(jobs, 1):
        print(f"\n{'='*80}")
        print(f"📌 Job {i}/{len(jobs)}: {job['company']} - {job['role']}")
        print("="*80)
        
        if not job.get('description') or len(job['description'].strip()) < 50:
            print("⚠️  Skipping - no valid job description")
            results.append({
                'job': job,
                'success': False,
                'error': 'No description'
            })
            continue
        
        # Optimize resume
        print(f"⏳ Optimizing resume (this may take 10-30 seconds)...")
        start_time = time.time()
        
        result = optimize_resume(job['description'])
        
        if not result:
            results.append({
                'job': job,
                'success': False,
                'error': 'API call failed'
            })
            continue
        
        elapsed = time.time() - start_time
        
        # Save resume
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{job['company'].replace(' ', '_')}_{job['role'].replace(' ', '_')}_{timestamp}.docx"
        
        filepath = save_resume(result['resume_base64'], filename)
        
        # Print results
        print(f"✅ Complete in {elapsed:.1f}s")
        print(f"   📊 Match Score: {result.get('match_score', 'N/A')}")
        print(f"   🔑 Keywords Added: {result.get('keywords_added', 0)}")
        print(f"   💾 Resume saved: {filepath}")
        
        results.append({
            'job': job,
            'success': True,
            'filepath': filepath,
            'match_score': result.get('match_score'),
            'keywords_added': result.get('keywords_added'),
            'time_taken': elapsed
        })
        
        # Small delay between requests (be nice to API)
        if i < len(jobs):
            print("   ⏳ Waiting 2 seconds before next job...")
            time.sleep(2)
    
    # Summary
    print_summary(results)
    
    return results

def print_summary(results: list):
    """Print summary of all processed jobs"""
    
    print("\n" + "="*80)
    print("📊 PROCESSING SUMMARY")
    print("="*80)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\n✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    
    if successful:
        print(f"\n{'='*80}")
        print("✅ SUCCESSFUL OPTIMIZATIONS")
        print("="*80)
        
        for r in successful:
            print(f"\n📄 {r['job']['company']} - {r['job']['role']}")
            print(f"   File: {r['filepath']}")
            print(f"   Match: {r['match_score']}")
            print(f"   Keywords: {r['keywords_added']}")
            print(f"   Time: {r['time_taken']:.1f}s")
            if r['job'].get('job_url'):
                print(f"   URL: {r['job']['job_url']}")
    
    if failed:
        print(f"\n{'='*80}")
        print("❌ FAILED OPTIMIZATIONS")
        print("="*80)
        
        for r in failed:
            print(f"\n📄 {r['job']['company']} - {r['job']['role']}")
            print(f"   Error: {r.get('error', 'Unknown')}")
    
    print("\n" + "="*80)
    print("🎯 NEXT STEPS")
    print("="*80)
    print(f"\n1. Check resumes in: {OUTPUT_DIR}/")
    print("2. Review each resume before applying")
    print("3. Apply to jobs using tailored resumes")
    print("4. Track applications and responses")
    print("\n💡 Tip: Upload resumes directly on job portals or via email")
    print("="*80 + "\n")

# ============================================================
# Run Script
# ============================================================

if __name__ == "__main__":
    
    print("\n" + "="*80)
    print("🤖 AUTOMATED JOB APPLICATION - RESUME OPTIMIZER")
    print("="*80)
    print(f"\nAPI: {API_URL}")
    print(f"Output: {OUTPUT_DIR}/")
    print(f"Jobs: {len(JOBS)}")
    
    # Validate jobs
    valid_jobs = [j for j in JOBS if j.get('description') and len(j['description'].strip()) >= 50]
    
    if not valid_jobs:
        print("\n❌ ERROR: No valid jobs found!")
        print("\nPlease add job descriptions to the JOBS list in this file.")
        print("Each job should have:")
        print("  - company: Company name")
        print("  - role: Job title")
        print("  - description: Full job posting (at least 50 characters)")
        print("  - job_url: Link to job (optional)")
        exit(1)
    
    if len(valid_jobs) < len(JOBS):
        print(f"\n⚠️  Warning: {len(JOBS) - len(valid_jobs)} jobs have invalid descriptions")
    
    print(f"\n📋 Processing {len(valid_jobs)} valid jobs")
    print("="*80)
    
    # Confirm
    try:
        input("\nPress Enter to start processing (or Ctrl+C to cancel)...")
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        exit(0)
    
    # Process all jobs
    results = process_jobs(valid_jobs)
    
    # Done
    if results:
        successful = sum(1 for r in results if r['success'])
        print(f"\n🎉 Generated {successful} optimized resumes!")
        print(f"📁 Check: {OUTPUT_DIR}/\n")
    else:
        print("\n❌ No resumes generated. Check API connection.\n")
