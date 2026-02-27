# 🚀 RESUME API - QUICK CHEAT SHEET

## 📋 Essential Info (Copy These)
```
API URL: https://resume-optimizer-api-fvpd.onrender.com
API Key: nFDqvbuNJb4dwsoL9E6HfyTaPC-O2oeHvK-y1RWDSGU
```

## 🐍 Python (Resume - 5 Lines)
```python
import requests, base64
r = requests.post("https://resume-optimizer-api-fvpd.onrender.com/api/v1/optimize",
    json={"job_description": "YOUR_JOB_HERE", "return_format": "base64"},
    headers={"X-API-Key": "nFDqvbuNJb4dwsoL9E6HfyTaPC-O2oeHvK-y1RWDSGU"}, timeout=120)
open("resume.docx", "wb").write(base64.b64decode(r.json()["resume_base64"]))
```

## ✉️ Python (Cover Letter - 6 Lines)
```python
import requests, base64
r = requests.post("https://resume-optimizer-api-fvpd.onrender.com/api/v1/generate-cover-letter",
    json={"job_description": "YOUR_JOB_HERE", "applicant_name": "Dilip Kumar", 
          "applicant_email": "your@email.com", "return_format": "base64"},
    headers={"X-API-Key": "nFDqvbuNJb4dwsoL9E6HfyTaPC-O2oeHvK-y1RWDSGU"}, timeout=120)
open("cover_letter.docx", "wb").write(base64.b64decode(r.json()["cover_letter_base64"]))
```

## 🌐 cURL (Resume)
```bash
curl -X POST https://resume-optimizer-api-fvpd.onrender.com/api/v1/optimize \
  -H "X-API-Key: nFDqvbuNJb4dwsoL9E6HfyTaPC-O2oeHvK-y1RWDSGU" \
  -H "Content-Type: application/json" \
  -d '{"job_description": "YOUR_JOB", "return_format": "base64"}'
```

## 🌐 cURL (Cover Letter)
```bash
curl -X POST https://resume-optimizer-api-fvpd.onrender.com/api/v1/generate-cover-letter \
  -H "X-API-Key: nFDqvbuNJb4dwsoL9E6HfyTaPC-O2oeHvK-y1RWDSGU" \
  -H "Content-Type: application/json" \
  -d '{"job_description": "YOUR_JOB", "applicant_name": "Dilip Kumar", "return_format": "base64"}'
```

## ⚡ PowerShell
```powershell
$headers = @{"X-API-Key" = "nFDqvbuNJb4dwsoL9E6HfyTaPC-O2oeHvK-y1RWDSGU"}
$body = @{job_description = "YOUR_JOB"; return_format = "base64"} | ConvertTo-Json
Invoke-RestMethod -Uri "https://resume-optimizer-api-fvpd.onrender.com/api/v1/optimize" `
  -Method Post -Headers $headers -Body $body -ContentType "application/json"
```

## 🟢 Node.js
```javascript
const axios = require('axios');
axios.post('https://resume-optimizer-api-fvpd.onrender.com/api/v1/optimize', {
  job_description: 'YOUR_JOB', return_format: 'base64'
}, {
  headers: {'X-API-Key': 'nFDqvbuNJb4dwsoL9E6HfyTaPC-O2oeHvK-y1RWDSGU'},
  timeout: 120000
}).then(r => console.log(r.data));
```

## 📦 Request Format
```json
POST /api/v1/optimize

Headers:
  X-API-Key: nFDqvbuNJb4dwsoL9E6HfyTaPC-O2oeHvK-y1RWDSGU
  Content-Type: application/json

Body:
{
  "job_description": "Full job posting text here...",
  "return_format": "base64"  // or "file"
}
```

## 📤 Response Format
```json
{
  "success": true,
  "match_score": "95-98%",
  "keywords_added": 23,
  "filename": "resume_optimized_20260209_180929.docx",
  "resume_base64": "UEsDBBQABg..."  // Decode this to get .docx
}
```

## ⚠️ Critical Must-Knows

| Item | Value | Why |
|------|-------|-----|
| **Timeout** | 120 seconds | AI processing takes time |
| **First Request** | 30-60 seconds | API wakes up (cold start) |
| **Auth Header** | `X-API-Key: ...` | Required or get 401 error |
| **Return Format** | `base64` or `file` | base64 = embedded, file = URL |
| **Cold Start** | After 15 min idle | Free tier sleeps when unused |

## 🔍 Quick Tests
```bash
# Health check (is API alive?)
curl https://resume-optimizer-api-fvpd.onrender.com/health

# API documentation
https://resume-optimizer-api-fvpd.onrender.com/docs
```

## 🐛 Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Missing API key | Add `X-API-Key` header |
| 403 Forbidden | Wrong API key | Check key value |
| Timeout | Cold start or long job | Wait 60s, retry once |
| 422 Unprocessable | Bad request format | Check JSON structure |

## 🎯 Use Cases

**Automation Script:**
```python
jobs = ["Job 1...", "Job 2...", "Job 3..."]
for i, job in enumerate(jobs):
    # Call API (use code above)
    # Save as f"resume_{i+1}.docx"
```

**Make.com/Zapier Webhook:**
```
URL: https://resume-optimizer-api-fvpd.onrender.com/api/v1/optimize
Method: POST
Header: X-API-Key = nFDqvbuNJb4dwsoL9E6HfyTaPC-O2oeHvK-y1RWDSGU
Body: {"job_description": "{{trigger.job}}", "return_format": "base64"}
```

**Chrome Extension/Bookmarklet:**
```javascript
fetch('https://resume-optimizer-api-fvpd.onrender.com/api/v1/optimize', {
  method: 'POST',
  headers: {
    'X-API-Key': 'nFDqvbuNJb4dwsoL9E6HfyTaPC-O2oeHvK-y1RWDSGU',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    job_description: document.body.innerText,
    return_format: 'base64'
  })
})
```

## 📁 Files to Reference
- **Full Template:** `API_USAGE_TEMPLATE.py` (detailed examples)
- **Automation:** `automate_applications.py` (batch processing)
- **Testing:** `test_remote_api.py` (verify API works)

---

**⚡ Pro Tip:** Save this cheat sheet. Whenever you need to integrate the API into a new tool/script, just copy the relevant code block!
