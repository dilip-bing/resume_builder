"""
Google Gemini AI Resume Optimizer for ATS
Optimizes resume content for specific job descriptions while preserving 90%+ original text
Respects character limits to prevent text overflow
"""

import json
from typing import Dict, List, Tuple, Optional
import streamlit as st
from char_limiter import get_limiter


class GeminiATSOptimizer:
    """Optimizes resume content for ATS (Applicant Tracking Systems) using Google Gemini API"""
    
    def __init__(self, api_key: str):
        """Initialize Gemini API with the provided key"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            # Use Gemini 2.5 Pro (best quality, advanced reasoning)
            # Note: Must use full model name with "models/" prefix
            self.model = genai.GenerativeModel('models/gemini-2.5-pro')
            self.genai = genai
                    
        except ImportError:
            raise ImportError(
                "google-generativeai package not installed. "
                "Install it with: pip install google-generativeai"
            )
    
    def optimize_resume(self, job_description: str, resume_content: Dict, char_limits: Optional[Dict] = None) -> Tuple[Dict, Dict]:
        """
        Optimize resume content for a specific job description
        
        Args:
            job_description: The target job posting text
            resume_content: Current resume content from resume_content.json
            char_limits: Optional dict of field-specific character limits
            
        Returns:
            Tuple of (optimized_resume_content, optimization_report)
        """
        
        print("\n" + "="*70)
        print("[AI OPTIMIZER] Starting optimization process...")
        print("="*70)
        
        # Extract current resume text for analysis
        current_text = self._extract_resume_text(resume_content)
        print(f"[AI OPTIMIZER] Extracted resume text: {len(current_text)} characters")
        
        # Calculate character limits if not provided
        if char_limits is None:
            print("[AI OPTIMIZER] Calculating character limits...")
            char_limits = self._calculate_char_limits(resume_content)
            print(f"[AI OPTIMIZER] Character limits calculated for {len(char_limits)} fields")
        
        # Build the optimization prompt with character limits
        print("[AI OPTIMIZER] Building optimization prompt...")
        prompt = self._build_optimization_prompt(job_description, resume_content, char_limits)
        print(f"[AI OPTIMIZER] Prompt length: {len(prompt)} characters")
        
        # Call Gemini API
        try:
            print("[AI OPTIMIZER] Calling Gemini API (models/gemini-2.5-pro - Advanced Reasoning)...")
            print("[AI OPTIMIZER] This may take 15-45 seconds...")
            
            response = self.model.generate_content(prompt)
            result_text = response.text
            
            print(f"[AI OPTIMIZER] Received response: {len(result_text)} characters")
            print(f"[AI OPTIMIZER] Response preview (first 200 chars):")
            print(f"   {result_text[:200]}...")
            
            # Parse the AI response to get optimized content
            print("[AI OPTIMIZER] Parsing AI response...")
            optimized_content, report = self._parse_ai_response(result_text, resume_content)
            
            # DEBUG: Show what AI returned
            print("\n" + "="*70)
            print("[DEBUG] AI RESPONSE STRUCTURE:")
            print("="*70)
            if 'skills' in optimized_content:
                print("Skills section:")
                for key, value in optimized_content['skills'].items():
                    print(f"  {key}: {type(value).__name__}")
                    if isinstance(value, dict):
                        print(f"    Keys: {list(value.keys())}")
                        print(f"    Value: {str(value)[:100]}")
                    else:
                        print(f"    Value: {str(value)[:100]}")
            print("="*70 + "\n")
            
            # Merge optimized values with original metadata
            print("[AI OPTIMIZER] Merging optimized content with original metadata...")
            optimized_content = self._merge_with_original_metadata(optimized_content, resume_content)
            
            # DEBUG: Show merged result
            print("\n" + "="*70)
            print("[DEBUG] MERGED RESULT STRUCTURE:")
            print("="*70)
            if 'skills' in optimized_content:
                print("Skills section after merge:")
                for key, value in optimized_content['skills'].items():
                    print(f"  {key}: {type(value).__name__}")
                    if isinstance(value, dict):
                        print(f"    Keys: {list(value.keys())}")
                        print(f"    Has paragraph_index: {'paragraph_index' in value}")
                        if 'paragraph_index' in value:
                            print(f"    paragraph_index value: {value['paragraph_index']}")
                        if 'value' in value:
                            print(f"    Value: {str(value['value'])[:80]}")
            print("="*70 + "\n")
            
            print(f"[AI OPTIMIZER] Parsing complete!")
            print(f"   - Keywords extracted: {len(report.get('keywords_extracted', []))}")
            print(f"   - Keywords added: {len(report.get('keywords_added', []))}")
            print(f"   - Match score estimate: {report.get('match_score_estimate', 'N/A')}")
            
            # Validate character limits and check for unauthorized fields
            print("[AI OPTIMIZER] Validating character limits and structure...")
            validation_results = self._validate_char_limits(optimized_content, char_limits)
            report['char_limit_validation'] = validation_results
            
            # Remove unauthorized skill fields if any were created
            if 'skills' in optimized_content and isinstance(optimized_content['skills'], dict):
                allowed_skill_fields = {'languages', 'software', 'tools'}
                unauthorized_fields = [k for k in optimized_content['skills'].keys() if k not in allowed_skill_fields]
                if unauthorized_fields:
                    print(f"   [CLEANING] Removing unauthorized skill fields: {unauthorized_fields}")
                    for field in unauthorized_fields:
                        del optimized_content['skills'][field]
                    print(f"   [CLEANED] Unauthorized fields removed from response")
            
            violations = validation_results.get('violations', [])
            warnings = validation_results.get('warnings', [])
            print(f"   - Violations: {len(violations)}")
            print(f"   - Warnings: {len(warnings)}")
            
            if violations:
                print("[AI OPTIMIZER] WARNING: Character limit violations detected!")
                for v in violations[:3]:
                    print(f"      {v}")
            
            print("[AI OPTIMIZER] Optimization complete!")
            print("="*70 + "\n")
            
            return optimized_content, report
            
        except Exception as e:
            print(f"[AI OPTIMIZER] ERROR: {str(e)}")
            print("="*70 + "\n")
            raise Exception(f"Gemini API Error: {str(e)}")
    
    def _extract_resume_text(self, resume_content: Dict) -> str:
        """Extract all text from resume content for analysis"""
        text_parts = []
        
        # Add professional summary
        if "professional_summary" in resume_content:
            text_parts.append(resume_content["professional_summary"])
        
        # Add experience bullets
        if "experience" in resume_content:
            for exp in resume_content["experience"]:
                for bullet_key in ["bullet_1", "bullet_2", "bullet_3", "bullet_4"]:
                    if bullet_key in exp:
                        text_parts.append(exp[bullet_key])
        
        # Add skills
        for skill_category in ["technical_skills", "languages", "frameworks"]:
            if skill_category in resume_content:
                text_parts.append(resume_content[skill_category])
        
        return "\n".join(text_parts)
    
    def _calculate_char_limits(self, resume_content: Dict) -> Dict:
        """Calculate character limits for all resume fields with 25% safety buffer"""
        limiter = get_limiter()
        limits = {}
        
        # Apply 20% safety buffer to all limits (e.g., 100 char limit -> 80 char max for AI)
        SAFETY_BUFFER = 0.80
        
        # Skills section (languages, software, tools) - with 20% buffer for safety
        if "skills" in resume_content and isinstance(resume_content["skills"], dict):
            for skill_key, skill_data in resume_content["skills"].items():
                if isinstance(skill_data, dict) and "value" in skill_data:
                    skill_text = skill_data["value"]
                    label = skill_data.get("label", skill_key.title())
                    prefix = f"{label}: "
                    limit_info = limiter.get_adaptive_limit(prefix, skill_text, skill_text)
                    # Apply 25% buffer to prevent overflow
                    limits[f"skills.{skill_key}"] = int(limit_info['current_limit'] * SAFETY_BUFFER)
        
        # Professional experience bullets
        if "professional" in resume_content and isinstance(resume_content["professional"], list):
            for exp_idx, exp in enumerate(resume_content["professional"]):
                # Tech stack - with 25% buffer
                if "tech_stack" in exp and isinstance(exp["tech_stack"], dict) and "value" in exp["tech_stack"]:
                    tech_text = exp["tech_stack"]["value"]
                    limit_info = limiter.get_adaptive_limit("Tech Stack: ", tech_text, tech_text)
                    limits[f"professional[{exp_idx}].tech_stack"] = int(limit_info['current_limit'] * SAFETY_BUFFER)
                
                # Bullets - with 25% buffer
                if "bullets" in exp and isinstance(exp["bullets"], list):
                    for bullet_idx, bullet in enumerate(exp["bullets"]):
                        if isinstance(bullet, dict) and "value" in bullet:
                            bullet_text = bullet["value"]
                            limit_info = limiter.get_adaptive_limit("• ", bullet_text, bullet_text)
                            limits[f"professional[{exp_idx}].bullets[{bullet_idx}]"] = int(limit_info['current_limit'] * SAFETY_BUFFER)
        
        # Projects - with 25% buffer
        if "projects" in resume_content and isinstance(resume_content["projects"], list):
            for proj_idx, proj in enumerate(resume_content["projects"]):
                # Tech stack - with 25% buffer
                if "tech_stack" in proj and isinstance(proj["tech_stack"], dict) and "value" in proj["tech_stack"]:
                    tech_text = proj["tech_stack"]["value"]
                    limit_info = limiter.get_adaptive_limit("Tech Stack: ", tech_text, tech_text)
                    limits[f"projects[{proj_idx}].tech_stack"] = int(limit_info['current_limit'] * SAFETY_BUFFER)
                
                # Bullets - with 25% buffer
                if "bullets" in proj and isinstance(proj["bullets"], list):
                    for bullet_idx, bullet in enumerate(proj["bullets"]):
                        if isinstance(bullet, dict) and "value" in bullet:
                            bullet_text = bullet["value"]
                            limit_info = limiter.get_adaptive_limit("• ", bullet_text, bullet_text)
                            limits[f"projects[{proj_idx}].bullets[{bullet_idx}]"] = int(limit_info['current_limit'] * SAFETY_BUFFER)
        
        # Leadership bullets - with 25% buffer
        if "leadership" in resume_content and isinstance(resume_content["leadership"], list):
            for lead_idx, lead in enumerate(resume_content["leadership"]):
                if "bullets" in lead and isinstance(lead["bullets"], list):
                    for bullet_idx, bullet in enumerate(lead["bullets"]):
                        if isinstance(bullet, dict) and "value" in bullet:
                            bullet_text = bullet["value"]
                            limit_info = limiter.get_adaptive_limit("• ", bullet_text, bullet_text)
                            limits[f"leadership[{lead_idx}].bullets[{bullet_idx}]"] = int(limit_info['current_limit'] * SAFETY_BUFFER)
        
        return limits
    
    def _build_optimization_prompt(self, job_description: str, resume_content: Dict, char_limits: Dict) -> str:
        """Build the prompt for Gemini to optimize the resume with character limit constraints"""
        
        resume_json = json.dumps(resume_content, indent=2)
        
        # Extract current skill values for additive strategy
        current_languages = ""
        current_software = ""
        current_tools = ""
        if "skills" in resume_content and isinstance(resume_content["skills"], dict):
            skills = resume_content["skills"]
            if "languages" in skills:
                lang_data = skills["languages"]
                current_languages = lang_data.get("value", "") if isinstance(lang_data, dict) else str(lang_data)
            if "software" in skills:
                soft_data = skills["software"]
                current_software = soft_data.get("value", "") if isinstance(soft_data, dict) else str(soft_data)
            if "tools" in skills:
                tool_data = skills["tools"]
                current_tools = tool_data.get("value", "") if isinstance(tool_data, dict) else str(tool_data)
        
        # Format character limits for prompt
        limits_info = "\n".join([f"  - {field}: MAX {limit} characters" for field, limit in char_limits.items()])
        
        prompt = f"""You are an expert ATS (Applicant Tracking System) resume optimizer. Your PRIMARY goal is to achieve 95%+ keyword match using an ADDITIVE strategy - ADD keywords to existing content, don't replace unless necessary.

