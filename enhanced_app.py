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

# Page config
st.set_page_config(page_title="Resume Builder - Enhanced Format", layout="wide", page_icon="📄")

# Paths
RESUME_CONTENT_JSON = "templates/resume_content.json"
FORMAT_METADATA_JSON = "metadata/format_metadata.json"
ORIGINAL_RESUME = r"C:\Users\dilip\OneDrive\Desktop\ResumeBuilder\reference_docx\resume_optimized_final.docx"

# Load resume content (with file modification time for cache invalidation)
@st.cache_data
def load_resume_content(file_mtime):
    with open(RESUME_CONTENT_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

try:
    # Force reload if file changed
    file_mtime = Path(RESUME_CONTENT_JSON).stat().st_mtime
    resume_data = load_resume_content(file_mtime)
except FileNotFoundError:
    st.error(f"❌ Resume content not found: {RESUME_CONTENT_JSON}")
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
def show_char_counter(prefix, current_text, field_key):
    """Display adaptive character counter with visual feedback."""
    if char_limiter is None:
        return
    
    info = char_limiter.get_adaptive_limit(prefix, current_text)
    
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
    
    # Add efficiency badge if applicable
    if info['efficiency_gain'] > 0:
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

# Priority tabs
tab_skills, tab_projects, tab_leadership, tab_professional, tab_education, tab_personal = st.tabs([
    "🔧 A. Skills",
    "💼 B. Projects",
    "👥 C. Leadership",
    "🏢 D. Professional",
    "🎓 E. Education",
    "👤 F. Personal"
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

# A. SKILLS TAB
with tab_skills:
    st.header("🔧 Skills Section")
    st.info("Priority A: Edit your technical skills")
    
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
                bullet_text = st.text_area(
                    f"Bullet {bidx + 1}",
                    value=bullet.get("value", ""),
                    height=80,
                    key=f"proj_{idx}_bullet_{bidx}",
                    help="Project achievement or responsibility"
                )
                show_char_counter("• ", bullet_text, f"proj_{idx}_bullet_{bidx}")
                
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
                bullet_text = st.text_area(
                    f"Bullet {bidx + 1}",
                    value=bullet.get("value", ""),
                    height=80,
                    key=f"lead_{idx}_bullet_{bidx}",
                    help="Leadership achievement or activity"
                )
                show_char_counter("• ", bullet_text, f"lead_{idx}_bullet_{bidx}")
                
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
                bullet_text = st.text_area(
                    f"Bullet {bidx + 1}",
                    value=bullet.get("value", ""),
                    height=80,
                    key=f"job_{idx}_bullet_{bidx}",
                    help="Job duty or achievement"
                )
                show_char_counter("• ", bullet_text, f"job_{idx}_bullet_{bidx}")
                
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
                # Create output directory
                output_dir = Path("output/generated_resumes")
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Generate filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = output_dir / f"resume_{timestamp}.docx"
                
                # Build resume
                builder = EnhancedFormatBuilder(ORIGINAL_RESUME, FORMAT_METADATA_JSON)
                result = builder.build_resume_from_json(edited_data, str(output_file))
                
                # Success
                st.success(f"✅ Resume generated successfully!")
                st.info(f"📁 **Saved to:** `{result}`")
                
                # Download button
                with open(result, 'rb') as f:
                    st.download_button(
                        label="⬇️ Download Resume",
                        data=f,
                        file_name=f"resume_{timestamp}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
                
            except Exception as e:
                st.error(f"❌ Error generating resume: {str(e)}")
                st.exception(e)

# Footer
st.markdown("---")
st.caption("📄 Enhanced Resume Builder v2.0 | Complete format preservation with metadata system")
