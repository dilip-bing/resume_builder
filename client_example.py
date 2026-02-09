"""
Example client for Resume Optimizer API
Demonstrates how to use the API in automation workflows
"""

import requests
import json
import base64
from pathlib import Path

# API Configuration
API_BASE_URL = "http://localhost:8000"  # Change to your deployed URL
API_ENDPOINT = f"{API_BASE_URL}/api/v1/optimize"

def optimize_resume_for_job(job_description: str, output_path: str = None, use_base64: bool = False):
    """
    Optimize resume for a specific job description
    
    Args:
        job_description: Full text of the job posting
        output_path: Where to save the resume (optional)
        use_base64: If True, get base64-encoded file in response, else get download link
    
    Returns:
        dict: Response with resume information
    """
    
    print(f"\n{'='*70}")
    print("Resume Optimization Request")
    print('='*70)
    print(f"Job description length: {len(job_description)} characters")
    print(f"Return format: {'base64' if use_base64 else 'file'}")
    print('='*70)
    
    # Prepare request
    payload = {
        "job_description": job_description,
        "return_format": "base64" if use_base64 else "file"
    }
    
    # Make API call
    print("\n[1/3] Sending optimization request to API...")
    try:
        response = requests.post(
            API_ENDPOINT,
            json=payload,
            timeout=120  # 2 minute timeout for AI processing
        )
        response.raise_for_status()
        
    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timed out. Job description might be too long.")
        return None
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR: Cannot connect to API at {API_BASE_URL}")
        print("   Make sure the API server is running: python api_server.py")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"❌ ERROR: API returned error: {e}")
        try:
            error_detail = response.json()
            print(f"   Detail: {error_detail.get('detail', 'Unknown error')}")
        except:
            pass
        return None
    
    result = response.json()
    
    print(f"✅ Optimization successful!")
    print(f"\n[2/3] Optimization Results:")
    print(f"   Match Score: {result.get('match_score', 'N/A')}")
    print(f"   Keywords Added: {result.get('keywords_added', 0)}")
    print(f"   Filename: {result.get('filename', 'N/A')}")
    
    # Download or save resume
    print(f"\n[3/3] Getting resume file...")
    
    if use_base64:
        # Decode base64 and save
        if 'resume_base64' not in result:
            print("❌ ERROR: No base64 data in response")
            return result
        
        resume_data = base64.b64decode(result['resume_base64'])
        
        # Determine output path
        if not output_path:
            output_path = f"resume_optimized_{result.get('filename', 'output.docx')}"
        
        # Save to file
        with open(output_path, 'wb') as f:
            f.write(resume_data)
        
        print(f"✅ Resume saved to: {output_path}")
        print(f"   File size: {len(resume_data):,} bytes")
    
    else:
        # Download from URL
        if 'download_url' not in result:
            print("❌ ERROR: No download URL in response")
            return result
        
        download_url = API_BASE_URL + result['download_url']
        
        # Download file
        download_response = requests.get(download_url)
        download_response.raise_for_status()
        
        # Determine output path
        if not output_path:
            output_path = result.get('filename', 'resume_optimized.docx')
        
        # Save to file
        with open(output_path, 'wb') as f:
            f.write(download_response.content)
        
        print(f"✅ Resume downloaded to: {output_path}")
        print(f"   File size: {len(download_response.content):,} bytes")
    
    print('='*70 + "\n")
    
    return result

def check_api_health():
    """Check if API is running and healthy"""
    
    print("\nChecking API health...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        response.raise_for_status()
        health = response.json()
        
        print(f"Status: {health.get('status', 'unknown')}")
        print(f"Checks:")
        for check, status in health.get('checks', {}).items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {check}")
        
        return health.get('status') == 'healthy'
    
    except Exception as e:
        print(f"❌ API not accessible: {e}")
        return False

def get_template():
    """Get the current resume template"""
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/template")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Failed to get template: {e}")
        return None

# Example usage
if __name__ == "__main__":
    
    # Example 1: Single job application
    print("\n" + "="*70)
    print("Example 1: Single Job Application")
    print("="*70)
    
    job_description = """
    Senior Software Engineer - Full Stack
    
    We are seeking a talented Senior Software Engineer to join our team.
    
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
    - Collaborate with cross-functional teams
    - Ensure code quality through reviews and testing
    """
    
    # Check API health first
    if not check_api_health():
        print("\n❌ API is not healthy. Please check the server.")
        exit(1)
    
    # Optimize resume
    result = optimize_resume_for_job(
        job_description=job_description,
        output_path="resume_software_engineer.docx",
        use_base64=True  # Use base64 for easier integration
    )
    
    # Example 2: Batch processing multiple jobs
    print("\n" + "="*70)
    print("Example 2: Batch Processing Multiple Jobs")
    print("="*70)
    
    job_postings = [
        {
            "company": "TechCorp",
            "role": "Backend Developer",
            "description": "Looking for Python developer with Django experience..."
        },
        {
            "company": "DataInc",
            "role": "Data Engineer",
            "description": "Seeking data engineer with AWS and ETL experience..."
        },
        {
            "company": "StartupXYZ",
            "role": "Full Stack Developer",
            "description": "Need full stack developer with React and Node.js..."
        }
    ]
    
    print(f"\nProcessing {len(job_postings)} job applications...")
    
    results = []
    for i, job in enumerate(job_postings, 1):
        print(f"\n--- Job {i}/{len(job_postings)}: {job['company']} - {job['role']} ---")
        
        output_file = f"resume_{job['company']}_{job['role'].replace(' ', '_')}.docx"
        
        result = optimize_resume_for_job(
            job_description=job['description'],
            output_path=output_file,
            use_base64=True
        )
        
        if result:
            results.append({
                "company": job['company'],
                "role": job['role'],
                "file": output_file,
                "match_score": result.get('match_score'),
                "keywords_added": result.get('keywords_added')
            })
    
    # Summary
    print("\n" + "="*70)
    print("Batch Processing Summary")
    print("="*70)
    
    for r in results:
        print(f"\n{r['company']} - {r['role']}")
        print(f"  File: {r['file']}")
        print(f"  Match Score: {r['match_score']}")
        print(f"  Keywords Added: {r['keywords_added']}")
    
    print("\n✅ All resumes generated successfully!")
    print("="*70 + "\n")
