"""
Enhanced Resume Builder with Complete Format Preservation
Uses metadata-based format preservation for exact replication.
"""

import streamlit as st
import json
from pathlib import Path
from enhanced_format_system import EnhancedFormatBuilder
from datetime import datetime
from char_limiter import get_limiter

# Conditional import for AI optimizer (only if package installed)
try:
    from gemini_optimizer import get_optimizer, calculate_text_preservation
    GEMINI_AVAILABLE = True
except ImportError as e:
    GEMINI_AVAILABLE = False
    GEMINI_IMPORT_ERROR = str(e)

# Page config
st.set_page_config(page_title="Resume Builder - Enhanced Format", layout="wide", page_icon="📄")

# Paths
RESUME_CONTENT_TEMPLATE = "templates/resume_content_template.json"  # Fixed original (never modified)
RESUME_CONTENT_JSON = "templates/resume_content.json"  # Working copy (modified by AI)
FORMAT_METADATA_JSON = "metadata/format_metadata.json"
ORIGINAL_RESUME = "reference_docx/resume_optimized_final.docx"

# Load resume content (with file modification time for cache invalidation)
@st.cache_data
def load_resume_content(file_mtime):
    with open(RESUME_CONTENT_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def reset_to_template():
    """Reset working copy from fixed template"""
    import shutil
    shutil.copy(RESUME_CONTENT_TEMPLATE, RESUME_CONTENT_JSON)
    print(f"[RESET] Copied template to working copy")

try:
    # Ensure working copy exists
    if not Path(RESUME_CONTENT_JSON).exists():
        print("[INIT] Creating working copy from template...")
        reset_to_template()
    
    # Force reload if file changed
    file_mtime = Path(RESUME_CONTENT_JSON).stat().st_mtime
    resume_data = load_resume_content(file_mtime)
except FileNotFoundError:
    st.error(f"❌ Template not found: {RESUME_CONTENT_TEMPLATE}")
    st.info("Run extract_to_json.py first to extract content from your resume.")
    st.stop()

# Check if metadata exists
if not Path(FORMAT_METADATA_JSON).exists():
    st.error(f"❌ Format metadata not found: {FORMAT_METADATA_JSON}")
    st.info("Run enhanced_format_system.py first to extract formatting metadata.")
    st.stop()

# Initialize character limiter
try:
    char_limiter = get_limiter()
except Exception as e:
    st.warning(f"⚠️ Character limiter unavailable: {e}")
    char_limiter = None

# Helper function to display character counter
def show_char_counter(prefix, current_text, field_key, original_text=""):
    """Display adaptive character counter with visual feedback.
    
    Args:
        prefix: Fixed prefix (e.g., "Languages: ")
        current_text: Current user input
        field_key: Unique field identifier
        original_text: Original text from resume (for multi-line detection)
    """
    if char_limiter is None:
        return
    
    info = char_limiter.get_adaptive_limit(prefix, current_text, original_text)
    
    # Choose color based on remaining characters
    if info['is_at_limit']:
        color = "red"
        icon = "🚫"
    elif info['is_near_limit']:
        color = "orange"
        icon = "⚠️"
    else:
        color = "green"
        icon = "✅"
    
    # Display counter
    counter_text = f"{icon} **{info['remaining']}** characters remaining"
    
    # Add multi-line indicator if applicable
    if info['num_lines'] > 1:
        counter_text += f" _(spanning {info['num_lines']} lines)_"
    
    # Add efficiency badge if applicable
    elif info['efficiency_gain'] > 0:
        counter_text += f" _(+{info['efficiency_gain']} bonus!)_"
    
    # Show with appropriate color
    st.markdown(f":{color}[{counter_text}]", unsafe_allow_html=True)

# Title
st.title("📄 Enhanced Resume Builder")
st.markdown("**Complete format preservation using metadata system** | All formatting identical to original")

# Sidebar info
with st.sidebar:
    st.header("📊 System Info")
    st.info(f"**Format Metadata:** {FORMAT_METADATA_JSON}\n\n**Content JSON:** {RESUME_CONTENT_JSON}")
    
    st.header("🎨 Format Preservation")
    st.success("✅ Page size & margins\n✅ Paragraph spacing\n✅ Font properties\n✅ Bold/italic patterns\n✅ ALL formatting metadata")
    
    st.header("📁 Output Location")
    st.write("Generated resumes save to:\n`output/generated_resumes/`")

# Priority tabs - AI Optimization moved to first position
tab_ai, tab_skills, tab_projects, tab_leadership, tab_professional, tab_education, tab_personal = st.tabs([
    "🤖 A. AI Optimization",
    "🔧 B. Skills",
    "💼 C. Projects",
    "👥 D. Leadership",
    "🏢 E. Professional",
    "🎓 F. Education",
    "👤 G. Personal"
])

# Initialize edited data
edited_data = {
    "personal": {},
    "education": [],
    "skills": {},
    "professional": [],
    "projects": [],
    "leadership": []
}

# A. AI OPTIMIZATION TAB (moved to first position)
with tab_ai:
    st.header("🤖 AI-Powered ATS Optimization")
    st.markdown("""
    **Optimize your resume for Applicant Tracking Systems (ATS)**
    
    This feature uses Google Gemini AI to:
    - ✅ Extract keywords from job descriptions
    - ✅ Add relevant terms naturally to your resume
    - ✅ Maintain 70-80% of your original text
    - ✅ Target 95%+ ATS keyword match
    - ✅ **Aggressively optimize Skills and Tech Stacks**
    """)
    
    # Check if package is installed
    if not GEMINI_AVAILABLE:
        st.error("❌ Google Generative AI package not installed")
        st.info("""
        **Installation Required:**
        
        Run this command in your terminal:
        ```bash
        pip install google-generativeai
        ```
        
        Or if using virtual environment:
        ```bash
        .venv/Scripts/python.exe -m pip install google-generativeai
        ```
        
        Then restart the app.
        """)
        st.stop()
    
    # Check if API key is configured
    try:
        optimizer = get_optimizer()
        api_configured = True
    except ValueError as e:
        api_configured = False
        st.error("❌ " + str(e))
        st.info("""
        **Setup Instructions:**
        1. Get your API key from https://makersuite.google.com/app/apikey
        2. Open `.streamlit/secrets.toml`
        3. Replace `paste-your-api-key-here` with your actual key
        4. Restart the app
        
        For detailed instructions, see `GEMINI_API_SETUP.md`
        """)
    except ImportError as e:
        api_configured = False
        st.error("❌ Package installation issue: " + str(e))
        st.info("Try reinstalling: `pip install --upgrade google-generativeai`")
    
    if api_configured:
        st.success("✅ Gemini Pro 2.5 configured and ready (Advanced reasoning model)")
        
        # Check if there are existing optimization results in session state
        if 'optimization_done' in st.session_state and st.session_state['optimization_done']:
            st.info("ℹ️ **Previous optimization results available**")
            if st.button("🔄 Start New Optimization", type="secondary"):
                # Clear all optimization session state
                if 'optimization_done' in st.session_state:
                    del st.session_state['optimization_done']
                if 'optimized_content' in st.session_state:
                    del st.session_state['optimized_content']
                if 'optimization_report' in st.session_state:
                    del st.session_state['optimization_report']
                if 'applied_content' in st.session_state:
                    del st.session_state['applied_content']
                if 'optimization_applied' in st.session_state:
                    del st.session_state['optimization_applied']
                st.rerun()
        
        # Job description input
        st.markdown("### 📋 Step 1: Paste Job Description")
        job_description = st.text_area(
            "Paste the complete job posting here:",
            height=250,
            placeholder="Paste the full job description including requirements, responsibilities, and qualifications...",
            help="The more complete the job description, the better the optimization"
        )
        
        # Optimization button
        st.markdown("### 🎯 Step 2: Optimize Resume")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            optimize_button = st.button(
                "🚀 Optimize Resume for ATS",
                type="primary",
                use_container_width=True,
                disabled=not job_description.strip()
            )
        
        # Run optimization if button clicked
        if optimize_button and job_description.strip():
            with st.spinner("🤖 Analyzing job description and optimizing resume..."):
                try:
                    st.write("📝 **Starting AI optimization...**")
                    
                    # Run optimization
                    optimized_content, report = optimizer.optimize_resume(
                        job_description,
                        resume_data
                    )
                    
                    # Store in session state so it persists after rerun
                    st.session_state['optimized_content'] = optimized_content
                    st.session_state['optimization_report'] = report
                    st.session_state['optimization_done'] = True
                    st.session_state['last_job_description'] = job_description  # Store for cover letter
                    
                    st.success("✅ **AI optimization complete!**")
                    
                except Exception as e:
                    st.error(f"❌ Optimization Error: {str(e)}")
                    st.exception(e)
        elif optimize_button:
            st.warning("⚠️ Please paste a job description first")
        
        # Display results if optimization was done (either just now or previously)
        if 'optimization_done' in st.session_state and st.session_state['optimization_done']:
            # Retrieve from session state
            optimized_content = st.session_state['optimized_content']
            report = st.session_state['optimization_report']
            
            # Calculate text preservation
            preservation = calculate_text_preservation(resume_data, optimized_content)
            
            # Display results
            st.markdown("---")
            st.markdown("### 📊 Optimization Results")
            
            # Check character limit validation
            validation = report.get('char_limit_validation', {})
            violations = validation.get('violations', [])
            warnings = validation.get('warnings', [])
            
            # Show validation status
            if violations:
                st.error(f"⚠️ **Character Limit Violations Detected!** ({len(violations)} fields exceed limits)")
                with st.expander("View Violations"):
                    for violation in violations:
                        st.write(f"• {violation}")
                st.warning("⚠️ **Warning:** These fields may affect resume formatting. Review before applying.")
            elif warnings:
                st.warning(f"⚠️ {len(warnings)} field(s) near character limit (90%+)")
                with st.expander("View Warnings"):
                    for warning in warnings:
                        st.write(f"• {warning}")
            else:
                st.success("✅ All fields within character limits!")
            
            st.markdown("---")
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                match_score = report.get('match_score_estimate', 'Unknown')
                st.metric("ATS Match Score", match_score)
            with col2:
                st.metric("Text Preservation", f"{preservation}%")
            with col3:
                keywords_added = len(report.get('keywords_added', []))
                st.metric("Keywords Added", keywords_added)
            
            # Show report details
            with st.expander("📋 View Detailed Report"):
                st.markdown("**Keywords Extracted from Job Description:**")
                keywords_extracted = report.get('keywords_extracted', [])
                if keywords_extracted:
                    # Handle both list of strings and list of dicts
                    if len(keywords_extracted) > 0 and isinstance(keywords_extracted[0], dict):
                        keyword_strs = [str(k) for k in keywords_extracted[:20]]
                    else:
                        keyword_strs = [str(k) for k in keywords_extracted[:20]]
                    st.write(", ".join(keyword_strs))
                else:
                    st.write("No keywords listed")
                
                st.markdown("**Changes Summary:**")
                st.write(report.get('changes_summary', 'No summary available'))
                
                if 'keywords_added' in report and report['keywords_added']:
                    st.markdown("**Keywords Successfully Added:**")
                    # Handle both list of strings and list of dicts
                    keywords_added = report['keywords_added']
                    if len(keywords_added) > 0 and isinstance(keywords_added[0], dict):
                        keyword_strs = [str(k) for k in keywords_added[:15]]
                    else:
                        keyword_strs = [str(k) for k in keywords_added[:15]]
                    st.write(", ".join(keyword_strs))
            
            # Preview changes
            with st.expander("🔍 Preview Changes (Before/After)", expanded=True):
                # Show Skills comparison
                if 'skills' in resume_data and 'skills' in optimized_content:
                    skills_orig = resume_data['skills']
                    skills_opt = optimized_content['skills']
                    
                    # Pick first available skill category
                    skill_key = None
                    for key in ['languages', 'software', 'tools']:
                        if key in skills_orig and key in skills_opt:
                            skill_key = key
                            break
                    
                    if skill_key:
                        st.markdown(f"**Skills - {skill_key.title()}:**")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("*Before:*")
                            orig_val = skills_orig[skill_key].get('value', '') if isinstance(skills_orig[skill_key], dict) else skills_orig[skill_key]
                            st.text_area("Original", orig_val, height=80, key="before_skills", disabled=True)
                        
                        with col2:
                            st.markdown("*After:*")
                            opt_val = skills_opt[skill_key].get('value', '') if isinstance(skills_opt[skill_key], dict) else skills_opt[skill_key]
                            st.text_area("Optimized", opt_val, height=80, key="after_skills", disabled=True)
                
                # Show Professional Experience bullet comparison
                if 'professional' in resume_data and 'professional' in optimized_content:
                    if resume_data['professional'] and optimized_content['professional']:
                        exp_orig = resume_data['professional'][0]
                        exp_opt = optimized_content['professional'][0]
                        
                        if 'bullets' in exp_orig and 'bullets' in exp_opt:
                            if exp_orig['bullets'] and exp_opt['bullets']:
                                st.markdown("**Professional Experience - First Bullet:**")
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown("*Before:*")
                                    bullet_val = exp_orig['bullets'][0].get('value', '') if isinstance(exp_orig['bullets'][0], dict) else exp_orig['bullets'][0]
                                    st.text_area("Original", bullet_val, height=120, key="before_exp", disabled=True)
                                
                                with col2:
                                    st.markdown("*After:*")
                                    bullet_val = exp_opt['bullets'][0].get('value', '') if isinstance(exp_opt['bullets'][0], dict) else exp_opt['bullets'][0]
                                    st.text_area("Optimized", bullet_val, height=120, key="after_exp", disabled=True)
                
                # Show Projects bullet comparison
                if 'projects' in resume_data and 'projects' in optimized_content:
                    if resume_data['projects'] and optimized_content['projects']:
                        proj_orig = resume_data['projects'][0]
                        proj_opt = optimized_content['projects'][0]
                        
                        if 'bullets' in proj_orig and 'bullets' in proj_opt:
                            if proj_orig['bullets'] and proj_opt['bullets']:
                                st.markdown("**Projects - First Bullet:**")
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown("*Before:*")
                                    bullet_val = proj_orig['bullets'][0].get('value', '') if isinstance(proj_orig['bullets'][0], dict) else proj_orig['bullets'][0]
                                    st.text_area("Original", bullet_val, height=120, key="before_proj", disabled=True)
                                
                                with col2:
                                    st.markdown("*After:*")
                                    bullet_val = proj_opt['bullets'][0].get('value', '') if isinstance(proj_opt['bullets'][0], dict) else proj_opt['bullets'][0]
                                    st.text_area("Optimized", bullet_val, height=120, key="after_proj", disabled=True)
            
            # Quick Actions - Always Available
            st.markdown("---")
            st.markdown("### ⚡ Quick Actions")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                # Generate Resume PDF button - always available
                if st.button("📄 Regenerate Resume PDF", use_container_width=True, type="secondary", key="regen_pdf_btn"):
                    with st.spinner("Generating resume PDF..."):
                        # Priority order: applied_content > optimized_content > file
                        # This ensures it works on both local and Streamlit Cloud
                        if 'applied_content' in st.session_state:
                            content_to_use = st.session_state['applied_content']
                            source = "applied_content (after Apply)"
                        elif 'optimized_content' in st.session_state:
                            content_to_use = st.session_state['optimized_content']
                            source = "optimized_content (before Apply)"
                        else:
                            # Clear cache and reload from file
                            load_resume_content.clear()
                            with open(RESUME_CONTENT_JSON, 'r', encoding='utf-8') as f:
                                content_to_use = json.load(f)
                            source = "file (no optimization)"
                        
                        try:
                            # Generate timestamp for unique filename
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            
                            # Show what content is being used
                            skills_preview = content_to_use.get('skills', {}).get('languages', {}).get('value', 'N/A')
                            print(f"[PDF GENERATION] Source: {source}")
                            print(f"[PDF GENERATION] Skills.languages: {skills_preview[:80]}...")
                            
                            st.info(f"📝 Using content from: **{source}**")
                            
                            # Create temp file for generation
                            import tempfile
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                                temp_path = tmp_file.name
                            
                            # Build resume using EnhancedFormatBuilder
                            builder = EnhancedFormatBuilder(ORIGINAL_RESUME, FORMAT_METADATA_JSON)
                            result = builder.build_resume_from_json(content_to_use, temp_path)
                            
                            # Read the generated file into memory
                            with open(result, "rb") as f:
                                resume_bytes = f.read()
                            
                            # Clean up temp file
                            try:
                                Path(temp_path).unlink()
                            except:
                                pass
                            
                            # Show success with download button
                            st.success(f"✅ Resume generated successfully!")
                            
                            # Provide download button with in-memory data
                            st.download_button(
                                label="⬇️ Download Resume",
                                data=resume_bytes,
                                file_name=f"resume_dilip_kumar_tc_{timestamp}.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True,
                                key=f"download_optimized_{timestamp}"
                            )
                            
                            # Store resume in session for cover letter generation
                            st.session_state['last_generated_resume'] = resume_bytes
                            st.session_state['last_resume_timestamp'] = timestamp
                            
                        except Exception as e:
                            st.error(f"❌ Error generating resume: {str(e)}")
                            import traceback
                            st.code(traceback.format_exc())
            
            with col2:
                # Download optimized JSON
                if st.button("💾 Download Optimized JSON", use_container_width=True, type="secondary"):
                    # Use same priority as PDF generation: applied > optimized > original
                    if 'applied_content' in st.session_state:
                        content_to_download = st.session_state['applied_content']
                    elif 'optimized_content' in st.session_state:
                        content_to_download = st.session_state['optimized_content']
                    else:
                        content_to_download = resume_data
                    
                    json_str = json.dumps(content_to_download, indent=2, ensure_ascii=False)
                    st.download_button(
                        label="⬇️ Download resume_content.json",
                        data=json_str,
                        file_name="resume_content_optimized.json",
                        mime="application/json",
                        use_container_width=True
                    )
            
            with col3:
                # Reset to template - clears all optimizations
                if st.button("🔄 Reset to Template", use_container_width=True, type="secondary", help="Reset resume to original template (clears AI optimizations)"):
                    try:
                        reset_to_template()
                        # Clear all optimization session state
                        if 'optimized_content' in st.session_state:
                            del st.session_state['optimized_content']
                        if 'optimization_report' in st.session_state:
                            del st.session_state['optimization_report']
                        if 'optimization_done' in st.session_state:
                            del st.session_state['optimization_done']
                        if 'applied_content' in st.session_state:
                            del st.session_state['applied_content']
                        if 'optimization_applied' in st.session_state:
                            del st.session_state['optimization_applied']
                        st.success("✅ Reset to original template!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error resetting: {str(e)}")
            
            # Cover Letter Generation Section
            st.markdown("---")
            st.markdown("### ✉️ Generate Cover Letter")
            
            st.info("💡 Generate an AI-powered cover letter tailored to this job description")
            
            if st.button("📝 Generate Cover Letter", use_container_width=True, type="primary", key="gen_cover_letter_btn"):
                with st.spinner("Generating cover letter with AI (5 paragraphs, <60 words each)..."):
                    try:
                        # Get job description from session
                        job_description = st.session_state.get('last_job_description', '')
                        
                        if not job_description:
                            st.error("❌ No job description found. Please re-run optimization with a job description.")
                        else:
                            # Import cover letter generator
                            from cover_letter_generator import CoverLetterGenerator
                            
                            # Get optimized content as context
                            if 'applied_content' in st.session_state:
                                resume_content = st.session_state['applied_content']
                            elif 'optimized_content' in st.session_state:
                                resume_content = st.session_state['optimized_content']
                            else:
                                resume_content = resume_data
                            
                            # Create resume text summary for context
                            resume_text = f"""
                            Skills: {resume_content.get('skills', {}).get('languages', {}).get('value', '')}, 
                            {resume_content.get('skills', {}).get('software', {}).get('value', '')}
                            """
                            if resume_content.get('professional'):
                                resume_text += f"\nExperience: {resume_content['professional'][0].get('position', '')}"
                            
                            # Initialize cover letter generator with same API key as optimizer
                            try:
                                api_key = st.secrets["GEMINI_API_KEY"]
                            except Exception:
                                st.error("❌ GEMINI_API_KEY not found in secrets.toml")
                                raise
                            
                            generator = CoverLetterGenerator(api_key=api_key)
                            
                            # Generate cover letter
                            st.info("🤖 AI is writing your cover letter (5 paragraphs)...")
                            doc, company_name = generator.create_cover_letter_docx(
                                job_description=job_description,
                                resume_text=resume_text,
                                context="Passionate about technology and eager to contribute to innovative projects",
                                applicant_name="Dilip Kumar Thirukonda Chandrasekaran",
                                applicant_email="dthirukondac@binghamton.edu",
                                applicant_phone="(607) 624-9390"
                            )
                            
                            # Save to temp file to get bytes
                            timestamp_cl = datetime.now().strftime("%Y%m%d_%H%M%S")
                            import tempfile
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                                temp_path_cl = tmp_file.name
                            
                            doc.save(temp_path_cl)
                            
                            with open(temp_path_cl, "rb") as f:
                                cover_letter_bytes = f.read()
                            
                            # Clean up
                            try:
                                Path(temp_path_cl).unlink()
                            except:
                                pass
                            
                            # Store in session
                            st.session_state['last_cover_letter'] = cover_letter_bytes
                            st.session_state['last_cover_letter_timestamp'] = timestamp_cl
                            st.session_state['cover_letter_company'] = company_name
                            
                            st.success(f"✅ Cover letter generated for: **{company_name or 'Hiring Manager'}**")
                            
                    except Exception as e:
                        st.error(f"❌ Error generating cover letter: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
            
            # Show download buttons if cover letter exists
            if 'last_cover_letter' in st.session_state:
                col_cl1, col_cl2 = st.columns(2)
                
                with col_cl1:
                    # Download cover letter only
                    st.download_button(
                        label="⬇️ Download Cover Letter",
                        data=st.session_state['last_cover_letter'],
                        file_name=f"cover_letter_dilip_kumar_{st.session_state['last_cover_letter_timestamp']}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                        key="download_cover_letter"
                    )
                
                with col_cl2:
                    # Download both resume and cover letter as ZIP
                    if 'last_generated_resume' in st.session_state:
                        import zipfile
                        from io import BytesIO
                        
                        # Create ZIP file in memory
                        zip_buffer = BytesIO()
                        resume_ts = st.session_state.get('last_resume_timestamp', datetime.now().strftime("%Y%m%d_%H%M%S"))
                        cover_ts = st.session_state.get('last_cover_letter_timestamp', datetime.now().strftime("%Y%m%d_%H%M%S"))
                        
                        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                            # Add resume
                            zip_file.writestr(
                                f"resume_dilip_kumar_tc_{resume_ts}.docx",
                                st.session_state['last_generated_resume']
                            )
                            # Add cover letter
                            zip_file.writestr(
                                f"cover_letter_dilip_kumar_{cover_ts}.docx",
                                st.session_state['last_cover_letter']
                            )
                        
                        st.download_button(
                            label="📦 Download Both (ZIP)",
                            data=zip_buffer.getvalue(),
                            file_name=f"application_package_{cover_ts}.zip",
                            mime="application/zip",
                            use_container_width=True,
                            key="download_both_zip"
                        )
                    else:
                        st.info("💡 Generate resume first, then download both together")
            
            # Save optimized content
            st.markdown("---")
            st.markdown("### 💾 Apply Changes to Resume")
            
            # Info box for warnings
            if warnings and not violations:
                st.info("💡 **Note:** You can still download the resume with warnings, but consider reviewing the highlighted fields.")
            
            col1, col2 = st.columns(2)
            with col1:
                # Show warning if there are violations, but allow apply
                if st.button("✅ Apply Optimization", type="primary", use_container_width=True):
                    # Try to save to file (works locally, fails gracefully on Streamlit Cloud)
                    file_saved = False
                    try:
                        with open(RESUME_CONTENT_JSON, 'w', encoding='utf-8') as f:
                            json.dump(optimized_content, f, indent=2, ensure_ascii=False)
                        file_saved = True
                        load_resume_content.clear()  # Clear cache only if file write succeeded
                    except (OSError, IOError, PermissionError) as e:
                        # Streamlit Cloud has read-only filesystem - this is expected
                        print(f"[INFO] Could not write to file (read-only filesystem on cloud): {e}")
                    
                    # CRITICAL: Save optimized content to persistent session state
                    # This ensures it's available for PDF generation even on cloud
                    st.session_state['applied_content'] = optimized_content
                    
                    # Show appropriate success message
                    if file_saved:
                        st.success("✅ Resume content saved locally and ready for PDF generation!")
                    else:
                        st.success("✅ Resume content ready for PDF generation! (Cloud mode - using session storage)")
                    
                    # Keep optimization results visible but mark as applied
                    st.session_state['optimization_applied'] = True
                    
                    st.info("💡 **Success!** Use 'Regenerate Resume PDF' button above to download your optimized resume.")
                    # Note: Removed st.rerun() so results stay visible
                
                if violations:
                    st.caption("⚠️ Warning: Character limit violations detected - proceed with caution")
            
            with col2:
                if st.button("❌ Discard Changes", use_container_width=True):
                    # Clear all optimization-related session state
                    if 'optimization_done' in st.session_state:
                        del st.session_state['optimization_done']
                    if 'optimized_content' in st.session_state:
                        del st.session_state['optimized_content']
                    if 'optimization_report' in st.session_state:
                        del st.session_state['optimization_report']
                    if 'applied_content' in st.session_state:
                        del st.session_state['applied_content']
                    if 'optimization_applied' in st.session_state:
                        del st.session_state['optimization_applied']
                    st.info("✅ Changes discarded - original resume unchanged")
                    st.rerun()

# B. SKILLS TAB
with tab_skills:
    st.header("🔧 Skills Section")
    st.info("Priority B: Edit your technical skills")
    
    skills_data = resume_data.get("skills", {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        if "languages" in skills_data:
            lang_data = skills_data["languages"]
            prefix = f"{lang_data.get('label', 'Languages')}: "
            
            languages = st.text_area(
                "Programming Languages",
                value=lang_data.get("value", ""),
                height=80,
                key="languages",
                help="Comma-separated list of programming languages"
            )
            show_char_counter(prefix, languages, "languages")
            
            edited_data["skills"]["languages"] = {
                "value": languages,
                "label": lang_data.get("label", "Languages"),
                "paragraph_index": lang_data.get("paragraph_index")
            }
        
        if "software" in skills_data:
            sw_data = skills_data["software"]
            prefix = f"{sw_data.get('label', 'Software')}: "
            
            software = st.text_area(
                "Software & Frameworks",
                value=sw_data.get("value", ""),
                height=80,
                key="software",
                help="Comma-separated list of software and frameworks"
            )
            show_char_counter(prefix, software, "software")
            
            edited_data["skills"]["software"] = {
                "value": software,
                "label": sw_data.get("label", "Software"),
                "paragraph_index": sw_data.get("paragraph_index")
            }
    
    with col2:
        if "tools" in skills_data:
            tools_data = skills_data["tools"]
            prefix = f"{tools_data.get('label', 'Tools')}: "
            
            tools = st.text_area(
                "Tools & Technologies",
                value=tools_data.get("value", ""),
                height=80,
                key="tools",
                help="Comma-separated list of tools and technologies"
            )
            show_char_counter(prefix, tools, "tools")
            
            edited_data["skills"]["tools"] = {
                "value": tools,
                "label": tools_data.get("label", "Tools"),
                "paragraph_index": tools_data.get("paragraph_index")
            }
        
        if "databases" in skills_data:
            db_data = skills_data["databases"]
            prefix = f"{db_data.get('label', 'Databases')}: "
            
            databases = st.text_area(
                "Databases",
                value=db_data.get("value", ""),
                height=80,
                key="databases",
                help="Comma-separated list of databases"
            )
            show_char_counter(prefix, databases, "databases")
            
            edited_data["skills"]["databases"] = {
                "value": databases,
                "label": db_data.get("label", "Databases"),
                "paragraph_index": db_data.get("paragraph_index")
            }

# B. PROJECTS TAB
with tab_projects:
    st.header("💼 Projects Section")
    st.info("Priority B: Edit your project experience")
    
    projects_data = resume_data.get("projects", [])
    
    for idx, project in enumerate(projects_data):
        with st.expander(f"Project {idx + 1}", expanded=(idx == 0)):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                proj_name = st.text_input(
                    "Project Name",
                    value=project.get("name", ""),
                    key=f"proj_{idx}_name",
                    help="Full project name"
                )
                show_char_counter("", proj_name, f"proj_{idx}_name")
            
            with col2:
                proj_role = st.text_input(
                    "Role/Team",
                    value=project.get("role", ""),
                    key=f"proj_{idx}_role",
                    help="e.g., Team Project, Personal Project"
                )
                show_char_counter("", proj_role, f"proj_{idx}_role")
            
            with col3:
                proj_dates = st.text_input(
                    "Dates",
                    value=project.get("dates", ""),
                    key=f"proj_{idx}_dates",
                    help="e.g., January 2019 - February 2019"
                )
                show_char_counter("", proj_dates, f"proj_{idx}_dates")
            
            # Store edited data
            edited_proj = {
                "name": proj_name,
                "role": proj_role,
                "dates": proj_dates,
                "header_line": project.get("header_line")
            }
            
            # Tech stack
            if "tech_stack" in project and project["tech_stack"]:
                tech = project["tech_stack"]
                tech_value = st.text_input(
                    "Tech Stack",
                    value=tech.get("value", ""),
                    key=f"proj_{idx}_tech",
                    help="Technologies used in this project"
                )
                show_char_counter("", tech_value, f"proj_{idx}_tech")
                
                edited_proj["tech_stack"] = {
                    "value": tech_value,
                    "paragraph_index": tech.get("paragraph_index")
                }
            
            # Bullets
            bullets = project.get("bullets", [])
            edited_bullets = []
            
            for bidx, bullet in enumerate(bullets):
                original_bullet = bullet.get("value", "")
                bullet_text = st.text_area(
                    f"Bullet {bidx + 1}",
                    value=original_bullet,
                    height=80,
                    key=f"proj_{idx}_bullet_{bidx}",
                    help="Project achievement or responsibility"
                )
                show_char_counter("• ", bullet_text, f"proj_{idx}_bullet_{bidx}", original_bullet)
                
                edited_bullets.append({
                    "value": bullet_text,
                    "paragraph_index": bullet.get("paragraph_index")
                })
            
            edited_proj["bullets"] = edited_bullets
            edited_data["projects"].append(edited_proj)

# C. LEADERSHIP TAB
with tab_leadership:
    st.header("👥 Leadership Section")
    st.info("Priority C: Edit leadership experience")
    
    leadership_data = resume_data.get("leadership", [])
    
    for idx, lead in enumerate(leadership_data):
        with st.expander(f"Leadership {idx + 1}", expanded=(idx == 0)):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                org = st.text_input(
                    "Organization",
                    value=lead.get("organization", ""),
                    key=f"lead_{idx}_org",
                    help="Organization or club name"
                )
                show_char_counter("", org, f"lead_{idx}_org")
            
            with col2:
                title = st.text_input(
                    "Title",
                    value=lead.get("title", ""),
                    key=f"lead_{idx}_title",
                    help="Your role or position"
                )
                show_char_counter("", title, f"lead_{idx}_title")
            
            with col3:
                dates = st.text_input(
                    "Dates",
                    value=lead.get("dates", ""),
                    key=f"lead_{idx}_dates",
                    help="Time period"
                )
                show_char_counter("", dates, f"lead_{idx}_dates")
            
            edited_lead = {
                "organization": org,
                "title": title,
                "dates": dates,
                "header_line": lead.get("header_line")
            }
            
            # Bullets
            bullets = lead.get("bullets", [])
            edited_bullets = []
            
            for bidx, bullet in enumerate(bullets):
                original_bullet_text = bullet.get("value", "")
                bullet_text = st.text_area(
                    f"Bullet {bidx + 1}",
                    value=original_bullet_text,
                    height=80,
                    key=f"lead_{idx}_bullet_{bidx}",
                    help="Leadership achievement or activity"
                )
                show_char_counter("• ", bullet_text, f"lead_{idx}_bullet_{bidx}", original_bullet_text)
                
                edited_bullets.append({
                    "value": bullet_text,
                    "paragraph_index": bullet.get("paragraph_index")
                })
            
            edited_lead["bullets"] = edited_bullets
            edited_data["leadership"].append(edited_lead)

# D. PROFESSIONAL TAB
with tab_professional:
    st.header("🏢 Professional Experience")
    st.info("Priority D: Edit work experience")
    
    prof_data = resume_data.get("professional", [])
    
    for idx, job in enumerate(prof_data):
        with st.expander(f"Job {idx + 1}", expanded=(idx == 0)):
            col1, col2 = st.columns(2)
            
            with col1:
                company = st.text_input(
                    "Company",
                    value=job.get("company", ""),
                    key=f"job_{idx}_company",
                    help="Company name"
                )
                show_char_counter("", company, f"job_{idx}_company")
                
                job_title = st.text_input(
                    "Job Title",
                    value=job.get("role", ""),
                    key=f"job_{idx}_title",
                    help="Your job title/role"
                )
                show_char_counter("", job_title, f"job_{idx}_title")
            
            with col2:
                location = st.text_input(
                    "Location",
                    value=job.get("location", ""),
                    key=f"job_{idx}_location",
                    help="City, State or Country"
                )
                show_char_counter("", location, f"job_{idx}_location")
                
                job_dates = st.text_input(
                    "Dates",
                    value=job.get("dates", ""),
                    key=f"job_{idx}_dates",
                    help="Employment period"
                )
                show_char_counter("", job_dates, f"job_{idx}_dates")
            
            edited_job = {
                "company": company,
                "role": job_title,
                "location": location,
                "dates": job_dates,
                "header_line": job.get("header_line")
            }
            
            # Tech stack
            if "tech_stack" in job and job["tech_stack"]:
                tech = job["tech_stack"]
                tech_value = st.text_input(
                    "Tech Stack",
                    value=tech.get("value", ""),
                    key=f"job_{idx}_tech",
                    help="Technologies used at this job"
                )
                show_char_counter("", tech_value, f"job_{idx}_tech")
                
                edited_job["tech_stack"] = {
                    "value": tech_value,
                    "paragraph_index": tech.get("paragraph_index")
                }
            
            # Bullets
            bullets = job.get("bullets", [])
            edited_bullets = []
            
            for bidx, bullet in enumerate(bullets):
                original_bullet_text = bullet.get("value", "")
                bullet_text = st.text_area(
                    f"Bullet {bidx + 1}",
                    value=original_bullet_text,
                    height=80,
                    key=f"job_{idx}_bullet_{bidx}",
                    help="Job duty or achievement"
                )
                show_char_counter("• ", bullet_text, f"job_{idx}_bullet_{bidx}", original_bullet_text)
                
                edited_bullets.append({
                    "value": bullet_text,
                    "paragraph_index": bullet.get("paragraph_index")
                })
            
            edited_job["bullets"] = edited_bullets
            edited_data["professional"].append(edited_job)

# E. EDUCATION TAB
with tab_education:
    st.header("🎓 Education Section")
    st.info("Priority E: Edit education details")
    
    edu_data = resume_data.get("education", [])
    
    for idx, edu in enumerate(edu_data):
        with st.expander(f"Education {idx + 1}", expanded=(idx == 0)):
            col1, col2 = st.columns(2)
            
            with col1:
                university = st.text_input(
                    "University",
                    value=edu.get("university", ""),
                    key=f"edu_{idx}_univ",
                    help="University name and location"
                )
                show_char_counter("", university, f"edu_{idx}_univ")
                
                degree = st.text_input(
                    "Degree",
                    value=edu.get("degree", ""),
                    key=f"edu_{idx}_degree",
                    help="Degree title and major"
                )
                show_char_counter("", degree, f"edu_{idx}_degree")
                
                edu_dates = st.text_input(
                    "Dates",
                    value=edu.get("dates", ""),
                    key=f"edu_{idx}_dates",
                    help="Graduation date or time period"
                )
                show_char_counter("", edu_dates, f"edu_{idx}_dates")
            
            with col2:
                gpa_value = st.text_input(
                    "GPA",
                    value=edu.get("gpa", ""),
                    key=f"edu_{idx}_gpa",
                    help="GPA score (e.g., 3.67/4.00)"
                )
                show_char_counter("Cumulative GPA: ", gpa_value, f"edu_{idx}_gpa")
                
                coursework_str = "\n".join(edu.get("coursework", []))
                coursework_value = st.text_area(
                    "Coursework",
                    value=coursework_str,
                    height=100,
                    key=f"edu_{idx}_coursework",
                    help="Relevant courses, comma-separated"
                )
                show_char_counter("Relevant Coursework: ", coursework_value, f"edu_{idx}_coursework")
            
            edited_edu = {
                "university": university,
                "degree": degree,
                "dates": edu_dates,
                "gpa": gpa_value,
                "coursework": coursework_value.split("\n") if coursework_value else [],
                "institution_line": edu.get("institution_line"),
                "gpa_paragraph_index": edu.get("gpa_paragraph_index"),
                "coursework_paragraph_indices": edu.get("coursework_paragraph_indices", [])
            }
            
            edited_data["education"].append(edited_edu)

# F. PERSONAL TAB
with tab_personal:
    st.header("👤 Personal Information")
    st.info("Priority F: Edit name and contact")
    
    personal_data = resume_data.get("personal", {})
    
    # Name
    if "name" in personal_data:
        name_data = personal_data["name"]
        name = st.text_input(
            "Full Name",
            value=name_data.get("value", ""),
            key="name",
            help="Your full name as it appears on resume"
        )
        show_char_counter("", name, "name")
        
        edited_data["personal"]["name"] = {
            "value": name,
            "paragraph_index": name_data.get("paragraph_index")
        }
    
    # Contact line
    if "contact_line" in personal_data:
        contact_data = personal_data["contact_line"]
        parts = contact_data.get("parts", {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            location = st.text_input("Location", value=parts.get("location", ""), key="location", help="City, State")
            show_char_counter("", location, "location")
            
            phone = st.text_input("Phone", value=parts.get("phone", ""), key="phone", help="Phone number")
            show_char_counter("", phone, "phone")
            
            email = st.text_input("Email", value=parts.get("email", ""), key="email", help="Email address")
            show_char_counter("", email, "email")
        
        with col2:
            linkedin = st.text_input("LinkedIn", value=parts.get("linkedin", ""), key="linkedin", help="LinkedIn URL or username")
            show_char_counter("", linkedin, "linkedin")
            
            portfolio = st.text_input("Portfolio", value=parts.get("portfolio", ""), key="portfolio", help="Portfolio URL")
            show_char_counter("", portfolio, "portfolio")
        
        edited_data["personal"]["contact_line"] = {
            "paragraph_index": contact_data.get("paragraph_index"),
            "parts": {
                "location": location,
                "phone": phone,
                "email": email,
                "linkedin": linkedin,
                "portfolio": portfolio
            }
        }

# Generate button
st.markdown("---")
col1, col2, col3 = st.columns([2, 1, 2])

with col2:
    if st.button("🚀 Generate Resume", type="primary", use_container_width=True):
        with st.spinner("Generating resume with enhanced format preservation..."):
            try:
                # Generate timestamp for unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Priority: Use applied AI optimization if available, else reload from file
                # This ensures AI optimizations work on Streamlit Cloud (read-only filesystem)
                if 'applied_content' in st.session_state:
                    current_resume_data = st.session_state['applied_content']
                    source = "applied_content (AI optimized)"
                else:
                    # Reload resume_content.json to get latest changes
                    with open(RESUME_CONTENT_JSON, 'r', encoding='utf-8') as f:
                        current_resume_data = json.load(f)
                    source = "file (manual edits)"
                
                print(f"[GENERATE] Source: {source}")
                st.info(f"📝 Using content from: **{source}**")
                
                # CRITICAL FIX: If AI optimization was applied, use it directly
                # Don't merge with edited_data from tabs (tabs show old cached values)
                # User can refresh page after Apply to see optimized values in tabs
                if 'applied_content' in st.session_state:
                    final_data = current_resume_data  # Use AI-optimized content directly
                    print("[GENERATE] Using AI-optimized content WITHOUT tab merge (tabs show old cached data)")
                else:
                    # Merge with edited_data from tabs (only when no AI optimization)
                    final_data = current_resume_data.copy()
                    
                    # Merge edited data from tabs if any fields were edited
                    if edited_data.get("personal"):
                        final_data["personal"] = edited_data["personal"]
                    if edited_data.get("education"):
                        final_data["education"] = edited_data["education"]
                    if edited_data.get("skills"):
                        final_data["skills"] = edited_data["skills"]
                    if edited_data.get("professional"):
                        final_data["professional"] = edited_data["professional"]
                    if edited_data.get("projects"):
                        final_data["projects"] = edited_data["projects"]
                    if edited_data.get("leadership"):
                        final_data["leadership"] = edited_data["leadership"]
                    
                    print("[GENERATE] Using file content WITH tab edits merged")
                
                # Create temp file for generation
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                    temp_path = tmp_file.name
                
                # Build resume
                builder = EnhancedFormatBuilder(ORIGINAL_RESUME, FORMAT_METADATA_JSON)
                result = builder.build_resume_from_json(final_data, temp_path)
                
                # Read the generated file into memory
                with open(result, "rb") as f:
                    resume_bytes = f.read()
                
                # Clean up temp file
                try:
                    Path(temp_path).unlink()
                except:
                    pass
                
                # Success
                st.success(f"✅ Resume generated successfully!")
                
                # Download button with in-memory data
                st.download_button(
                    label="⬇️ Download Resume",
                    data=resume_bytes,
                    file_name=f"resume_dilip_kumar_tc_{timestamp}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                    key=f"download_resume_{timestamp}"
                )
                
            except Exception as e:
                st.error(f"❌ Error generating resume: {str(e)}")
                st.exception(e)

# Footer
st.markdown("---")
st.caption("📄 Enhanced Resume Builder v2.0 | Complete format preservation with metadata system")
