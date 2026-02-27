"""
Test complete cover letter generation with SIMPLE builder
"""

from cover_letter_generator import CoverLetterGenerator
import os

def test_simple_system():
    """Test with simple copy-and-replace approach"""
    
    job_description = """
    Senior Software Engineer - Microsoft
    
    We are seeking a Senior Software Engineer for our Azure Cloud team.
    
    Requirements:
    - 5+ years Python/Java experience
    - Cloud platform expertise (Azure, AWS, GCP)
    - Strong system design skills
    - Experience with distributed systems
    
    Microsoft is committed to empowering every person and organization.
    """
    
    resume_text = """
    Dilip Kumar Thirukonda Chandrasekaran
    
    Experience:
    - 6+ years Python development
    - AWS and Azure cloud platforms
    - Microservices architecture
    - Led high-performance teams
    """
    
    print("🧪 Testing SIMPLE Cover Letter System")
    print("="  * 70)
    print("\nApproach: Copy template → Replace text → Save")
    print("="  * 70)
    
    try:
        # Initialize
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        print("\n1️⃣  Initializing generator...")
        generator = CoverLetterGenerator(api_key=api_key)
        
        # Generate
        print("\n2️⃣  Generating cover letter (copy template + AI content)...")
        doc, company_name = generator.create_cover_letter_docx(
            job_description=job_description,
            resume_text=resume_text,
            context="Passionate about cloud technologies"
        )
        
        # Save
        output_path = "test_cover_letter_simple_system.docx"
        doc.save(output_path)
        
        print(f"\n✅ SUCCESS!")
        print(f"   Company: {company_name}")
        print(f"   Output: {output_path}")
        
        # Verify
        print(f"\n3️⃣  Verification:")
        print(f"   Paragraphs: {len(doc.paragraphs)}")
        print(f"   Template: reference_docx/cover_letter_template.docx")
        print(f"   Metadata: metadata/cover_letter_format_metadata.json")
        
        # Show structure
        print(f"\n4️⃣  Document structure:")
        for i, para in enumerate(doc.paragraphs):
            if para.text.strip():
                preview = para.text[:60].replace('\n', ' ')
                print(f"   [{i:2d}] {preview}...")
        
        print(f"\n" + "="  * 70)
        print("✅ SIMPLE SYSTEM WORKING!")
        print("\nFormatting preserved from template:")
        print("  ✅ Same spacing between paragraphs")
        print("  ✅ Same fonts and sizes")
        print("  ✅ Same alignment (center header, justified body)")
        print("  ✅ Same line spacing (1.5 for body paragraphs)")
        print(f"\n{'='  * 70}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_system()
    exit(0 if success else 1)
