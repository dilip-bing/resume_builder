"""
FastAPI Server for Resume Optimization API
Provides REST API endpoint for automated resume generation with job description
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Header, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Optional
import uvicorn
import tempfile
import json
from pathlib import Path
from datetime import datetime
import os
import secrets

# Import existing resume builder components
from gemini_optimizer import GeminiATSOptimizer
from enhanced_format_system import EnhancedFormatBuilder
from cover_letter_generator import CoverLetterGenerator

# Initialize FastAPI app
app = FastAPI(
    title="Resume Optimizer API",
    description="AI-powered resume optimization API for ATS (Applicant Tracking Systems)",
    version="1.0.0"
)

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# API Key for authentication (set this as environment variable)
API_SECRET_KEY = os.getenv("API_SECRET_KEY")

# If not in environment, try to load from .streamlit/secrets.toml
if not GEMINI_API_KEY or not API_SECRET_KEY:
    try:
        import toml
        secrets_path = ".streamlit/secrets.toml"
        if os.path.exists(secrets_path):
            secrets_data = toml.load(secrets_path)
            if not GEMINI_API_KEY:
                GEMINI_API_KEY = secrets_data.get("GEMINI_API_KEY")
                if GEMINI_API_KEY:
                    print(f"[INFO] Loaded GEMINI_API_KEY from {secrets_path}")
            if not API_SECRET_KEY:
                API_SECRET_KEY = secrets_data.get("API_SECRET_KEY")
                if API_SECRET_KEY:
                    print(f"[INFO] Loaded API_SECRET_KEY from {secrets_path}")
    except Exception as e:
        print(f"[WARNING] Could not load from secrets.toml: {e}")

# Generate a random API key if not set (for local development)
if not API_SECRET_KEY:
    API_SECRET_KEY = secrets.token_urlsafe(32)
    print(f"\n{'='*70}")
    print("⚠️  WARNING: API_SECRET_KEY not set!")
    print("="*70)
    print(f"Using temporary key: {API_SECRET_KEY}")
    print("\nFor production, set API_SECRET_KEY environment variable:")
    print("  export API_SECRET_KEY='your-secret-key-here'")
    print("="*70 + "\n")

RESUME_CONTENT_TEMPLATE = "templates/resume_content_template.json"
FORMAT_METADATA_JSON = "metadata/format_metadata.json"
ORIGINAL_RESUME = "reference_docx/resume_optimized_final.docx"

# API Key security
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Depends(api_key_header)):
    """
    Verify API key for authentication
    
    Args:
        api_key: API key from X-API-Key header
    
    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Include 'X-API-Key' header with your request."
        )
    
    if api_key != API_SECRET_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key. Access denied."
        )
    
    return api_key

# Request/Response models
class OptimizeRequest(BaseModel):
    job_description: str
    return_format: str = "file"  # "file" or "base64"
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_description": "We are looking for a Senior Software Engineer with experience in Python, React, AWS...",
                "return_format": "file"
            }
        }

class CoverLetterRequest(BaseModel):
    job_description: str
    resume_text: str = ""  # Optimized resume content for additional context (optional)
    context: str = ""  # Additional context like career passion areas (optional)
    return_format: str = "file"  # "file" or "base64"
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_description": "We are looking for a Senior Software Engineer with experience in Python, React, AWS...",
                "resume_text": "Experienced Software Engineer with 3+ years...",
                "context": "Passionate about cloud infrastructure and DevOps",
                "return_format": "file"
            }
        }

class OptimizeResponse(BaseModel):
    status: str
    message: str
    download_url: Optional[str] = None
    filename: Optional[str] = None
    match_score: Optional[str] = None
    keywords_added: Optional[int] = None
    resume_base64: Optional[str] = None

class CoverLetterResponse(BaseModel):
    status: str
    message: str
    download_url: Optional[str] = None
    filename: str
    company_name: Optional[str] = None
    cover_letter_base64: Optional[str] = None  # Only present if return_format="base64"

# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Resume Optimizer API",
        "version": "1.0.0",
        "endpoints": {
            "optimize": "POST /api/v1/optimize",
            "health": "GET /health"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    checks = {
        "api_key_configured": GEMINI_API_KEY is not None and GEMINI_API_KEY != "",
        "secret_key_configured": API_SECRET_KEY is not None and API_SECRET_KEY != "",
        "template_exists": Path(RESUME_CONTENT_TEMPLATE).exists(),
        "metadata_exists": Path(FORMAT_METADATA_JSON).exists(),
        "original_resume_exists": Path(ORIGINAL_RESUME).exists()
    }
    
    all_healthy = all(checks.values())
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "checks": checks,
        "timestamp": datetime.now().isoformat(),
        "authentication": "enabled" if API_SECRET_KEY else "disabled"
    }

