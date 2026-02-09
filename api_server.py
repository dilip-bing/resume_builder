"""
FastAPI Server for Resume Optimization API
Provides REST API endpoint for automated resume generation with job description
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
import tempfile
import json
from pathlib import Path
from datetime import datetime
import os

# Import existing resume builder components
from gemini_optimizer import GeminiATSOptimizer
from enhanced_format_system import EnhancedFormatBuilder

# Initialize FastAPI app
app = FastAPI(
    title="Resume Optimizer API",
    description="AI-powered resume optimization API for ATS (Applicant Tracking Systems)",
    version="1.0.0"
)

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# If not in environment, try to load from .streamlit/secrets.toml
if not GEMINI_API_KEY:
    try:
        import toml
        secrets_path = ".streamlit/secrets.toml"
        if os.path.exists(secrets_path):
            secrets = toml.load(secrets_path)
            GEMINI_API_KEY = secrets.get("GEMINI_API_KEY")
            if GEMINI_API_KEY:
                print(f"[INFO] Loaded API key from {secrets_path}")
    except Exception as e:
        print(f"[WARNING] Could not load from secrets.toml: {e}")

RESUME_CONTENT_TEMPLATE = "templates/resume_content_template.json"
FORMAT_METADATA_JSON = "metadata/format_metadata.json"
ORIGINAL_RESUME = "reference_docx/resume_optimized_final.docx"

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

class OptimizeResponse(BaseModel):
    status: str
    message: str
    download_url: Optional[str] = None
    filename: Optional[str] = None
    match_score: Optional[str] = None
    keywords_added: Optional[int] = None
    resume_base64: Optional[str] = None

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
        "template_exists": Path(RESUME_CONTENT_TEMPLATE).exists(),
        "metadata_exists": Path(FORMAT_METADATA_JSON).exists(),
        "original_resume_exists": Path(ORIGINAL_RESUME).exists()
    }
    
    all_healthy = all(checks.values())
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "checks": checks,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/optimize", response_model=OptimizeResponse)
async def optimize_resume(request: OptimizeRequest):
    """
    Optimize resume for a specific job description
    
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
                filename=f"resume_optimized_{timestamp}.docx",
                match_score=report.get('match_score_estimate', 'Unknown'),
                keywords_added=len(report.get('keywords_added', [])),
                resume_base64=resume_base64
            )
        
        else:  # return_format == "file"
            # Save to output directory for download
            output_dir = Path("output/api_generated")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = output_dir / f"resume_optimized_{timestamp}.docx"
            
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
async def download_resume(filename: str):
    """
    Download a generated resume file
    
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
