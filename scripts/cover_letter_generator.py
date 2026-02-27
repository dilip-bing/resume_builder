"""
AI-Powered Cover Letter Generator
Generates tailored cover letters using Gemini AI

Template Structure (5 Paragraphs):
1. Opening: Express enthusiasm, mention job posting source, hook about fit
2. Skills (Body 1): Highlight relevant technical skills with metrics
3. Achievements (Body 2): Specific projects and measurable impact
4. Company Knowledge (Body 3): Research on company mission, values, culture fit
5. Closing: Reiterate enthusiasm, request discussion, thank them

Each paragraph: Maximum 60 words for conciseness
"""

import google.generativeai as genai
import os
import json
from datetime import datetime
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import re


class CoverLetterGenerator:
    """Generate professional cover letters using AI"""
    
    def __init__(self, api_key=None):
        """Initialize with Gemini API key"""
        if api_key:
            genai.configure(api_key=api_key)
        
        # Configure AI model (use same model as optimizer)
        self.model = genai.GenerativeModel('gemini-3-flash-preview')
        
    def _call_model(self, prompt, retries=3):
        """Call the model with automatic retry on 429 rate limit errors."""
        import time
        from google.api_core.exceptions import ResourceExhausted
        for attempt in range(retries):
            try:
                return self.model.generate_content(prompt)
            except ResourceExhausted as e:
                if attempt < retries - 1:
                    wait = 30 * (attempt + 1)
                    print(f"[RATE LIMIT] Quota exceeded. Waiting {wait}s before retry {attempt + 2}/{retries}...")
                    time.sleep(wait)
                else:
                    raise

    def extract_company_name(self, job_description):
        """Extract company name from job description (no API call — regex-based)."""
        import re
        patterns = [
            r'(?:at|@|with|join)\s+([A-Z][A-Za-z0-9&\s,\.]+?)(?:\s+(?:is|are|was|were|has|have)|[,\.\n]|$)',
            r'Company(?:\s+Name)?:\s*([A-Z][A-Za-z0-9&\s,\.]+?)(?:[,\.\n]|$)',
            r'About\s+([A-Z][A-Za-z0-9&\s]+?)(?:\s*[\n:])',
        ]
        for pattern in patterns:
            match = re.search(pattern, job_description[:800])
            if match:
                name = match.group(1).strip().rstrip('.,')
                if 2 < len(name) < 60:
                    return name
        return None

    def extract_job_details(self, job_description):
        """Extract job title and hiring manager name (no API call — regex-based)."""
        import re
        job_title = None
        hiring_mgr = None

        title_patterns = [
            r'(?:Job Title|Position|Role|Title):\s*(.+)',
            r'(?:hiring|looking for|seeking)\s+(?:a\s+)?([A-Z][A-Za-z\s]+?)(?:\s+to|\s+with|\s+who|[,\.\n])',
        ]
        for pattern in title_patterns:
            match = re.search(pattern, job_description[:600], re.IGNORECASE)
            if match:
                title = match.group(1).strip().rstrip('.,')
                if 2 < len(title) < 80:
                    job_title = title
                    break

        mgr_patterns = [
            r'(?:Hiring Manager|Contact|Recruiter|Report to):\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'(?:contact|reach out to)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
        ]
        for pattern in mgr_patterns:
            match = re.search(pattern, job_description[:600], re.IGNORECASE)
            if match:
                hiring_mgr = match.group(1).strip()
                break

        return job_title, hiring_mgr

    def generate_cover_letter(self, job_description, resume_text="", context=""):
        """
        Generate a complete cover letter in a SINGLE API call.

        Returns:
            dict: {
                'company_name': str,
                'job_title': str,
                'hiring_manager': str,
                'paragraphs': dict,
                'full_text': str
            }
        """
        prompt = f"""
You are writing a professional cover letter. Complete ALL tasks below in ONE response.

JOB DESCRIPTION:
{job_description[:1200]}

RESUME / BACKGROUND:
{resume_text[:800]}

CONTEXT: {context}

Return your response using EXACTLY these labeled sections (keep labels as-is):

COMPANY_NAME: [company name from job description, or Unknown]
JOB_TITLE: [job title from job description, or Unknown]
HIRING_MANAGER: [hiring manager name if mentioned, or Unknown]

PARAGRAPH_OPENING:
[Opening paragraph — max 55 words. Express genuine enthusiasm for the role. Mention relevant experience.]

PARAGRAPH_SKILLS:
[Skills paragraph — max 55 words. Highlight relevant technical skills with quantifiable metrics.]

PARAGRAPH_ACHIEVEMENTS:
[Achievements paragraph — max 55 words. Highlight specific projects and measurable impact.]

PARAGRAPH_COMPANY_KNOWLEDGE:
[Company knowledge paragraph — max 55 words. Show understanding of the company mission/values and your alignment.]

PARAGRAPH_CLOSING:
[Closing paragraph — max 55 words. Reinforce enthusiasm, invite discussion, thank them.]

Rules: Each paragraph must be complete and polished. No placeholders. Professional tone. Max 55 words each.
"""
        response = self._call_model(prompt)
        text = response.text.strip()

        # Parse metadata lines
        company_name = None
        job_title = None
        hiring_mgr = None
        for line in text.split('\n'):
            stripped = line.strip()
            if stripped.startswith('COMPANY_NAME:'):
                val = stripped.replace('COMPANY_NAME:', '').strip().strip('"\'')
                if val and 'unknown' not in val.lower():
                    company_name = val
            elif stripped.startswith('JOB_TITLE:'):
                val = stripped.replace('JOB_TITLE:', '').strip().strip('"\'')
                if val and 'unknown' not in val.lower():
                    job_title = val
            elif stripped.startswith('HIRING_MANAGER:'):
                val = stripped.replace('HIRING_MANAGER:', '').strip().strip('"\'')
                if val and 'unknown' not in val.lower():
                    hiring_mgr = val

        # Fallback to regex extraction if AI didn't return them
        if not company_name:
            company_name = self.extract_company_name(job_description)
        if not job_title:
            job_title, _ = self.extract_job_details(job_description)

        # Parse paragraphs
        para_sections = ['OPENING', 'SKILLS', 'ACHIEVEMENTS', 'COMPANY_KNOWLEDGE', 'CLOSING']
        para_map = {s: s.lower() for s in para_sections}
        paragraphs = {}

        for i, section in enumerate(para_sections):
            marker = f'PARAGRAPH_{section}:'
            if marker not in text:
                continue
            start = text.index(marker) + len(marker)
            end = len(text)
            for j in range(i + 1, len(para_sections)):
                next_marker = f'PARAGRAPH_{para_sections[j]}:'
                if next_marker in text:
                    end = min(end, text.index(next_marker))
            para_text = text[start:end].strip()
            words = para_text.split()
            if len(words) > 55:
                para_text = ' '.join(words[:55]) + '...'
            paragraphs[para_map[section]] = para_text

        return {
            'company_name': company_name,
            'job_title': job_title,
            'hiring_manager': hiring_mgr,
            'paragraphs': paragraphs,
            'full_text': '\n\n'.join(paragraphs.values())
        }
    
    def create_cover_letter_content_json(self, job_description, resume_text="", context="", 
                                          applicant_name="Dilip Kumar", applicant_email="", 
                                          applicant_phone=""):
        """
        Create a structured JSON content for cover letter (template-based approach)
        
        Returns:
            tuple: (content_dict, company_name)
        """
        # Generate content
        letter_data = self.generate_cover_letter(job_description, resume_text, context)
        company_name = letter_data['company_name']
        paragraphs = letter_data['paragraphs']
        
        # Build content JSON structure
        content = {
            "header": {
                "applicant_name": applicant_name,
                "email": applicant_email,
                "phone": applicant_phone,
                "date": "[Current Date]"  # Will be replaced with actual date
            },
            "recipient": {
                "hiring_manager": "Hiring Manager",
                "company_name": company_name or "[Company Name]"
            },
            "salutation": "Dear Hiring Manager,",
            "paragraphs": {
                "opening": {"value": paragraphs.get('opening', '')},
                "skills": {"value": paragraphs.get('skills', '')},
                "achievements": {"value": paragraphs.get('achievements', '')},
                "company_knowledge": {"value": paragraphs.get('company_knowledge', '')},
                "closing": {"value": paragraphs.get('closing', '')}
            },
            "signature": {
                "closing_phrase": "Sincerely,",
                "name": applicant_name
            }
        }
        
        return content, company_name
    
    def create_cover_letter_docx(self, job_description, resume_text="", context="", 
                                  applicant_name="Dilip Kumar Thirukonda Chandrasekaran", 
                                  applicant_email="", applicant_phone=""):
        """
        Create formatted cover letter - SIMPLE: Copy template + replace text
        
        Returns:
            tuple: (Document object, company_name)
        """
        from simple_cover_letter_builder import build_cover_letter_simple
        from pathlib import Path
        import tempfile
        
        # Single API call — extracts company/job details AND generates all paragraphs
        result = self.generate_cover_letter(job_description, resume_text, context)
        paragraphs = result['paragraphs']
        company_name = result.get('company_name')
        job_title = result.get('job_title')
        hiring_mgr = result.get('hiring_manager')
        
        # Create temp file
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
            temp_output = tmp.name
        
        # Build using simple builder (copy template + replace text)
        build_cover_letter_simple(
            paragraphs, 
            company_name=company_name,
            job_title=job_title,
            hiring_manager=hiring_mgr,
            output_path=temp_output
        )
        
        # Load and return
        doc = Document(temp_output)
        
        return doc, company_name