JOB DESCRIPTION:
{job_description}

CURRENT RESUME (in JSON format):
{resume_json}

*** CURRENT SKILL VALUES (YOU WILL ADD TO THESE, NOT REPLACE) ***
- Current Languages: {current_languages}
- Current Software: {current_software}
- Current Tools: {current_tools}

*** CRITICAL: CHARACTER LIMIT CONSTRAINTS ***
Each field has a STRICT character limit based on pixel-perfect formatting.
These limits include a 20% safety buffer - YOU MUST STAY UNDER THESE LIMITS!
{limits_info}

*** ABSOLUTE REQUIREMENT: NEVER EXCEED THESE CHARACTER LIMITS! ***
If you exceed ANY limit, the resume formatting will break and be rejected.
Count characters carefully BEFORE finalizing each field.
When adding keywords, COUNT the total length - if you're over, REMOVE keywords until under limit.
Better to have fewer keywords than to exceed the limit!
The limits shown are MAXIMUM - aim for 5-10 chars BELOW each limit for safety.

*** OPTIMIZATION PRIORITY (IN THIS EXACT ORDER) ***:
1. **SKILLS SECTION MODIFICATION IS MANDATORY** (skills.languages, skills.software, skills.tools)
   - YOU MUST ADD KEYWORDS TO EXISTING - This is priority #1!
   - ADDITIVE STRATEGY: Keep current + add missing job keywords
   - If job is UI/UX: ADD Figma, Adobe XD, Sketch, InVision, Prototyping, Wireframing, User Research, etc.
   - If job is Backend: ADD frameworks, databases, APIs relevant to job description
   - If job is Mobile: ADD iOS/Android SDKs, mobile frameworks from job description
   - This section MUST HAVE MORE KEYWORDS - visible expansion required!

