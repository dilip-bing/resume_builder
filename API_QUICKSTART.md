# Resume Optimizer API - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Start the API Server

```bash
python start_api.py
```

The API will automatically load your GEMINI_API_KEY from `.streamlit/secrets.toml`.

**Expected output:**
```
🚀 Starting Resume Optimizer API Server
✅ API Key configured
📝 API Documentation: http://localhost:8000/docs
❤️  Health Check: http://localhost:8000/health
```

### Step 2: Test the API

Open a **new terminal** and run:

```bash
python test_api.py
```

This will run 4 tests:
1. ✅ Root endpoint
2. ✅ Health check
3. ✅ Template retrieval
4. ✅ Resume optimization (creates `test_resume.docx`)

**Expected output:**
```
✅ All tests passed! API is working correctly.
```

### Step 3: Use in Your Automation

```python
import requests
import base64

# Optimize resume for a job
response = requests.post(
    "http://localhost:8000/api/v1/optimize",
    json={
        "job_description": "Your job description here...",
        "return_format": "base64"
    },
    timeout=120
)

result = response.json()

# Save the resume
resume_data = base64.b64decode(result['resume_base64'])
with open('resume.docx', 'wb') as f:
    f.write(resume_data)

print(f"Match Score: {result['match_score']}")
print(f"Keywords Added: {result['keywords_added']}")
```

## 📚 Full Examples

### Single Job Application

```python
python client_example.py
```

This will:
1. Check API health
2. Optimize resume for a sample job
3. Save to `resume_software_engineer.docx`
4. Show match score and keywords added

### Batch Processing Multiple Jobs

The `client_example.py` script also demonstrates batch processing:
- Process 3 different job postings
- Generate tailored resume for each
- Show summary of all results

## 🔗 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root - Service info |
| `/health` | GET | Health check |
| `/api/v1/optimize` | POST | Optimize resume |
| `/api/v1/download/{filename}` | GET | Download resume file |
| `/api/v1/template` | GET | Get current template |

## 📖 Documentation

- **Interactive API Docs**: http://localhost:8000/docs (when server is running)
- **Full Documentation**: See [API_README.md](API_README.md)
- **Client Examples**: See [client_example.py](client_example.py)

## 🛠️ Common Issues

### API won't start
- Make sure `.streamlit/secrets.toml` has your `GEMINI_API_KEY`
- Check port 8000 is not in use
- Verify all files exist (template, metadata, original resume)

### Optimization fails
- Check your Gemini API quota
- Ensure job description is not empty
- Wait 10-30 seconds for AI processing

### Test fails
- Make sure API server is running in another terminal
- Check `http://localhost:8000/health` shows all ✅

## 💡 Use Cases

### 1. Job Application Automation
```python
# Read job descriptions from file/database
# For each job:
#   - Call API to optimize resume
#   - Save with company name
#   - Apply to job with tailored resume
```

### 2. A/B Testing Resumes
```python
# Test different resume variations
# Compare match scores
# Use best performing template
```

### 3. Batch Generation
```python
# Generate 10 resumes at once
# Each optimized for different role/company
# Save all for later use
```

## 🌐 Deployment

### Local (Development)
```bash
python start_api.py
```

### Production (with more workers)
```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Cloud Platforms
- Railway
- Render
- AWS Lambda
- Google Cloud Run

See [API_README.md](API_README.md) for deployment details.

## 📝 API Response Example

```json
{
  "status": "success",
  "message": "Resume optimized successfully",
  "filename": "resume_optimized_20260209_120000.docx",
  "match_score": "85-90%",
  "keywords_added": 12,
  "resume_base64": "UEsDBBQABgAIAAAAIQ..."
}
```

## 🎯 Next Steps

1. ✅ Test the API: `python test_api.py`
2. 📖 Read full docs: [API_README.md](API_README.md)
3. 🔍 Explore examples: [client_example.py](client_example.py)
4. 🚀 Build your automation!

## ❓ Questions?

- Check `/docs` endpoint for interactive API documentation
- See [API_README.md](API_README.md) for detailed information
- Test with `test_api.py` to verify setup
