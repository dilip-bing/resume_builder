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
        self.model = genai.GenerativeModel('models/gemini-2.5-pro')
        
    def extract_company_name(self, job_description):
        """Extract company name from job description using AI"""
        prompt = f"""
        Extract ONLY the company name from this job description.
        If no company name is found, return "Unknown".
        Return only the company name, nothing else.
        
        Job Description:
        {job_description[:500]}
        """
        
        try:
            response = self.model.generate_content(prompt)
            company = response.text.strip()
            
            # Clean up common AI responses
            if any(word in company.lower() for word in ['unknown', 'not found', 'not mentioned', 'unclear']):
                return None
            
            # Remove quotes and extra spaces
            company = company.strip('"').strip("'").strip()
            
            return company if company else None
        except:
            return None
    
    def extract_job_details(self, job_description):
        """Extract job title and hiring manager name if available"""
        prompt = f"""
        Extract from this job description:
        1. Job title (the position being hired for)
        2. Hiring manager name (if mentioned)
        
        Return in this exact format:
        Job Title: [title or "Unknown"]
        Hiring Manager: [name or "Unknown"]
        
        Job Description:
        {job_description[:600]}
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            job_title = None
            hiring_mgr = None
            
            for line in text.split('\n'):
                if line.startswith('Job Title:'):
                    title = line.replace('Job Title:', '').strip()
                    if title and 'unknown' not in title.lower():
                        job_title = title
                elif line.startswith('Hiring Manager:'):
                    mgr = line.replace('Hiring Manager:', '').strip()
                    if mgr and 'unknown' not in mgr.lower():
                        hiring_mgr = mgr
            
            return job_title, hiring_mgr
        except:
            return None, None
    
    def generate_paragraph(self, paragraph_type, job_description, resume_text, context, company_name=None):
        """Generate a single paragraph (max 60 words)"""
        
        prompts = {
            "opening": f"""
            Write a polished opening paragraph for a professional cover letter (MAX 55 WORDS):
            - Express genuine enthusiasm for the specific position at {company_name or "the company"}
            - Mention your relevant experience that makes you an excellent fit
            - Reference the specific job title if clear from the description
            - Skip any mention of where you found the job if not obvious
            
            Job Description: {job_description[:400]}
            Company Name: {company_name or "the company"}
            
            Write a complete, polished paragraph. Maximum 55 words. No placeholders or examples. Professional and enthusiastic.
            """,
            
            "skills": f"""
            Write a polished skills paragraph (MAX 55 WORDS):
            - Discuss your most relevant technical skills and experiences matching the job requirements
            - Include specific examples with quantifiable metrics when possible
            - Show how your background aligns with company needs
            
            Job Requirements: {job_description[:500]}
            Background: {resume_text[:600]}
            
            Write a complete, polished paragraph. Maximum 55 words. No placeholders. Focus on concrete achievements.
            """,
            
            "achievements": f"""
            Write a polished achievements paragraph (MAX 55 WORDS):
            - Highlight specific projects and accomplishments demonstrating your capabilities
            - Emphasize measurable impact and concrete results
            - Connect achievements to what you can contribute in this role
            
            Job Description: {job_description[:400]}
            Experience: {resume_text[:600]}
            
            Write a complete, polished paragraph. Maximum 55 words. No placeholders. Focus on impact.
            """,
            
            "company_knowledge": f"""
            Write a polished company knowledge paragraph (MAX 55 WORDS):
            - Show understanding of the company's mission, values, or work
            - Explain why you're specifically interested in joining this company
            - Demonstrate alignment with their culture and objectives
            
            Job Description: {job_description[:400]}
            Company Name: {company_name or "the company"}
            Additional Context: {context}
            
            Write a complete, polished paragraph. Maximum 55 words. No placeholders or examples. Show genuine interest.
            """,
            
            "closing": f"""
            Write a polished closing paragraph (MAX 55 WORDS):
            - Reinforce your enthusiasm for the opportunity
            - Express interest in discussing how you can contribute
            - Thank them for their time and consideration
            
            Write a complete, polished paragraph. Maximum 55 words. No placeholders. Professional and forward-looking.
            """
        }
        
        prompt = prompts.get(paragraph_type, prompts["opening"])
        
        response = self.model.generate_content(prompt)
        paragraph = response.text.strip()
        
        # Ensure it's under 55 words
        words = paragraph.split()
        if len(words) > 55:
            paragraph = ' '.join(words[:55]) + '...'
        
        return paragraph
    
    def generate_cover_letter(self, job_description, resume_text="", context=""):
        """
        Generate complete cover letter (5 paragraphs as per template)
        
        Args:
            job_description (str): Full job posting
            resume_text (str): Optimized resume content for context
            context (str): Additional context or template instructions
            
        Returns:
            dict: {
                'company_name': str,
                'paragraphs': dict,
                'full_text': str
            }
        """
        # Extract company name first (needed for prompts)
        company_name = self.extract_company_name(job_description)
        
        # Generate each paragraph (5 paragraphs total)
        paragraphs = {
            'opening': self.generate_paragraph('opening', job_description, resume_text, context, company_name),
            'skills': self.generate_paragraph('skills', job_description, resume_text, context, company_name),
            'achievements': self.generate_paragraph('achievements', job_description, resume_text, context, company_name),
            'company_knowledge': self.generate_paragraph('company_knowledge', job_description, resume_text, context, company_name),
            'closing': self.generate_paragraph('closing', job_description, resume_text, context, company_name)
        }
        
        return {
            'company_name': company_name,
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
        
        # Extract details from job description
        company_name = self.extract_company_name(job_description)
        job_title, hiring_mgr = self.extract_job_details(job_description)
        
        # Generate AI paragraphs
        result = self.generate_cover_letter(job_description, resume_text, context)
        paragraphs = result['paragraphs']
        
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
    
    print(f"✅ Cover letter created: {filename}")
    print(f"✅ Company: {company or 'Hiring Manager'}")
