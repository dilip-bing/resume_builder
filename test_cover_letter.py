"""
Test Cover Letter Generator
Quick test to ensure cover letter generation works
"""

from cover_letter_generator import generate_cover_letter_file
import os

# Test job description
job_desc = """
Software Engineer - Python & Cloud
TechCorp Inc.

We're looking for a talented Software Engineer with expertise in Python, 
AWS, and Docker. You'll build scalable APIs and microservices.

Requirements:
- 3+ years Python experience
- AWS/Docker deployment
- REST API design
- Strong problem-solving skills
"""

print("🧪 Testing Cover Letter Generator...")
print("=" * 70)

# Set API key from environment (should be already set)
if not os.getenv("GEMINI_API_KEY"):
    print("⚠️  GEMINI_API_KEY not set in environment")
    print("    Loading from .streamlit/secrets.toml...")
    try:
        import toml
        secrets = toml.load(".streamlit/secrets.toml")
        os.environ["GEMINI_API_KEY"] = secrets["GEMINI_API_KEY"]
        print("✅ Loaded API key from secrets.toml")
    except Exception as e:
        print(f"❌ Failed to load API key: {e}")
        exit(1)

# Generate cover letter
try:
    print("\n📝 Generating cover letter (5 paragraphs, <60 words each)...")
    print("⏳ This may take 20-40 seconds...")
    
    filename, company = generate_cover_letter_file(
        job_description=job_desc,
        context="Passionate about cloud technologies and scalable systems",
        applicant_name="Dilip Kumar",
        applicant_email="dilip@example.com",
        applicant_phone="+1-234-567-8900"
    )
    
    print("\n" + "=" * 70)
    print(f"✅ SUCCESS!")
    print(f"✅ Cover Letter: {filename}")
    print(f"✅ Company: {company or 'Hiring Manager'}")
    print("=" * 70)
    print("\n💡 Open the file to review the AI-generated cover letter!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
