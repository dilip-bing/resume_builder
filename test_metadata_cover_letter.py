"""
Test the complete metadata-based cover letter generation system
"""

from cover_letter_generator import CoverLetterGenerator
import os

def test_complete_cover_letter_system():
    """Test end-to-end cover letter generation with metadata-based formatting"""
    
    job_description = """
    Senior Software Engineer - Google
    
    We are seeking a talented Senior Software Engineer to join our Cloud Platform team.
    
    Requirements:
    - 5+ years of Python development experience
    - Strong experience with cloud platforms (GCP, AWS, Azure)
    - Excellent problem-solving and collaboration skills
    - Experience with microservices architecture
    
    Google is committed to building products that help billions of users worldwide.
    """
    
    resume_text = """
    Dilip Kumar Thirukonda Chandrasekaran
    Senior Software Engineer with 6+ years experience
    
    Skills:
    - Python, Django, Flask
    - AWS, Google Cloud Platform
    - Microservices, Docker, Kubernetes
    - RESTful APIs, SQL, NoSQL
    
    Experience:
    - Led development of high-traffic applications
    - Improved system performance by 40%
    - Architected cloud infrastructure migrations
    """
    
    context = "Passionate about cloud technologies and scalable systems"
    
    print("🧪 Testing Complete Cover Letter System with Metadata")
    print("=" * 70)
    
    try:
        # Initialize generator
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        print("\n1️⃣ Initializing generator...")
        generator = CoverLetterGenerator(api_key=api_key)
        
        # Generate cover letter
        print("\n2️⃣ Generating AI-powered cover letter with exact format preservation...")
        doc, company_name = generator.create_cover_letter_docx(
            job_description=job_description,
            resume_text=resume_text,
            context=context,
            applicant_name="Dilip Kumar Thirukonda Chandrasekaran",
            applicant_email="dthirukondac@binghamton.edu",
            applicant_phone="(607) 624-9390"
        )
        
        # Save output
        output_path = "test_cover_letter_complete.docx"
        doc.save(output_path)
        
        print(f"\n✅ Cover letter generated successfully!")
        print(f"   Company: {company_name}")
        print(f"   Output: {output_path}")
        
        # Verify paragraphs
        print(f"\n3️⃣ Document structure verification:")
        print(f"   Total paragraphs: {len(doc.paragraphs)}")
        print(f"   Non-empty paragraphs: {sum(1 for p in doc.paragraphs if p.text.strip())}")
        
        # Show header
        print(f"\n4️⃣ Header content:")
        for i in range(min(3, len(doc.paragraphs))):
            if doc.paragraphs[i].text.strip():
                print(f"   {i}: {doc.paragraphs[i].text[:80]}...")
        
        # Show body paragraphs
        print(f"\n5️⃣ Body paragraphs (AI-generated):")
        for i in range(9, min(14, len(doc.paragraphs))):
            text = doc.paragraphs[i].text.strip()
            if text and not text.startswith('['):
                word_count = len(text.split())
                print(f"   Para {i}: {word_count} words - {text[:100]}...")
        
        print(f"\n" + "=" * 70)
        print("✅ TEST PASSED!")
        print("\nNext steps:")
        print("1. Open test_cover_letter_complete.docx")
        print("2. Verify formatting matches reference_docx/cover_letter_template.docx")
        print("3. Check that all paragraphs have proper spacing and alignment")
        print("4. Confirm no placeholder text like '[your role]' remains")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_cover_letter_system()
    exit(0 if success else 1)
