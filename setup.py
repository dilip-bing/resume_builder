"""
Setup Script for Enhanced Resume Builder
Run this first to extract format metadata and content from your original resume.
"""

import sys
from pathlib import Path
from enhanced_format_system import FormatMetadata
from extract_to_json import ResumeToJSON

def setup_resume_builder(original_resume_path: str):
    """
    Complete setup for resume builder system.
    
    Steps:
    1. Create necessary folders
    2. Extract format metadata
    3. Extract content to JSON
    4. Verify setup
    """
    
    print("🚀 ENHANCED RESUME BUILDER - SETUP")
    print("=" * 60)
    
    # Check if original resume exists
    if not Path(original_resume_path).exists():
        print(f"❌ Error: Original resume not found at:")
        print(f"   {original_resume_path}")
        print("\n💡 Please update the path in setup.py")
        return False
    
    print(f"✅ Original resume found: {original_resume_path}\n")
    
    # Step 1: Create folders
    print("📁 STEP 1: Creating folders...")
    folders = ["templates", "output", "output/generated_resumes", "metadata"]
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created: {folder}/")
    
    # Step 2: Extract format metadata
    print("\n🎨 STEP 2: Extracting format metadata...")
    try:
        metadata_extractor = FormatMetadata(original_resume_path)
        metadata_path = metadata_extractor.save_metadata("metadata/format_metadata.json")
        print(f"   ✅ Format metadata saved")
    except Exception as e:
        print(f"   ❌ Error extracting metadata: {e}")
        return False
    
    # Step 3: Extract content
    print("\n📄 STEP 3: Extracting resume content...")
    try:
        content_extractor = ResumeToJSON(original_resume_path)
        content_path = content_extractor.save_to_json("templates/resume_content.json")
        print(f"   ✅ Content saved: {content_path}")
    except Exception as e:
        print(f"   ❌ Error extracting content: {e}")
        return False
    
    # Step 4: Verify
    print("\n✅ STEP 4: Verifying setup...")
    required_files = [
        "metadata/format_metadata.json",
        "templates/resume_content.json",
        "enhanced_app.py",
        "enhanced_format_system.py"
    ]
    
    all_good = True
    for file in required_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING")
            all_good = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_good:
        print("✅ SETUP COMPLETE!")
        print("\n📋 Next steps:")
        print("   1. Run the app: streamlit run enhanced_app.py")
        print("   2. Edit your resume in the web interface")
        print("   3. Click 'Generate Resume' to create output")
        print("\n📁 Generated resumes will be saved to:")
        print("   output/generated_resumes/")
        return True
    else:
        print("❌ SETUP INCOMPLETE - Some files are missing")
        return False


if __name__ == '__main__':
    # Update this path to your original resume
    ORIGINAL_RESUME = r"C:\Users\dilip\OneDrive\Desktop\ResumeBuilder\reference_docx\resume_optimized_final.docx"
    
    success = setup_resume_builder(ORIGINAL_RESUME)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
