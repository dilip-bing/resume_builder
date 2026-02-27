# Cover Letter System - Simple Approach (Like Resume)

## ✅ SIMPLE SYSTEM - Copy Template + Replace Text

### What It Does (3 Steps)

1. **Copy** template DOCX to output file
2. **Replace** text at specific paragraph indices (9-13 for AI content)
3. **Save** - formatting preserved automatically!

## File Structure

```
reference_docx/
  └── cover_letter_template.docx          ← Your template (NEVER modified)

metadata/
  └── cover_letter_format_metadata.json   ← Format data (extracted once)

templates/
  └── cover_letter_content.json           ← Content structure

simple_cover_letter_builder.py           ← Builder (copy + replace)
cover_letter_generator.py                ← AI generation
```

## How It Works

### Step 1: Extract Format Data (ONE TIME)

```bash
python extract_cover_letter_metadata.py
```

Creates `metadata/cover_letter_format_metadata.json` with:
- Paragraph formatting (alignment, spacing, line heights)
- Run formatting (fonts, sizes, bold/italic)
- For ALL 16 paragraphs in template

### Step 2: Template Structure (Fixed)

Your template `cover_letter_template.docx` has 16 paragraphs:

| Para | Content | Position |
|------|---------|----------|
| 0 | Your Name (bold) | Header |
| 1 | Phone & Email | Header |
| 2 | LinkedIn & Portfolio | Header |
| 3 | **[Date]** | ← AI replaces |
| 4 | **[Hiring Manager Name]** | ← AI replaces |
| 5 | **[Job Title]** | ← AI replaces |
| 6 | **[Company Name]** | ← AI replaces |
| 7 | **[Company Address]** | ← AI replaces |
| 8 | Dear Hiring Manager, | Salutation |
| 9 | **[Opening paragraph]** | ← **AI writes** |
| 10 | **[Skills paragraph]** | ← **AI writes** |
| 11 | **[Achievements paragraph]** | ← **AI writes** |
| 12 | **[Company knowledge paragraph]** | ← **AI writes** |
| 13 | **[Closing paragraph]** | ← **AI writes** |
| 14 | Sincerely, | Signature |
| 15 | Your Name | Signature |

**Fixed items (0-2, 8, 14-15):** Copied from template as-is  
**Variable items (3-7, 9-13):** Replaced with AI/extracted content

### Step 3: Generate Cover Letter

```python
from cover_letter_generator import CoverLetterGenerator

generator = CoverLetterGenerator(api_key="your-key")
doc, company = generator.create_cover_letter_docx(
    job_description="...",
    resume_text="..."
)
doc.save("output.docx")
```

**Behind the scenes:**
1. AI generates 5 paragraphs (opening, skills, achievements, company_knowledge, closing)
2. AI extracts company name
3. `SimpleCoverLetterBuilder`:
   - Copies template → output
   - Opens output
   - Replaces para 3: current date
   - Replaces para 4-7: company info
   - Replaces para 9-13: AI paragraphs
   - Saves
4. **Formatting preserved automatically** because we're modifying existing paragraphs!

## Code Flow

```python
# simple_cover_letter_builder.py

class SimpleCoverLetterBuilder:
    def replace_paragraph_text(self, doc, para_idx, new_text):
        """Replace text at paragraph index - EXACT copy of resume pattern"""
        para = doc.paragraphs[para_idx]
        
        # Clear existing runs
        for run in para.runs:
            run.text = ""
        
        # Apply format from metadata
        self.apply_paragraph_format_from_metadata(para, para_idx)
        
        # Add new text with format
        run = para.runs[0] if para.runs else para.add_run()
        run.text = new_text
        self.apply_run_format_from_metadata(run, para_idx, 0)
    
    def build_from_json(self, content_json, template_path, output_path):
        """Build cover letter - SIMPLE"""
        # 1. Copy template
        shutil.copy(template_path, output_path)
        
        # 2. Open
        doc = Document(output_path)
        
        # 3. Replace text at specific indices
        self.replace_paragraph_text(doc, 3, date)
        self.replace_paragraph_text(doc, 9, ai_opening)
        self.replace_paragraph_text(doc, 10, ai_skills)
        # ... etc
        
        # 4. Save
        doc.save(output_path)
```

## What Gets Preserved

Because we're modifying existing paragraphs (not creating new ones):

✅ **Paragraph Formatting:**
- Alignment (CENTER for header, JUSTIFY for body)
- Spacing before/after
- Line spacing (1.5 for body paragraphs)
- Indents

✅ **Run Formatting:**
- Font name
- Font size
- Bold/italic
- Color

✅ **Document Properties:**
- Margins
- Page size
- Section settings

## Templates

### `templates/cover_letter_content.json`

```json
{
  "header": {
    "name": "Dilip Kumar Thirukonda Chandrasekaran",
    "contact_line_1": "(607) 624-9390 | dthirukondac@binghamton.edu",
    "contact_line_2": "linkedin.com/dilipkumartc | dilip-bing.github.io/portfolio/"
  },
  "date": "[Date]",
  "recipient": {
    "hiring_manager": "[Hiring Manager Name]",
    "job_title": "[Job Title]",
    "company_name": "[Company Name]",
    "company_address": "[Company Address]"
  },
  "salutation": "Dear [Hiring Manager Name/Hiring Team],",
  "paragraphs": {
    "opening": { "value": "", "paragraph_index": 9 },
    "skills": { "value": "", "paragraph_index": 10 },
    "achievements": { "value": "", "paragraph_index": 11 },
    "company_knowledge": { "value": "", "paragraph_index": 12 },
    "closing": { "value": "", "paragraph_index": 13 }
  },
  "signature": {
    "closing_phrase": "Sincerely,",
    "name": "Dilip Kumar Thirukonda Chandrasekaran"
  }
}
```

## Testing

```bash
# Test simple builder directly
python simple_cover_letter_builder.py

# Test with AI generation
python test_simple_system.py

# Both create cover letters with EXACT template formatting!
```

## Comparison to Resume System

| Aspect | Resume System | Cover Letter System |
|--------|---------------|---------------------|
| Template | resume_optimized_final.docx | cover_letter_template.docx |
| Metadata | format_metadata.json | cover_letter_format_metadata.json |
| Builder | EnhancedFormatBuilder | SimpleCoverLetterBuilder |
| Approach | Copy + Replace | Copy + Replace |
| Format Preservation | ✅ Exact | ✅ Exact |

**Both use SAME pattern:**
1. Copy template
2. Replace text at indices
3. Format preserved automatically
4. Save

## Why This Works

- Template has **exact formatting** you want
- Copying preserves **all document structure**
- Replacing **text only** (not paragraphs) keeps formatting
- Metadata ensures **consistent application** of styles
- Simple = Reliable!

## Summary

**Before:** Complex system with manual DOCX creation ❌  
**After:** Simple copy-and-replace ✅

Just like your resume optimizer - **reliable, simple, exact formatting every time!**
