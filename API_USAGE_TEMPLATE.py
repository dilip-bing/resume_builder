"""
═══════════════════════════════════════════════════════════════════════════════
RESUME OPTIMIZER API - QUICK REFERENCE & USAGE TEMPLATE
═══════════════════════════════════════════════════════════════════════════════

Copy-paste this into any script or automation tool.
Works with: Python, Node.js, cURL, Postman, Make.com, Zapier, etc.

═══════════════════════════════════════════════════════════════════════════════
"""

# ═══════════════════════════════════════════════════════════════════════════
# 📋 CONFIGURATION (Copy these to your script)
# ═══════════════════════════════════════════════════════════════════════════

API_URL = "https://resume-optimizer-api-fvpd.onrender.com"
API_SECRET_KEY = "nFDqvbuNJb4dwsoL9E6HfyTaPC-O2oeHvK-y1RWDSGU"

# ═══════════════════════════════════════════════════════════════════════════
# 🐍 PYTHON USAGE (Most Common)
# ═══════════════════════════════════════════════════════════════════════════

import requests
import base64
from pathlib import Path

def optimize_resume(job_description, output_filename="optimized_resume.docx"):
    """
    Generate optimized resume for a job description.
    
    Args:
        job_description (str): Full job posting text
        output_filename (str): Where to save the resume
        
    Returns:
        dict: Result with match_score, keywords_added, etc.
    """
    # Make API request
    response = requests.post(
        f"{API_URL}/api/v1/optimize",
        json={
            "job_description": job_description,
            "return_format": "base64"  # or "file" for download URL
        },
        headers={
            "X-API-Key": API_SECRET_KEY  # ⚠️ REQUIRED - Authentication
        },
        timeout=120  # ⚠️ IMPORTANT - Allow time for AI processing
    )
    
    # Handle errors
    if response.status_code == 401:
        raise Exception("❌ Missing API key - add X-API-Key header")
    elif response.status_code == 403:
        raise Exception("❌ Invalid API key - check API_SECRET_KEY")
    elif response.status_code != 200:
        raise Exception(f"❌ API error: {response.status_code} - {response.text}")
    
    # Get result
    result = response.json()
    
    # Save resume (if base64 format)
    if "resume_base64" in result:
        resume_bytes = base64.b64decode(result["resume_base64"])
        Path(output_filename).write_bytes(resume_bytes)
        print(f"✅ Saved: {output_filename}")
    
    # Print metrics
    print(f"✅ Match Score: {result['match_score']}")
    print(f"✅ Keywords Added: {result['keywords_added']}")
    
    return result

def generate_cover_letter(job_description, resume_text="", context="", 
                          applicant_name="Dilip Kumar", applicant_email="", 
                          applicant_phone="", output_filename="cover_letter.docx"):
    """
    Generate AI-powered cover letter for a job description.
    
    Args:
        job_description (str): Full job posting text
        resume_text (str): Optimized resume content (optional, for context)
        context (str): Additional context like career goals (optional)
        applicant_name (str): Your full name
        applicant_email (str): Your email
        applicant_phone (str): Your phone
        output_filename (str): Where to save the cover letter
        
    Returns:
        dict: Result with company_name, filename, etc.
    """
    # Make API request
    response = requests.post(
        f"{API_URL}/api/v1/generate-cover-letter",
        json={
            "job_description": job_description,
            "resume_text": resume_text,
            "context": context,
            "applicant_name": applicant_name,
            "applicant_email": applicant_email,
            "applicant_phone": applicant_phone,
            "return_format": "base64"
        },
        headers={
            "X-API-Key": API_SECRET_KEY  # ⚠️ REQUIRED - Authentication
        },
        timeout=120  # ⚠️ IMPORTANT - Allow time for AI processing
    )
    
    # Handle errors
    if response.status_code == 401:
        raise Exception("❌ Missing API key - add X-API-Key header")
    elif response.status_code == 403:
        raise Exception("❌ Invalid API key - check API_SECRET_KEY")
    elif response.status_code != 200:
        raise Exception(f"❌ API error: {response.status_code} - {response.text}")
    
    # Get result
    result = response.json()
    
    # Save cover letter (if base64 format)
    if "cover_letter_base64" in result:
        cover_letter_bytes = base64.b64decode(result["cover_letter_base64"])
        Path(output_filename).write_bytes(cover_letter_bytes)
        print(f"✅ Saved: {output_filename}")
    
    # Print info
    print(f"✅ Company: {result.get('company_name', 'Hiring Manager')}")
    print(f"✅ Filename: {result['filename']}")
    
    return result