2. **TECH STACKS MUST HAVE ADDED KEYWORDS** (professional[].tech_stack, projects[].tech_stack)
   - ADDITIVE STRATEGY: Keep existing tech + add new from job description
   - Add ALL relevant technologies missing from current value
   - This is critical for ATS keyword matching
   - Stay under character limits - prioritize most important keywords

3. **Bullet point optimization** (lower priority - only if space allows)
   - ADD keywords naturally to existing text
   - Maintain core achievements and quantifiable metrics

YOUR TASK:

STEP 1: **Extract EVERY SINGLE keyword from job description**:
   - Identify the PRIMARY ROLE (e.g., UI/UX Designer, Backend Engineer, Data Scientist, Mobile Developer, DevOps, Full-Stack, etc.)
   - Extract EVERY programming language mentioned
   - Extract EVERY tool, software, framework, library mentioned
   - Extract EVERY methodology, practice, concept mentioned
   - Extract soft skills (leadership, communication, collaboration)
   - Industry terms and buzzwords - ALL OF THEM
   - Exact phrases (e.g., "cross-functional teams", "agile methodologies")
   - Acronyms and their full forms
   - Action verbs (e.g., "spearheaded", "architected", "optimized")
   - **TARGET**: Extract 50-100+ keywords from job description
   - **GOAL**: 95%+ of these keywords MUST appear in the optimized resume