@app.post("/api/v1/optimize", response_model=OptimizeResponse)
async def optimize_resume(request: OptimizeRequest, api_key: str = Depends(verify_api_key)):
    """
    Optimize resume for a specific job description
    
    **Authentication:** Requires X-API-Key header
    
    **Parameters:**
    - job_description: Full text of the job posting
    - return_format: "file" (download link) or "base64" (embedded in response)
    
    **Returns:**
    - status: "success" or "error"
    - message: Human-readable message
    - download_url: URL to download the resume (if return_format="file")
    - filename: Generated filename
    - match_score: Estimated ATS match percentage
    - keywords_added: Number of keywords added during optimization
    - resume_base64: Base64-encoded resume file (if return_format="base64")
    """
    
    try:
        print(f"\n[API] Received optimization request")
        print(f"[API] Job description length: {len(request.job_description)} characters")
        
        # Validate API key
        if not GEMINI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY not configured. Set environment variable GEMINI_API_KEY."
            )
        
        # Load template
        print(f"[API] Loading template from: {RESUME_CONTENT_TEMPLATE}")
        with open(RESUME_CONTENT_TEMPLATE, 'r', encoding='utf-8') as f:
            resume_content = json.load(f)
        
        # Initialize optimizer
        print(f"[API] Initializing Gemini optimizer...")
        optimizer = GeminiATSOptimizer(GEMINI_API_KEY)
        
        # Optimize resume
        print(f"[API] Starting AI optimization...")
        optimized_content, report = optimizer.optimize_resume(
            request.job_description,
            resume_content
        )
        
        print(f"[API] Optimization complete!")
        print(f"[API] Match score: {report.get('match_score_estimate', 'N/A')}")
        print(f"[API] Keywords added: {len(report.get('keywords_added', []))}")
        
        # Check for character limit violations
        validation = report.get('char_limit_validation', {})
        violations = validation.get('violations', [])
        if violations:
            print(f"[API] WARNING: {len(violations)} character limit violations detected")
            # Still proceed but include warning in response
        
        # Generate resume document
        print(f"[API] Generating resume document...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_base = f"resume_dilip_kumar_tc_{timestamp}"
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            temp_path = tmp_file.name
        
        # Build resume
        builder = EnhancedFormatBuilder(ORIGINAL_RESUME, FORMAT_METADATA_JSON)
        result_path = builder.build_resume_from_json(optimized_content, temp_path)
        
        print(f"[API] Resume generated: {result_path}")
        
        # Prepare response based on return format
        if request.return_format == "base64":
            # Return base64-encoded file
            import base64
            with open(result_path, "rb") as f:
                resume_bytes = f.read()
            resume_base64 = base64.b64encode(resume_bytes).decode('utf-8')
            
            # Clean up temp file
            try:
                Path(temp_path).unlink()
            except:
                pass
            
            return OptimizeResponse(
                status="success",
                message="Resume optimized successfully",
                filename=f"{filename_base}.docx",
                match_score=report.get('match_score_estimate', 'Unknown'),
                keywords_added=len(report.get('keywords_added', [])),
                resume_base64=resume_base64
            )
        
        else:  # return_format == "file"
            # Save to output directory for download
            output_dir = Path("output/api_generated")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = output_dir / f"{filename_base}.docx"
            
            # Copy from temp to output
            import shutil
            shutil.copy2(temp_path, output_file)
            
            # Clean up temp file
            try:
                Path(temp_path).unlink()
            except:
                pass
            
            # Return file path for download
            return OptimizeResponse(
                status="success",
                message="Resume optimized successfully",
                download_url=f"/api/v1/download/{output_file.name}",
                filename=output_file.name,
                match_score=report.get('match_score_estimate', 'Unknown'),
                keywords_added=len(report.get('keywords_added', []))
            )
    
    except Exception as e:
        print(f"[API] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=f"Optimization failed: {str(e)}"
        )

@app.get("/api/v1/download/{filename}")
async def download_resume(filename: str, api_key: str = Depends(verify_api_key)):
    """
    Download a generated resume file
    
    **Authentication:** Requires X-API-Key header
    
    **Parameters:**
    - filename: Name of the generated resume file
    
    **Returns:**
    - Resume file as download
    """
    
    file_path = Path("output/api_generated") / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Resume file not found: {filename}"
        )
    
    return FileResponse(
        path=str(file_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename
    )

@app.post("/api/v1/generate-cover-letter", response_model=CoverLetterResponse)
async def generate_cover_letter(request: CoverLetterRequest, api_key: str = Depends(verify_api_key)):
    """
    Generate AI-powered cover letter for a job description
    
    **Authentication:** Requires X-API-Key header
    
    **Parameters:**
    - job_description: Full text of the job posting
    - resume_text: Optimized resume content (optional, for better context)
    - context: Additional context like career goals (optional, default: tech passion)
    - return_format: "file" (download link) or "base64" (embedded in response)
    
    **Returns:**
    - status: "success" or "error"
    - message: Human-readable message
    - download_url: URL to download cover letter (if return_format="file")
    - filename: Generated filename
    - company_name: Extracted company name or "Hiring Manager"
    - cover_letter_base64: Base64-encoded cover letter (if return_format="base64")
    
    **Note:** 
    - Applicant info is pre-configured: Dilip Kumar Thirukonda Chandrasekaran
    - Contact: (607) 624-9390 | dthirukondac@binghamton.edu
    """
    
    try:
        print(f"\n[API] Received cover letter generation request")
        print(f"[API] Job description length: {len(request.job_description)} characters")
        
        # Validate API key
        if not GEMINI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY not configured. Set environment variable GEMINI_API_KEY."
            )
        
        # Initialize cover letter generator
        print(f"[API] Initializing cover letter generator...")
        generator = CoverLetterGenerator(api_key=GEMINI_API_KEY)
        
        # Generate cover letter (uses simple builder with metadata)
        print(f"[API] Generating AI-powered cover letter...")
        doc, company_name = generator.create_cover_letter_docx(
            job_description=request.job_description,
            resume_text=request.resume_text or "",
            context=request.context or "Passionate about technology and eager to contribute to innovative projects"
        )
        
        print(f"[API] Cover letter generated!")
        print(f"[API] Company: {company_name or 'Hiring Manager'}")
        
        # Generate timestamp and filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_base = f"cover_letter_dilip_kumar_{timestamp}"
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            temp_path = tmp_file.name
        
        # Save document
        doc.save(temp_path)
        print(f"[API] Cover letter saved: {temp_path}")
        
        # Prepare response based on return format
        if request.return_format == "base64":
            # Return base64-encoded file
            import base64
            with open(temp_path, "rb") as f:
                cover_letter_bytes = f.read()
            cover_letter_base64 = base64.b64encode(cover_letter_bytes).decode('utf-8')
            
            # Clean up temp file
            try:
                Path(temp_path).unlink()
            except:
                pass
            
            return CoverLetterResponse(
                status="success",
                message="Cover letter generated successfully (55-word paragraphs, exact template formatting)",
                filename=f"{filename_base}.docx",
                company_name=company_name,
                cover_letter_base64=cover_letter_base64
            )
        
        else:  # return_format == "file"
            # Save to output directory for download
            output_dir = Path("output/api_generated")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = output_dir / f"{filename_base}.docx"
            
            # Copy from temp to output
            import shutil
            shutil.copy2(temp_path, output_file)
            
            # Clean up temp file
            try:
                Path(temp_path).unlink()
            except:
                pass
            
            # Return file path for download
            return CoverLetterResponse(
                status="success",
                message="Cover letter generated successfully (55-word paragraphs, exact template formatting)",
                download_url=f"/api/v1/download/{output_file.name}",
                filename=output_file.name,
                company_name=company_name
            )
    
    except Exception as e:
        print(f"[API] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=f"Cover letter generation failed: {str(e)}"
        )

