"""
Enhanced Resume Builder with Complete Format Preservation
Uses metadata-based format preservation for exact replication.
"""

import streamlit as st
import json
from pathlib import Path
from enhanced_format_system import EnhancedFormatBuilder
from datetime import datetime

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
            languages = st.text_area(
                "Programming Languages",
                value=lang_data.get("value", ""),
                height=80,
                key="languages"
            )
            edited_data["skills"]["languages"] = {
                "value": languages,
                "label": lang_data.get("label", "Languages"),
                "paragraph_index": lang_data.get("paragraph_index")
            }
        
        if "software" in skills_data:
            sw_data = skills_data["software"]
            software = st.text_area(
                "Software & Frameworks",
                value=sw_data.get("value", ""),
                height=80,
                key="software"
            )
            edited_data["skills"]["software"] = {
                "value": software,
                "label": sw_data.get("label", "Software"),
                "paragraph_index": sw_data.get("paragraph_index")
            }
    
    with col2:
        if "tools" in skills_data:
            tools_data = skills_data["tools"]
            tools = st.text_area(
                "Tools & Technologies",
                value=tools_data.get("value", ""),
                height=80,
                key="tools"
            )
            edited_data["skills"]["tools"] = {
                "value": tools,
                "label": tools_data.get("label", "Tools"),
                "paragraph_index": tools_data.get("paragraph_index")
            }
        
        if "databases" in skills_data:
            db_data = skills_data["databases"]
            databases = st.text_area(
                "Databases",
                value=db_data.get("value", ""),
                height=80,
                key="databases"
            )
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
                    key=f"proj_{idx}_name"
                )
            
            with col2:
                proj_role = st.text_input(
                    "Role/Team",
                    value=project.get("role", ""),
                    key=f"proj_{idx}_role"
                )
            
            with col3:
                proj_dates = st.text_input(
                    "Dates",
                    value=project.get("dates", ""),
                    key=f"proj_{idx}_dates"
                )
            
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
                    key=f"proj_{idx}_tech"
                )
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
                    key=f"proj_{idx}_bullet_{bidx}"
                )
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
                    key=f"lead_{idx}_org"
                )
            
            with col2:
                title = st.text_input(
                    "Title",
                    value=lead.get("title", ""),
                    key=f"lead_{idx}_title"
                )
            
            with col3:
                dates = st.text_input(
                    "Dates",
                    value=lead.get("dates", ""),
                    key=f"lead_{idx}_dates"
                )
            
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
                    key=f"lead_{idx}_bullet_{bidx}"
                )
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
                    key=f"job_{idx}_company"
                )
                job_title = st.text_input(
                    "Job Title",
                    value=job.get("role", ""),
                    key=f"job_{idx}_title"
                )
            
            with col2:
                location = st.text_input(
                    "Location",
                    value=job.get("location", ""),
                    key=f"job_{idx}_location"
                )
                job_dates = st.text_input(
                    "Dates",
                    value=job.get("dates", ""),
                    key=f"job_{idx}_dates"
                )
            
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
                    key=f"job_{idx}_tech"
                )
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
                    key=f"job_{idx}_bullet_{bidx}"
                )
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
                    key=f"edu_{idx}_univ"
                )
                
                degree = st.text_input(
                    "Degree",
                    value=edu.get("degree", ""),
                    key=f"edu_{idx}_degree"
                )
                
                edu_dates = st.text_input(
                    "Dates",
                    value=edu.get("dates", ""),
                    key=f"edu_{idx}_dates"
                )
            
            with col2:
                gpa_value = st.text_input(
                    "GPA",
                    value=edu.get("gpa", ""),
                    key=f"edu_{idx}_gpa"
                )
                
                coursework_str = "\n".join(edu.get("coursework", []))
                coursework_value = st.text_area(
                    "Coursework",
                    value=coursework_str,
                    height=100,
                    key=f"edu_{idx}_coursework"
                )
            
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
            key="name"
        )
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
            location = st.text_input("Location", value=parts.get("location", ""), key="location")
            phone = st.text_input("Phone", value=parts.get("phone", ""), key="phone")
            email = st.text_input("Email", value=parts.get("email", ""), key="email")
        
        with col2:
            linkedin = st.text_input("LinkedIn", value=parts.get("linkedin", ""), key="linkedin")
            portfolio = st.text_input("Portfolio", value=parts.get("portfolio", ""), key="portfolio")
        
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