def generate_cover_letter_file(job_description, resume_text="", context="",
                                output_filename=None, applicant_name="Dilip Kumar",
                                applicant_email="", applicant_phone="", api_key=None):
    """
    Convenience function to generate and save cover letter
    
    Args:
        api_key: Gemini API key (if not provided, will try to load from environment)
    
    Returns:
        tuple: (output_filename, company_name)
    """
    # Get API key from environment if not provided
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            # Try loading from secrets.toml
            try:
                import toml
                secrets_path = ".streamlit/secrets.toml"
                if os.path.exists(secrets_path):
                    secrets_data = toml.load(secrets_path)
                    api_key = secrets_data.get("GEMINI_API_KEY")
            except:
                pass
    
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found. Set environment variable or pass as parameter.")
    
    generator = CoverLetterGenerator(api_key=api_key)
    doc, company_name = generator.create_cover_letter_docx(
        job_description, resume_text, context,
        applicant_name, applicant_email, applicant_phone
    )
    
    # Generate filename if not provided
    if not output_filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"cover_letter_dilip_kumar_{timestamp}.docx"
    
    doc.save(output_filename)
    return output_filename, company_name


# Example usage
if __name__ == "__main__":
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
    
    filename, company = generate_cover_letter_file(
        job_description=job_desc,
        context="I'm passionate about cloud technologies and have 5 years of experience",
        applicant_email="dilip@example.com",
        applicant_phone="+1-234-567-8900"
    )
    
    print(f"[OK] Cover letter created: {filename}")
    print(f"[OK] Company: {company or 'Hiring Manager'}")