@app.get("/api/v1/template")
async def get_template():
    """
    Get the current resume template in JSON format
    
    **Returns:**
    - JSON structure of the resume template
    """
    
    try:
        with open(RESUME_CONTENT_TEMPLATE, 'r', encoding='utf-8') as f:
            template = json.load(f)
        
        return {
            "status": "success",
            "template": template
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load template: {str(e)}"
        )

# Run server
if __name__ == "__main__":
    # Check for API key
    if not GEMINI_API_KEY:
        print("=" * 70)
        print("WARNING: GEMINI_API_KEY environment variable not set!")
        print("=" * 70)
        print("\nSet your API key before starting the server:")
        print("  Windows (PowerShell):")
        print("    $env:GEMINI_API_KEY='your-api-key-here'")
        print("    python api_server.py")
        print("\n  Linux/Mac:")
        print("    export GEMINI_API_KEY='your-api-key-here'")
        print("    python api_server.py")
        print("\nOr create a .env file with:")
        print("  GEMINI_API_KEY=your-api-key-here")
        print("=" * 70)
    
    print("\n" + "=" * 70)
    print("Starting Resume Optimizer API Server")
    print("=" * 70)
    print(f"API Documentation: http://localhost:8000/docs")
    print(f"Health Check: http://localhost:8000/health")
    print("=" * 70 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