# ═══════════════════════════════════════════════════════════════════════════
# 📝 USAGE EXAMPLES
# ═══════════════════════════════════════════════════════════════════════════

# Example 1: Single Job - Resume + Cover Letter
job = """
Senior Python Developer
Requirements:
- 5+ years Python experience
- Django/Flask frameworks
- AWS/Docker deployment
- REST API design
"""

# Generate resume
resume_result = optimize_resume(job, "resume_python_dev.docx")

# Generate cover letter
cover_letter_result = generate_cover_letter(
    job_description=job,
    resume_text="Python developer with 5 years experience in Django, Flask, AWS",
    context="Passionate about building scalable web applications",
    applicant_name="Dilip Kumar",
    applicant_email="dilip@example.com",
    applicant_phone="+1-234-567-8900",
    output_filename="cover_letter_python_dev.docx"
)


# Example 2: Multiple Jobs (Batch Processing - Resume + Cover Letter)
jobs = [
    {"company": "Google", "role": "SWE", "description": "..."},
    {"company": "Meta", "role": "Backend", "description": "..."},
    {"company": "Amazon", "role": "Cloud", "description": "..."},
]

for job in jobs:
    # Generate resume
    resume_file = f"resume_{job['company'].lower()}.docx"
    resume_result = optimize_resume(job["description"], resume_file)
    
    # Generate cover letter    cover_letter_file = f"cover_letter_{job['company'].lower()}.docx"
    cover_letter_result = generate_cover_letter(
        job_description=job["description"],
        applicant_name="Dilip Kumar",
        output_filename=cover_letter_file
    )
    
    print(f"✅ {job['company']} - Resume + Cover Letter Done\n")


# Example 3: First Request (Handle Cold Start)
import time

print("⏳ First request may take 30-60 seconds (API waking up)...")
try:
    result = optimize_resume(job, "resume.docx")
except requests.exceptions.Timeout:
    print("⚠️ Timeout - trying again in 10 seconds...")
    time.sleep(10)
    result = optimize_resume(job, "resume.docx")


# ═══════════════════════════════════════════════════════════════════════════
# 🌐 cURL (Terminal/Command Line)
# ═══════════════════════════════════════════════════════════════════════════

"""
# Health Check (test if API is alive)
curl https://resume-optimizer-api-fvpd.onrender.com/health

# Optimize Resume
curl -X POST https://resume-optimizer-api-fvpd.onrender.com/api/v1/optimize \
  -H "Content-Type: application/json" \
  -H "X-API-Key: nFDqvbuNJb4dwsoL9E6HfyTaPC-O2oeHvK-y1RWDSGU" \
  -d '{
    "job_description": "Software Engineer with Python and React",
    "return_format": "base64"
  }'

# Generate Cover Letter
curl -X POST https://resume-optimizer-api-fvpd.onrender.com/api/v1/generate-cover-letter \
  -H "Content-Type: application/json" \
  -H "X-API-Key: nFDqvbuNJb4dwsoL9E6HfyTaPC-O2oeHvK-y1RWDSGU" \
  -d '{
    "job_description": "Software Engineer with Python and React",
    "applicant_name": "Dilip Kumar",
    "applicant_email": "dilip@example.com",
    "applicant_phone": "+1-234-567-8900",
    "return_format": "base64"
  }'
"""

# ═══════════════════════════════════════════════════════════════════════════
# 🟢 Node.js (JavaScript)
# ═══════════════════════════════════════════════════════════════════════════

