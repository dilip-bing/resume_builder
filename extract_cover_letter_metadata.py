"""
Extract format metadata from cover letter template
Creates metadata/cover_letter_format_metadata.json
"""

from enhanced_format_system import FormatMetadata
import json
from pathlib import Path

def extract_cover_letter_metadata():
    """Extract formatting metadata from cover letter template"""
    
    template_path = "reference_docx/cover_letter_template.docx"
    
    if not Path(template_path).exists():
        print(f"❌ Template not found: {template_path}")
        return
    
    print(f"📄 Extracting metadata from: {template_path}")
    
    # Extract metadata
    extractor = FormatMetadata(template_path)
    metadata = extractor.extract_complete_format_metadata()
    
    # Save to metadata folder
    output_dir = Path("metadata")
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / "cover_letter_format_metadata.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Metadata saved to: {output_path}")
    print(f"📊 Extracted {len(metadata['paragraph_formats'])} paragraphs")
    print(f"📊 Extracted {sum(len(runs) for runs in metadata['run_formats'].values())} runs")
    
    return output_path

if __name__ == "__main__":
    extract_cover_letter_metadata()
