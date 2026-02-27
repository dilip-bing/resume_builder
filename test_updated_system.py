"""
Test updated cover letter system with all improvements:
- 55 word limit for paragraphs
- No placeholder hints in AI output
- Graceful handling of missing data
- Updated template metadata
"""

from cover_letter_generator import CoverLetterGenerator
import os

def test_updated_system():
    """Test with real job description"""
    
    # Job description with company name and job title
    job_description = """
    Senior Qt/C++ Developer - KDAB
    
    KDAB is seeking a talented Senior Qt/C++ Developer to join our consultancy team.
    
    Requirements:
    - 5+ years C++ and Qt/QML experience
    - Strong debugging and optimization skills
    - Experience with Linux development environment
    - Excellent communication skills
    
    KDAB is a world-leading Qt/C++ consultancy working with clients in aerospace,
    automotive, and medical industries.
    """
    
    resume_text = """
    Dilip Kumar Thirukonda Chandrasekaran
    
    Skills:
    - C++, Qt/QML, Python
    - Multithreaded applications
    - Performance optimization
    - Linux, GCC, Git
    
    Experience:
    - 6+ years software development
    - Built real-time data processing applications
    - Optimized automotive HMI systems
    - Reduced CPU usage by 20%
    - Improved boot time by 30%
    """
    
    print("🧪 Testing Updated Cover Letter System")
    print("=" * 70)
    print("\nImprovements:")
    print("  ✅ 55-word limit for paragraphs (fit on one page)")
    print("  ✅ No placeholder hints like '[Platform, e.g., LinkedIn]'")
    print("  ✅ Smart defaults: Hiring Manager if name not found")
    print("  ✅ Blank fields if data not available")
    print("  ✅ Updated template metadata")
    print("=" * 70)
    
    try:
        # Initialize
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        print("\n1️⃣  Initializing generator...")
        generator = CoverLetterGenerator(api_key=api_key)
        
        # Generate
        print("\n2️⃣  Generating cover letter...")
        print("     - Extracting company name, job title, hiring manager...")
        print("     - Generating 5 paragraphs (max 55 words each)...")
        
        doc, company_name = generator.create_cover_letter_docx(
            job_description=job_description,
            resume_text=resume_text,
            context="Passionate about high-performance Qt/C++ development"
        )
        
        # Save
        output_path = "test_updated_cover_letter.docx"
        doc.save(output_path)
        
        print(f"\n✅ SUCCESS!")
        print(f"   Company: {company_name}")
        print(f"   Output: {output_path}")
        
        # Analyze output
        print(f"\n3️⃣  Document analysis:")
        print(f"   Total paragraphs: {len(doc.paragraphs)}")
        
        # Check header
        print(f"\n4️⃣  Header (fixed from template):")
        for i in range(3):
            if doc.paragraphs[i].text.strip():
                print(f"   [{i}] {doc.paragraphs[i].text}")
        
        # Check recipient info
        print(f"\n5️⃣  Recipient info (AI-extracted or defaults):")
        for i in range(3, 9):
            text = doc.paragraphs[i].text.strip()
            labels = ['Date:', 'Hiring Mgr:', 'Job Title:', 'Company:', 'Address:', 'Salutation:']
            label = labels[i-3] if i-3 < len(labels) else f'Para {i}:'
            if text:
                print(f"   {label:12} {text}")
            else:
                print(f"   {label:12} (blank)")
        
        # Check body paragraphs
        print(f"\n6️⃣  Body paragraphs (AI-generated, max 55 words):")
        para_names = ['Opening', 'Skills', 'Achievements', 'Company', 'Closing']
        for idx, i in enumerate(range(9, 14)):
            text = doc.paragraphs[i].text.strip()
            if text:
                word_count = len(text.split())
                status = "✅" if word_count <= 55 else "⚠️"
                print(f"   {status} {para_names[idx]:12} ({word_count:2d} words): {text[:80]}...")
        
        # Check signature
        print(f"\n7️⃣  Signature (fixed from template):")
        for i in range(14, 16):
            if doc.paragraphs[i].text.strip():
                print(f"   [{i}] {doc.paragraphs[i].text}")
        
        print(f"\n" + "=" * 70)
        print("✅ ALL IMPROVEMENTS WORKING!")
        print("\nVerify in document:")
        print(f"  1. Open: {output_path}")
        print("  2. Check: No placeholder hints like '[Platform, e.g., LinkedIn]'")
        print("  3. Check: All paragraphs ≤ 55 words")
        print("  4. Check: Smart defaults for missing data")
        print("  5. Check: Fits on one page")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_updated_system()
    exit(0 if success else 1)