"""
const axios = require('axios');
const fs = require('fs');

async function optimizeResume(jobDescription, outputFile) {
    const response = await axios.post(
        'https://resume-optimizer-api-fvpd.onrender.com/api/v1/optimize',
        {
            job_description: jobDescription,
            return_format: 'base64'
        },
        {
            headers: {
                'X-API-Key': 'nFDqvbuNJb4dwsoL9E6HfyTaPC-O2oeHvK-y1RWDSGU'
            },
            timeout: 120000  // 120 seconds
        }
    );
    
    const resumeBuffer = Buffer.from(response.data.resume_base64, 'base64');
    fs.writeFileSync(outputFile, resumeBuffer);
    
    console.log(`✅ Match Score: ${response.data.match_score}`);
    console.log(`✅ Keywords Added: ${response.data.keywords_added}`);
}

// Usage
const job = "Full Stack Developer with React and Node.js";
optimizeResume(job, 'resume.docx');
"""

# ═══════════════════════════════════════════════════════════════════════════
# 🔧 POSTMAN / API Tools
# ═══════════════════════════════════════════════════════════════════════════

"""
Method: POST
URL: https://resume-optimizer-api-fvpd.onrender.com/api/v1/optimize

Headers:
  Content-Type: application/json
  X-API-Key: nFDqvbuNJb4dwsoL9E6HfyTaPC-O2oeHvK-y1RWDSGU

Body (JSON):
{
  "job_description": "Paste full job description here...",
  "return_format": "base64"
}
"""

# ═══════════════════════════════════════════════════════════════════════════
# ⚙️ Make.com / Zapier / n8n (No-Code Automation)
# ═══════════════════════════════════════════════════════════════════════════

"""
WEBHOOK/HTTP REQUEST CONFIGURATION:

URL: https://resume-optimizer-api-fvpd.onrender.com/api/v1/optimize
Method: POST
Headers:
  - Key: Content-Type, Value: application/json
  - Key: X-API-Key, Value: nFDqvbuNJb4dwsoL9E6HfyTaPC-O2oeHvK-y1RWDSGU

Body:
{
  "job_description": "{{JobDescription}}",  # From previous step
  "return_format": "base64"
}

Response Mapping:
- Match Score: {{data.match_score}}
- Keywords: {{data.keywords_added}}
- Resume (base64): {{data.resume_base64}}

To save file: Decode base64 → Save to Google Drive/Dropbox
"""

# ═══════════════════════════════════════════════════════════════════════════
# ⚠️ IMPORTANT NOTES
# ═══════════════════════════════════════════════════════════════════════════

"""
1. AUTHENTICATION (REQUIRED):
   - Always include header: X-API-Key: nFDqvbuNJb4dwsoL9E6HfyTaPC-O2oeHvK-y1RWDSGU
   - Without it: 401 Unauthorized
   - Wrong key: 403 Forbidden

2. TIMEOUTS:
   - Set timeout to 120 seconds minimum
   - First request (cold start): 30-60 seconds
   - Subsequent requests: 10-30 seconds
   - Processing time depends on job description length

3. COLD START (Free Tier Limitation):
   - API sleeps after 15 minutes of inactivity
   - First request wakes it up (30-60 seconds)
   - During business hours → faster (likely already awake)
   - Weekends/late night → might be cold

4. RETURN FORMATS:
   - "base64": Resume embedded in JSON response (recommended for automation)
   - "file": Returns download URL (good for manual downloads)

5. RATE LIMITS:
   - No hard limits currently
   - Be respectful: Don't spam requests
   - Batch processing: Add 5-10 second delays between jobs

6. ERROR HANDLING:
   Status 401: Missing API key → Add X-API-Key header
   Status 403: Invalid API key → Check API_SECRET_KEY value
   Status 422: Invalid request → Check job_description format
   Status 500: Server error → Try again in 30 seconds
   Timeout: API cold or job too long → Retry once

7. BEST PRACTICES:
   ✅ Always check health endpoint first (GET /health)
   ✅ Store API_SECRET_KEY in environment variables (not hardcoded)
   ✅ Add error handling and retries
   ✅ Log match scores for tracking
   ✅ Save resumes with descriptive names (company_role_date.docx)

8. FREE TIER LIMITS:
   - 750 hours/month (always-on for 31 days)
   - Unlimited API calls within those hours
   - 512 MB RAM (enough for resume generation)
   - Your current usage: API will never run out

9. DEBUGGING:
   - Test endpoint: GET https://resume-optimizer-api-fvpd.onrender.com/health
   - API docs: https://resume-optimizer-api-fvpd.onrender.com/docs
   - Check Render dashboard for logs if errors occur

10. SECURITY:
    ⚠️ NEVER commit API_SECRET_KEY to public GitHub repos
    ✅ Use .env files or environment variables
    ✅ Rotate key if accidentally exposed (regenerate in Render)
"""

