# Resume Optimizer API Documentation

REST API for automated resume optimization using Google Gemini AI.

## Overview

The Resume Optimizer API allows you to programmatically optimize resumes for specific job descriptions. Perfect for:
- **Automated job applications** - Apply to multiple jobs with tailored resumes
- **Batch processing** - Generate resumes for dozens of jobs at once
- **Integration** - Connect to your job application automation tools
- **Testing** - Quickly test different resume variations

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set API Key

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY = "your-api-key-here"
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

**Or create `.env` file:**
```
GEMINI_API_KEY=your-api-key-here
```

### 3. Start the Server

```bash
python api_server.py
```

Server will start on: `http://localhost:8000`

### 4. Test the API

**Check health:**
```bash
curl http://localhost:8000/health
```

**Open interactive docs:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### 1. Health Check

**GET** `/health`

Check if API is running and configured correctly.

**Response:**
```json
{
  "status": "healthy",
  "checks": {
    "api_key_configured": true,
    "template_exists": true,
    "metadata_exists": true,
    "original_resume_exists": true
  },
  "timestamp": "2026-02-09T12:00:00"
}
```

---

### 2. Optimize Resume

**POST** `/api/v1/optimize`

Generate an optimized resume for a specific job description.

**Request Body:**
```json
{
  "job_description": "We are looking for a Senior Software Engineer with...",
  "return_format": "file"  // or "base64"
}
```

**Parameters:**
- `job_description` (string, required): Full text of the job posting
- `return_format` (string, optional): 
  - `"file"` (default) - Returns download URL
  - `"base64"` - Returns base64-encoded file in response

**Response (file mode):**
```json
{
  "status": "success",
  "message": "Resume optimized successfully",
  "download_url": "/api/v1/download/resume_optimized_20260209_120000.docx",
  "filename": "resume_optimized_20260209_120000.docx",
  "match_score": "85-90%",
  "keywords_added": 12
}
```

**Response (base64 mode):**
```json
{
  "status": "success",
  "message": "Resume optimized successfully",
  "filename": "resume_optimized_20260209_120000.docx",
  "match_score": "85-90%",
  "keywords_added": 12,
  "resume_base64": "UEsDBBQABgAIAAAAIQBi7p1o..."
}
```

---

### 3. Download Resume

**GET** `/api/v1/download/{filename}`

Download a generated resume file (used with `return_format="file"`).

**Response:**
- Content-Type: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- File download

---

### 4. Get Template

**GET** `/api/v1/template`

Get the current resume template in JSON format.

**Response:**
```json
{
  "status": "success",
  "template": {
    "personal": {...},
    "education": [...],
    "skills": {...},
    ...
  }
}
```

## Usage Examples

### Python (using requests)

```python
import requests

# Optimize resume
response = requests.post(
    "http://localhost:8000/api/v1/optimize",
    json={
        "job_description": "Your job description here...",
        "return_format": "base64"
    },
    timeout=120
)

result = response.json()
print(f"Match Score: {result['match_score']}")

# Save base64 resume
import base64
resume_data = base64.b64decode(result['resume_base64'])
with open('resume.docx', 'wb') as f:
    f.write(resume_data)
```

### cURL

```bash
# Optimize resume
curl -X POST "http://localhost:8000/api/v1/optimize" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Your job description here...",
    "return_format": "file"
  }'

# Download resume
curl -O "http://localhost:8000/api/v1/download/resume_optimized_20260209_120000.docx"
```

### JavaScript (fetch)

```javascript
// Optimize resume
const response = await fetch('http://localhost:8000/api/v1/optimize', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    job_description: 'Your job description here...',
    return_format: 'base64'
  })
});

const result = await response.json();
console.log('Match Score:', result.match_score);

// Decode and download
const binaryData = atob(result.resume_base64);
const blob = new Blob([binaryData], { 
  type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' 
});

// Trigger download
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = result.filename;
a.click();
```

## Batch Processing Example

Process multiple job applications at once:

```python
import requests
import base64

# List of jobs
jobs = [
    {"company": "TechCorp", "description": "..."},
    {"company": "DataInc", "description": "..."},
    {"company": "StartupXYZ", "description": "..."}
]

# Process each job
for job in jobs:
    response = requests.post(
        "http://localhost:8000/api/v1/optimize",
        json={
            "job_description": job['description'],
            "return_format": "base64"
        },
        timeout=120
    )
    
    result = response.json()
    
    # Save resume
    resume_data = base64.b64decode(result['resume_base64'])
    filename = f"resume_{job['company']}.docx"
    with open(filename, 'wb') as f:
        f.write(resume_data)
    
    print(f"✅ {job['company']}: Match {result['match_score']}")
```

See [client_example.py](client_example.py) for full batch processing example.

## Deployment

### Local Development

```bash
python api_server.py
```

### Production (with Uvicorn)

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (Future)

```dockerfile
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
ENV GEMINI_API_KEY=your-key-here
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment Options

1. **Railway** - Easy one-click deployment
2. **Render** - Free tier available
3. **Heroku** - Classic PaaS
4. **AWS Lambda** + API Gateway - Serverless
5. **Google Cloud Run** - Container-based

## Rate Limits & Performance

- **Processing Time**: 10-30 seconds per resume (depends on Gemini API)
- **Concurrent Requests**: Depends on your deployment
- **Gemini API Limits**: Check your Google AI Studio quota
- **Timeout**: 120 seconds recommended

## Error Handling

**Common errors:**

| Status Code | Error | Solution |
|-------------|-------|----------|
| 500 | `GEMINI_API_KEY not configured` | Set environment variable |
| 500 | `Optimization failed` | Check job description format |
| 404 | Resume file not found | File expired or invalid filename |
| 408 | Request timeout | Job description too long |

**Example error response:**
```json
{
  "detail": "GEMINI_API_KEY not configured. Set environment variable GEMINI_API_KEY."
}
```

## Security Considerations

⚠️ **Important for production:**

1. **API Key Protection**
   - Never commit API keys to Git
   - Use environment variables or secret managers
   - Rotate keys regularly

2. **Authentication** (add if needed)
   - Add API key authentication for your endpoints
   - Use OAuth2 for user-based access
   - Implement rate limiting

3. **Input Validation**
   - Job descriptions are limited to reasonable length
   - Prevent injection attacks
   - Sanitize file names

4. **CORS** (if accessed from browser)
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourfrontend.com"],
       allow_methods=["POST", "GET"],
       allow_headers=["*"]
   )
   ```

## Monitoring & Logging

The API logs to console by default. For production:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)
```

## Troubleshooting

**API won't start:**
- Check if port 8000 is available
- Verify all files exist (template, metadata, original resume)
- Ensure GEMINI_API_KEY is set

**Optimization fails:**
- Check Gemini API quota
- Verify job description is not empty
- Check network connectivity

**Downloads fail:**
- Ensure `output/api_generated/` directory exists
- Check file permissions

**Slow performance:**
- Gemini API can take 10-30 seconds
- Consider caching results
- Use background tasks for batch processing

## Support

See main [README.md](README.md) for general project documentation.

## License

Same as main project.