STEP 2: **ADDITIVE KEYWORD STRATEGY** - ADD TO EXISTING, DON'T REPLACE:

   >>> ABSOLUTE HIGHEST PRIORITY - SKILLS SECTION AUGMENTATION <<<
   
   *** YOU MUST ADD KEYWORDS TO ALL THREE SKILLS FIELDS ***
   *** IF NO NEW KEYWORDS ADDED, YOU HAVE FAILED THIS TASK ***
   *** PRESERVE EXISTING - ADD JOB-SPECIFIC KEYWORDS ***
   
   ADDITIVE PROCESS FOR EACH FIELD:
   1. READ current comma-separated values in the field
   2. IDENTIFY keywords from STEP 1 that are missing
   3. ADD missing job-relevant keywords to the existing list
   4. Remove ONLY if: (a) completely irrelevant to target role, OR (b) space needed for critical job keywords
   5. Final result = CURRENT + NEW_JOB_KEYWORDS (merged, deduplicated)
   6. Ensure total stays UNDER character limit
   
   - **skills.languages: ADD JOB LANGUAGES**
     * Current value: "{current_languages}"
     * Your task: ADD languages from job description that are missing
     * Keep existing relevant languages, add new ones from job posting
     * Only remove if completely irrelevant to role or need space
     * EXAMPLE ADDITIVE PROCESS:
       - Current: "HTML5, CSS3, JavaScript (ES6+), TypeScript, SCSS"
       - Job mentions: "React, Python, SQL"
       - Result: "HTML5, CSS3, JavaScript (ES6+), TypeScript, SCSS, React, Python, SQL"
   
   - **skills.software: ADD JOB TOOLS/SOFTWARE**
     * Current value: "{current_software}"
     * Your task: ADD role-specific tools from job description that are missing
     * Keep existing relevant tools, add new ones from job posting
     * Only remove if not relevant to target role or need space
     * EXAMPLE ADDITIVE PROCESS:
       - Current: "Figma, Sketch, Adobe XD"
       - Job mentions: "InVision, Miro, Principle, Zeplin"
       - Result: "Figma, Sketch, Adobe XD, InVision, Miro, Principle, Zeplin"
   
   - **skills.tools: ADD JOB METHODOLOGIES/PRACTICES**
     * Current value: "{current_tools}"
     * Your task: ADD methodologies, frameworks, practices from job description
     * Keep existing relevant items, add new ones from job posting
     * This is your keyword expansion field - pack it with job keywords
     * EXAMPLE ADDITIVE PROCESS:
       - Current: "Wireframing, Prototyping, User Research"
       - Job mentions: "Usability Testing, A/B Testing, Design Systems, Accessibility, Responsive Design"
       - Result: "Wireframing, Prototyping, User Research, Usability Testing, A/B Testing, Design Systems, Accessibility, Responsive Design"

   >>> SECOND PRIORITY - TECH STACKS - ADD JOB TECHNOLOGIES <<<
   - **professional[].tech_stack: ADD KEYWORDS**
   - **projects[].tech_stack: ADD KEYWORDS**
     * Process: CURRENT_TECH_STACK + NEW_JOB_TECHNOLOGIES (merged, deduplicated)
     * ADD every relevant framework, library, tool from job posting
     * Keep existing relevant technologies, add new ones
     * Remove only if completely unrelated to role or need space for critical job keywords
     * Aim for 10-15+ technologies per tech stack (if space allows)
     * ADDITIVE EXAMPLES:
       - Current: "React, MongoDB, Docker"
       - Job mentions: "Node.js, PostgreSQL, Redis, AWS, Kubernetes"  
       - Result: "React, MongoDB, Docker, Node.js, PostgreSQL, Redis, AWS, Kubernetes"

   >>> THIRD PRIORITY - BULLET POINTS - KEYWORD ENHANCEMENT <<<
   - **professional[].bullets, projects[].bullets, leadership[].bullets**
     * Keep core achievements and metrics (numbers, percentages)
     * ADD job keywords naturally into existing sentences
     * Rephrase to include more job-specific terminology
     * Do NOT remove quantifiable achievements
     * Target: 60-70% text preservation with keyword enhancement

   [DO] Additional Rules:
   - ATS MATCH SCORE IS PRIORITY #1 - aim for 95%+ keyword coverage
   - Extract and use 80-100+ keywords from job description
   - Skills sections MUST have added keywords (visible expansion)
   - Target 60-70% text preservation for bullet points (aggressive keyword insertion)
   - Replace generic phrases with keyword-rich equivalents
   - Use EXACT terminology from job posting (copy-paste keywords)
   - Keep quantifiable metrics and numbers from original text
   - Character limits have 20% buffer - use every available character for keywords

   [DO NOT TOUCH] FORBIDDEN - CRITICAL:
   - **education[] - DO NOT MODIFY AT ALL**
   - **coursework[] - DO NOT MODIFY AT ALL**
   - **GPA - DO NOT MODIFY AT ALL**
   - **School names, degrees, dates - KEEP EXACTLY AS IS**
   - **DO NOT CREATE NEW SKILL FIELDS** - Only modify languages/software/tools
   - Company names, job titles, dates in professional/projects/leadership
   
   [DON'T] Forbidden Actions:
   - DO NOT add false claims or exaggerations
   - DO NOT change job titles unless critical for ATS
   - DO NOT remove quantifiable achievements (numbers, percentages, metrics)
   - DO NOT change company names or dates
   - DO NOT add completely new experience that doesn't exist
   - *** NEVER EXCEED CHARACTER LIMITS - this breaks resume formatting!
   - DO NOT create new skill categories (like "web_design", "frameworks", "design_tools")
   - ONLY use the existing three skill fields: languages, software, tools

STEP 3: **Examples of REQUIRED optimizations:**

   >>> EXAMPLE 1 - SKILLS MODIFICATION (UI/UX Designer Role):
   Original skills.software: "Android Studio, Xcode, VS Code, Git"
   [OPTIMIZED]: "Figma, Adobe XD, Sketch, InVision, Zeplin, Git"
   (Removed Android Studio, Xcode, VS Code - Added UI/UX specific tools)
   
   Original skills.tools: "Git, Docker, GitHub, Agile"
   [OPTIMIZED]: "Prototyping, Wireframing, User Research, Usability Testing, Design Systems, Agile"
   (Removed development tools - Added design methodologies)

   >>> EXAMPLE 2 - SKILLS MODIFICATION (Backend Engineer Role):
   Original skills.languages: "Java, Python, C++"
   [OPTIMIZED]: "Java, Python, Go, SQL, TypeScript, C++"
   (Added languages from job description)

   Original skills.software: "VS Code, Git"
   [OPTIMIZED]: "IntelliJ IDEA, Docker, Kubernetes, Postman, Redis, Git, Jenkins"
   (Added backend development tools)

   Original skills.tools: "GitHub, Maven"
   [OPTIMIZED]: "Spring Boot, Hibernate, REST APIs, GraphQL, Microservices, JUnit, Maven"
   (Added backend frameworks and practices)

   >>> EXAMPLE 3 - TECH STACK EXPANSION (Data Science Role):
   Original Tech Stack: "Python, Jupyter"
   [OPTIMIZED] (under limit): "Python, TensorFlow, PyTorch, Pandas, NumPy, Scikit-learn, Jupyter, SQL"
   (Added ML/Data tools)

   [WRONG] - Don't create new skill fields:
   Original: skills has only "languages", "software", "tools"
   [WRONG]: skills has "languages", "software", "tools", "web_design" (FAILED - New field added!)
   
   [WRONG] - Don't return skills unchanged:
   Original skills.software: "Android Studio, Xcode"
   [WRONG]: "Android Studio, Xcode" (unchanged - FAILURE!)

   Good Bullet Optimization (Lower Priority):
   Original: "Led a team of engineers"
   Optimized: "Led cross-functional team of engineers using Agile/Scrum methodologies"
   (Added keywords while preserving achievement)

STEP 4: **Return your response** in this EXACT format:

*** CRITICAL REMINDER BEFORE YOU RESPOND ***
- What is the PRIMARY ROLE in this job description? (Identify it first!)
- What skills would a 5-year experienced professional in this role have?
- Have you ONLY modified the three existing fields: languages, software, tools? (No new fields!)
- Have you REMOVED less important keywords if fields are getting too long?
- Skills must be MODIFIED with role-appropriate values:
  * languages: Add/replace with role-relevant programming languages
  * software: Add/replace with role-specific tools (remove generic ones if needed)
  * tools: Add/replace with methodologies/frameworks for this role
- Have you expanded all tech_stack fields with relevant technologies? (MANDATORY)
- COUNT EVERY CHARACTER: Count len() of EACH field value you're about to return!
- Are ALL fields at least 5-10 chars BELOW their limits? (If not, REMOVE keywords!)
- FINAL CHECK: Verify you have NOT created any new skill fields beyond languages/software/tools!

```json
{{
  "optimized_resume": {{
    "skills": {{
      // ONLY THESE THREE FIELDS - DO NOT ADD MORE!
      // You can return just the value string - metadata will be preserved automatically
      "languages": "[KEEP RELEVANT + ADD FROM JOB - REMOVE GENERIC IF TOO LONG]",
      "software": "[KEEP RELEVANT + ADD ROLE-SPECIFIC TOOLS - REMOVE GENERIC IF TOO LONG]",
      "tools": "[KEEP RELEVANT + ADD METHODOLOGIES/FRAMEWORKS - REMOVE LESS CRITICAL IF TOO LONG]"
      // STOP HERE - NO MORE SKILL FIELDS!
    }},
    "professional": [
      {{
        "tech_stack": "[EXPANDED WITH ROLE-RELEVANT TECH - STAY UNDER CHAR LIMIT]",
        "bullets": [
          "[OPTIMIZED BULLET WITH KEYWORDS]",
          "[OPTIMIZED BULLET WITH KEYWORDS]"
        ]
      }}
    ],
    "projects": [
      {{
        "tech_stack": "[EXPANDED WITH KEYWORDS]",
        "bullets": ["[OPTIMIZED]", "[OPTIMIZED]"]
      }}
    ]
    ... rest of resume structure ...
  }},
  "report": {{
    "keywords_extracted": ["keyword1", "keyword2", ...],
    "keywords_added": ["keyword1", "keyword2", ...],
    "match_score_estimate": "95-98%",
    "changes_summary": "Identified role as [ROLE]. MODIFIED skills.languages, skills.software, skills.tools with [X] role-appropriate keywords. Expanded tech_stacks with industry-standard technologies..."
  }}
}}
```

REMEMBER: Your success is measured by:
1. [REQUIRED] Skills sections MUST be modified (if unchanged, you failed!)
2. [REQUIRED] 95%+ keyword match score
3. [REQUIRED] ALL fields STRICTLY under character limits - AIM 5-10 CHARS BELOW MAXIMUM!
   - The limits shown already have a 25% safety buffer applied
   - If you go over even by 1 character, you FAILED
   - Do NOT push to the limit - stay comfortably under
   - When in doubt, remove keywords to stay under limit
4. [REQUIRED] 70-80% text preservation in bullet points
5. [REQUIRED] Authentic achievements and metrics maintained

*** ZERO TOLERANCE FOR CHARACTER LIMIT VIOLATIONS ***
*** AIM FOR 5-10 CHARACTERS BELOW EACH LIMIT ***

Return ONLY valid JSON. No explanations before or after."""

        return prompt

    
    def _parse_ai_response(self, response_text: str, original_resume: Dict) -> Tuple[Dict, Dict]:
        """Parse the Gemini API response to extract optimized content and report"""
        
        print("[AI OPTIMIZER] Parsing AI response...")
        print(f"   Raw response length: {len(response_text)} chars")
        
        try:
            # Remove markdown code blocks if present
            response_text = response_text.strip()
            
            print(f"   Checking for markdown code blocks...")
            if response_text.startswith("```json"):
                response_text = response_text[7:]
                print(f"      Removed ```json prefix")
            if response_text.startswith("```"):
                response_text = response_text[3:]
                print(f"      Removed ``` prefix")
            if response_text.endswith("```"):
                response_text = response_text[:-3]
                print(f"      Removed ``` suffix")
            response_text = response_text.strip()
            
            print(f"   Cleaned response length: {len(response_text)} chars")
            print(f"   First 100 chars: {response_text[:100]}")
            
            # Parse the JSON response
            print(f"   Attempting JSON parse...")
            parsed = json.loads(response_text)
            print(f"   JSON parse successful!")
            print(f"   Top-level keys: {list(parsed.keys())}")
            
            optimized_resume = parsed.get("optimized_resume", original_resume)
            print(f"   Optimized resume keys: {list(optimized_resume.keys())}")
            
            report = parsed.get("report", {
                "keywords_extracted": [],
                "keywords_added": [],
                "match_score_estimate": "Unknown",
                "changes_summary": "Parsing error - returning original resume"
            })
            print(f"   Report keys: {list(report.keys())}")
            
            return optimized_resume, report
            
        except json.JSONDecodeError as e:
            # If parsing fails, return original resume with error report
            print(f"   [ERROR] JSON parsing failed: {str(e)}")
            print(f"   Response text preview:")
            print(f"   {response_text[:500]}")
            
            return original_resume, {
                "error": f"Failed to parse AI response: {str(e)}",
                "keywords_extracted": [],
                "keywords_added": [],
                "match_score_estimate": "0%",
                "changes_summary": "Error occurred - resume unchanged"
            }
    
    def _merge_with_original_metadata(self, optimized: Dict, original: Dict) -> Dict:
        """Merge optimized values with original metadata (paragraph_index, labels, etc.)"""
        import copy
        
        # Start with deep copy of original to preserve all metadata
        merged = copy.deepcopy(original)
        
        # Merge skills - preserve paragraph_index and label from original
        if 'skills' in optimized and isinstance(optimized['skills'], dict):
            if 'skills' not in merged:
                merged['skills'] = {}
            
            for skill_key, skill_value in optimized['skills'].items():
                # Only process allowed skill fields
                if skill_key in ['languages', 'software', 'tools']:
                    # If AI returned just a string, wrap it in original metadata structure
                    if isinstance(skill_value, str):
                        if skill_key in merged['skills'] and isinstance(merged['skills'][skill_key], dict):
                            # Preserve metadata, update value
                            merged['skills'][skill_key]['value'] = skill_value
                        else:
                            # Shouldn't happen, but create minimal structure
                            merged['skills'][skill_key] = {
                                'label': skill_key.title(),
                                'value': skill_value,
                                'paragraph_index': None
                            }
                    # If AI returned full structure, use it but validate
                    elif isinstance(skill_value, dict):
                        if 'value' in skill_value:
                            # Preserve original metadata, update value
                            if skill_key in merged['skills'] and isinstance(merged['skills'][skill_key], dict):
                                merged['skills'][skill_key]['value'] = skill_value['value']
                            else:
                                merged['skills'][skill_key] = skill_value
        
        # Merge professional experiences - preserve paragraph_index metadata
        if 'professional' in optimized and isinstance(optimized['professional'], list):
            for idx, opt_job in enumerate(optimized['professional']):
                if idx < len(merged.get('professional', [])):
                    orig_job = merged['professional'][idx]
                    
                    # Update tech_stack but preserve paragraph_index
                    if 'tech_stack' in opt_job:
                        if isinstance(opt_job['tech_stack'], str):
                            # Simple string - preserve original paragraph_index
                            if 'tech_stack' in orig_job and isinstance(orig_job['tech_stack'], dict):
                                orig_job['tech_stack']['value'] = opt_job['tech_stack']
                            else:
                                orig_job['tech_stack'] = {
                                    'value': opt_job['tech_stack'],
                                    'paragraph_index': orig_job.get('tech_stack', {}).get('paragraph_index')
                                }
                        elif isinstance(opt_job['tech_stack'], dict) and 'value' in opt_job['tech_stack']:
                            if 'tech_stack' in orig_job and isinstance(orig_job['tech_stack'], dict):
                                orig_job['tech_stack']['value'] = opt_job['tech_stack']['value']
                    
                    # Update bullets but preserve paragraph_index
                    if 'bullets' in opt_job and isinstance(opt_job['bullets'], list):
                        for bullet_idx, opt_bullet in enumerate(opt_job['bullets']):
                            if bullet_idx < len(orig_job.get('bullets', [])):
                                orig_bullet = orig_job['bullets'][bullet_idx]
                                if isinstance(opt_bullet, str):
                                    if isinstance(orig_bullet, dict):
                                        orig_bullet['value'] = opt_bullet
                                    else:
                                        orig_job['bullets'][bullet_idx] = {
                                            'value': opt_bullet,
                                            'paragraph_index': None
                                        }
                                elif isinstance(opt_bullet, dict) and 'value' in opt_bullet:
                                    if isinstance(orig_bullet, dict):
                                        orig_bullet['value'] = opt_bullet['value']
        
        # Merge projects - preserve paragraph_index metadata
        if 'projects' in optimized and isinstance(optimized['projects'], list):
            for idx, opt_proj in enumerate(optimized['projects']):
                if idx < len(merged.get('projects', [])):
                    orig_proj = merged['projects'][idx]
                    
                    # Update tech_stack but preserve paragraph_index
                    if 'tech_stack' in opt_proj:
                        if isinstance(opt_proj['tech_stack'], str):
                            if 'tech_stack' in orig_proj and isinstance(orig_proj['tech_stack'], dict):
                                orig_proj['tech_stack']['value'] = opt_proj['tech_stack']
                            else:
                                orig_proj['tech_stack'] = {
                                    'value': opt_proj['tech_stack'],
                                    'paragraph_index': orig_proj.get('tech_stack', {}).get('paragraph_index')
                                }
                        elif isinstance(opt_proj['tech_stack'], dict) and 'value' in opt_proj['tech_stack']:
                            if 'tech_stack' in orig_proj and isinstance(orig_proj['tech_stack'], dict):
                                orig_proj['tech_stack']['value'] = opt_proj['tech_stack']['value']
                    
                    # Update bullets but preserve paragraph_index
                    if 'bullets' in opt_proj and isinstance(opt_proj['bullets'], list):
                        for bullet_idx, opt_bullet in enumerate(opt_proj['bullets']):
                            if bullet_idx < len(orig_proj.get('bullets', [])):
                                orig_bullet = orig_proj['bullets'][bullet_idx]
                                if isinstance(opt_bullet, str):
                                    if isinstance(orig_bullet, dict):
                                        orig_bullet['value'] = opt_bullet
                                    else:
                                        orig_proj['bullets'][bullet_idx] = {
                                            'value': opt_bullet,
                                            'paragraph_index': None
                                        }
                                elif isinstance(opt_bullet, dict) and 'value' in opt_bullet:
                                    if isinstance(orig_bullet, dict):
                                        orig_bullet['value'] = opt_bullet['value']
        
        # Merge leadership - preserve paragraph_index metadata
        if 'leadership' in optimized and isinstance(optimized['leadership'], list):
            for idx, opt_lead in enumerate(optimized['leadership']):
                if idx < len(merged.get('leadership', [])):
                    orig_lead = merged['leadership'][idx]
                    
                    # Update bullets but preserve paragraph_index
                    if 'bullets' in opt_lead and isinstance(opt_lead['bullets'], list):
                        for bullet_idx, opt_bullet in enumerate(opt_lead['bullets']):
                            if bullet_idx < len(orig_lead.get('bullets', [])):
                                orig_bullet = orig_lead['bullets'][bullet_idx]
                                if isinstance(opt_bullet, str):
                                    if isinstance(orig_bullet, dict):
                                        orig_bullet['value'] = opt_bullet
                                    else:
                                        orig_lead['bullets'][bullet_idx] = {
                                            'value': opt_bullet,
                                            'paragraph_index': None
                                        }
                                elif isinstance(opt_bullet, dict) and 'value' in opt_bullet:
                                    if isinstance(orig_bullet, dict):
                                        orig_bullet['value'] = opt_bullet['value']
        
        print(f"   [MERGE] Skills metadata preserved: {list(merged.get('skills', {}).keys())}")
        
        # Debug: Check if paragraph_index is preserved
        for skill_key in ['languages', 'software', 'tools']:
            if skill_key in merged.get('skills', {}):
                skill_data = merged['skills'][skill_key]
                if isinstance(skill_data, dict):
                    para_idx = skill_data.get('paragraph_index')
                    print(f"   [MERGE] skills.{skill_key} paragraph_index: {para_idx}")
        
        if 'professional' in merged:
            print(f"   [MERGE] Professional entries: {len(merged['professional'])}")
        if 'projects' in merged:
            print(f"   [MERGE] Project entries: {len(merged['projects'])}")
        
        return merged
    
    def _validate_char_limits(self, optimized_content: Dict, char_limits: Dict) -> Dict:
        """Validate that optimized content respects character limits and structure"""
        violations = []
        warnings = []
        
        # Check for unexpected new skill fields
        if 'skills' in optimized_content and isinstance(optimized_content['skills'], dict):
            allowed_skill_fields = {'languages', 'software', 'tools'}
            actual_skill_fields = set(optimized_content['skills'].keys())
            unexpected_fields = actual_skill_fields - allowed_skill_fields
            
            if unexpected_fields:
                for field in unexpected_fields:
                    violations.append(f"skills.{field}: UNAUTHORIZED NEW FIELD - AI created field that doesn't exist in template!")
                    print(f"   [VIOLATION] Unauthorized skill field detected: {field}")
        
        # Helper function to get nested value
        def get_nested_value(data, path):
            import re
            # Handle paths like "skills.languages" or "professional[0].tech_stack"
            parts = re.split(r'\.|\[|\]', path)
            parts = [p for p in parts if p]  # Remove empty strings
            
            current = data
            for part in parts:
                if part.isdigit():
                    current = current[int(part)]
                elif isinstance(current, dict):
                    if part in current:
                        current = current[part]
                        if isinstance(current, dict) and 'value' in current:
                            current = current['value']
                    else:
                        return None
                else:
                    return None
            return current
        
        # Check all fields in char_limits
        for field_path, limit in char_limits.items():
            text = get_nested_value(optimized_content, field_path)
            if text is not None and isinstance(text, str):
                if len(text) > limit:
                    violations.append(f"{field_path}: {len(text)} chars (limit: {limit})")
                elif len(text) > limit * 0.9:
                    warnings.append(f"{field_path}: {len(text)} chars (90% of limit)")
        
        return {
            "violations": violations,
            "warnings": warnings,
            "is_valid": len(violations) == 0
        }


def get_optimizer() -> GeminiATSOptimizer:
    """
    Get initialized Gemini optimizer using API key from Streamlit secrets
    
    Returns:
        GeminiATSOptimizer instance
        
    Raises:
        ValueError if API key not configured
    """
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except KeyError:
        raise ValueError(
            "Gemini API key not configured. "
            "Please add GEMINI_API_KEY to .streamlit/secrets.toml"
        )
    except Exception as e:
        raise ValueError(f"Error reading secrets.toml: {str(e)}")
    
    # Try to initialize the optimizer
    try:
        return GeminiATSOptimizer(api_key)
    except ImportError as e:
        raise ImportError(
            "google-generativeai package not installed. "
            f"Install it with: pip install google-generativeai\n"
            f"Error: {str(e)}"
        )
    except Exception as e:
        raise ValueError(f"Error initializing Gemini optimizer: {str(e)}")


def calculate_text_preservation(original: Dict, optimized: Dict) -> float:
    """
    Calculate what percentage of original text was preserved
    
    Args:
        original: Original resume content
        optimized: Optimized resume content
        
    Returns:
        Percentage of text preserved (0-100)
    """
    original_text = json.dumps(original, sort_keys=True)
    optimized_text = json.dumps(optimized, sort_keys=True)
    
    # Simple character-based comparison
    original_len = len(original_text)
    optimized_len = len(optimized_text)
    
    # Count matching characters (very rough approximation)
    matches = sum(1 for a, b in zip(original_text, optimized_text) if a == b)
    preservation_rate = (matches / max(original_len, optimized_len)) * 100
    
    return round(preservation_rate, 1)