# ═══════════════════════════════════════════════════════════════════════════
# 🎯 COMMON INTEGRATION SCENARIOS
# ═══════════════════════════════════════════════════════════════════════════

# Scenario 1: LinkedIn Job Scraper + Resume Generator
"""
1. Scrape LinkedIn jobs (using Selenium/Beautiful Soup)
2. Extract job description
3. Call API to generate tailored resume
4. Save resume with job ID in filename
5. Auto-apply or save for manual review
"""

# Scenario 2: Email Automation
"""
1. Receive job posting via email
2. Parse job description from email body
3. Generate resume via API
4. Attach resume to reply email
5. Send to recruiter
"""

# Scenario 3: Job Board Integration
"""
1. Monitor Indeed/Glassdoor RSS feeds
2. For each new job:
   - Extract description
   - Generate resume
   - Auto-fill application form
   - Upload generated resume
"""

# Scenario 4: Airtable/Notion Database
"""
1. Maintain job tracker in Airtable
2. When status = "Ready to Apply":
   - Fetch job description from column
   - Generate resume via API
   - Upload to Airtable attachment field
   - Mark status = "Applied"
"""

# ═══════════════════════════════════════════════════════════════════════════
# 📊 RESPONSE FORMAT (What You Get Back)
# ═══════════════════════════════════════════════════════════════════════════

"""
{
  "success": true,
  "match_score": "95-98%",           # How well resume matches job
  "keywords_added": 23,              # Technical terms added
  "filename": "resume_optimized_20260209_180929.docx",
  "resume_base64": "UEsDBBQABg..."   # Full resume (if return_format=base64)
  # OR
  "download_url": "/api/v1/download/resume_optimized_20260209_180929.docx"
}

Decode base64:
  import base64
  resume_bytes = base64.b64decode(result["resume_base64"])
  with open("resume.docx", "wb") as f:
      f.write(resume_bytes)
"""

# ═══════════════════════════════════════════════════════════════════════════
# 🚀 QUICK START (Copy-Paste Ready)
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import requests
    import base64
    
    # Your job description (paste here)
    JOB = """
    Paste the full job description here.
    Include requirements, responsibilities, skills, etc.
    """
    
    # Generate resume
    response = requests.post(
        "https://resume-optimizer-api-fvpd.onrender.com/api/v1/optimize",
        json={"job_description": JOB, "return_format": "base64"},
        headers={"X-API-Key": "nFDqvbuNJb4dwsoL9E6HfyTaPC-O2oeHvK-y1RWDSGU"},
        timeout=120
    )
    
    # Save resume
    result = response.json()
    resume_data = base64.b64decode(result["resume_base64"])
    
    with open("my_resume.docx", "wb") as f:
        f.write(resume_data)
    
    print(f"✅ Match: {result['match_score']}")
    print(f"✅ Keywords: {result['keywords_added']}")
    print(f"✅ Saved: my_resume.docx")

# ═══════════════════════════════════════════════════════════════════════════
# 📚 ADDITIONAL RESOURCES
# ═══════════════════════════════════════════════════════════════════════════

"""
Documentation:
  - Full API Docs: API_README.md
  - Authentication Guide: API_AUTHENTICATION.md
  - Deployment Guide: DEPLOY_RENDER.md
  - Remote Access: REMOTE_ACCESS_GUIDE.md

Live Tools:
  - API Dashboard: https://resume-optimizer-api-fvpd.onrender.com/docs
  - Health Check: https://resume-optimizer-api-fvpd.onrender.com/health
  - Render Logs: https://dashboard.render.com (your account)

Example Scripts:
  - automate_applications.py - Batch job processing
  - client_remote_example.py - Remote API examples
  - test_remote_api.py - Quick API test

Support:
  - Check Render dashboard logs for errors
  - Test with /health endpoint first
  - Verify API_SECRET_KEY matches Render environment variable
"""

# ═══════════════════════════════════════════════════════════════════════════
# END OF TEMPLATE
# ═══════════════════════════════════════════════════════════════════════════
