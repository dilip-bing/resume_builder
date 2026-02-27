"""
Quick test script to verify cover letter template-based generation
"""

from cover_letter_generator import CoverLetterGenerator
from pathlib import Path
import os

def test_cover_letter_template_system():
    """Test the new template-based cover letter generation"""
    
    # Test data
    job_description = """
    Senior Software Engineer - TechCorp Inc.
    
    We are looking for a talented Senior Software Engineer to join our team.
    
    Requirements:
    - 5+ years Python development experience
    - Strong knowledge of web frameworks (Django, Flask)
    - Experience with cloud platforms (AWS, Azure)
    - Excellent problem-solving skills
    
    TechCorp Inc. is a leading AI company focused on innovative solutions.
    """
    
    resume_text = """
    Dilip Kumar
    Senior Software Engineer
    
    Experience:
    - 6 years of Python development
    - Extensive work with Django and Flask
    - AWS certified solutions architect
    - Led multiple high-impact projects
    """
    
    # Get API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment")
    
    print("🧪 Testing Cover Letter Template System...")
    print("=" * 60)
    
    try:
        # Initialize generator
        print("\n1️⃣ Initializing generator...")
        generator = CoverLetterGenerator(api_key=api_key)
        
        # Generate cover letter using new template system
        print("\n2️⃣ Generating cover letter with template system...")
        doc, company_name = generator.create_cover_letter_docx(
            job_description=job_description,
            resume_text=resume_text,
            applicant_name="Dilip Kumar",
            applicant_email="dilip@example.com",
            applicant_phone="+1-234-567-8900"
        )
        
        print(f"   ✅ Cover letter generated for: {company_name}")
        
        # Save test output
        output_path = "test_cover_letter_template_output.docx"
        doc.save(output_path)
        
        print(f"\n3️⃣ Document saved: {output_path}")
        print(f"   ✅ File size: {Path(output_path).stat().st_size} bytes")
        
        # Verify template file exists
        template_path = Path("reference_docx/cover_letter_template.docx")
        if template_path.exists():
            print(f"\n4️⃣ Template verification:")
            print(f"   ✅ Template found: {template_path}")
            print(f"   ✅ Template size: {template_path.stat().st_size} bytes")
        else:
            print(f"\n4️⃣ ⚠️ Template not found at: {template_path}")
        
        print("\n" + "=" * 60)
        print("✅ TEST PASSED: Cover letter template system working!")
        print("\nNext steps:")
        print("1. Open test_cover_letter_template_output.docx to verify formatting")
        print("2. Check if formatting is preserved correctly")
        print("3. Compare with reference_docx/cover_letter_template.docx")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_cover_letter_template_system()
    exit(0 if success else 1)
