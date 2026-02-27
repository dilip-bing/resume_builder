"""
Get the last test resume
"""

import requests
import base64
from pathlib import Path

API_URL = "https://resume-optimizer-api-fvpd.onrender.com"
API_SECRET_KEY = "nFDqvbuNJb4dwsoL9E6HfyTaPC-O2oeHvK-y1RWDSGU"

# The job description from the test
job_description = "Software Engineer with Python, React, and AWS experience required."

print("Generating resume for job description:")
print(f"\n{job_description}\n")
print("⏳ Processing (10-60 seconds)...\n")

# Call API
response = requests.post(
    f"{API_URL}/api/v1/optimize",
    json={
        "job_description": job_description,
        "return_format": "base64"
    },
    headers={
        "X-API-Key": API_SECRET_KEY
    },
    timeout=120
)

result = response.json()

print(f"✅ Match Score: {result['match_score']}")
print(f"✅ Keywords Added: {result['keywords_added']}")

# Save resume
resume_data = base64.b64decode(result['resume_base64'])
output_path = Path("test_resume_output.docx")
output_path.write_bytes(resume_data)

print(f"\n✅ Resume saved to: {output_path.absolute()}")
print(f"   File size: {len(resume_data):,} bytes")
