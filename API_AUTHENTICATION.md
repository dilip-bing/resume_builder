# API Authentication Setup Guide

Your Resume Optimizer API now requires authentication to prevent unauthorized use. This ensures only you can access your deployed API.

## 🔐 How It Works

Every API request must include a secret key in the headers:

```python
headers = {
    "X-API-Key": "your-secret-key-here"
}
```

Without the correct key, requests will be rejected with `401 Unauthorized` or `403 Forbidden`.

## 🚀 Quick Setup (3 Steps)

### Step 1: Generate Your Secret Key

Run the API server to see your recommended key:

```bash
python start_api.py
```

**Output:**
```
🔐 Your API Secret Key: Xk7mP9nQ2rU5wY8zB1cD4fG6hJ0kL3mN5pR7sT9vW2xZ4aE6gI8jK0m
   ⚠️  Keep this secret! Include it in X-API-Key header
```

**Or generate manually:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 2: Save to `.streamlit/secrets.toml`

Edit `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your-gemini-api-key-here"
API_SECRET_KEY = "your-generated-secret-key-here"
```

### Step 3: Update Your Scripts

Edit your automation scripts:

**`automate_applications.py` (line 22):**
```python
API_SECRET_KEY = "Xk7mP9nQ2rU5wY8zB1cD4fG6hJ0kL3mN5pR7sT9vW2xZ4aE6gI8jK0m"
```

**`client_remote_example.py` (line 22):**
```python
API_SECRET_KEY = "Xk7mP9nQ2rU5wY8zB1cD4fG6hJ0kL3mN5pR7sT9vW2xZ4aE6gI8jK0m"
```

## 🌐 For Remote Deployment (Render)

When deploying to Render, add the secret key as an environment variable:

1. Go to your Render dashboard
2. Click on your service: `resume-optimizer-api`
3. Go to **"Environment"** tab
4. Click **"Add Environment Variable"**
5. Add:
   - **Key:** `API_SECRET_KEY`
   - **Value:** `Xk7mP9nQ2rU5wY8zB1cD4fG6hJ0kL3mN5pR7sT9vW2xZ4aE6gI8jK0m`
6. Click **"Save Changes"**
7. Service will auto-redeploy

## 📝 Using the API with Authentication

### Python Example

```python
import requests
import base64

API_URL = "https://resume-optimizer-api.onrender.com"
API_SECRET_KEY = "your-secret-key-here"

# Make authenticated request
response = requests.post(
    f"{API_URL}/api/v1/optimize",
    json={
        "job_description": "Job description here...",
        "return_format": "base64"
    },
    headers={
        "X-API-Key": API_SECRET_KEY  # Authentication header
    },
    timeout=120
)

result = response.json()
```

### cURL Example

```bash
curl -X POST "https://resume-optimizer-api.onrender.com/api/v1/optimize" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key-here" \
  -d '{
    "job_description": "Job description...",
    "return_format": "base64"
  }'
```

### JavaScript Example

```javascript
const response = await fetch('https://resume-optimizer-api.onrender.com/api/v1/optimize', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your-secret-key-here'  // Authentication header
  },
  body: JSON.stringify({
    job_description: 'Job description...',
    return_format: 'base64'
  })
});

const result = await response.json();
```

## ❌ Error Messages

| Error | Status Code | Meaning | Solution |
|-------|-------------|---------|----------|
| Missing API key | 401 | No `X-API-Key` header | Add header with your key |
| Invalid API key | 403 | Wrong key | Check key matches server |

**Example error:**
```json
{
  "detail": "Invalid API key. Access denied."
}
```

## 🔄 Rotating Your Key (Security Best Practice)

To change your API key:

1. **Generate new key:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Update `.streamlit/secrets.toml`:**
   ```toml
   API_SECRET_KEY = "NEW_KEY_HERE"
   ```

3. **Update Render environment variable** (if deployed)

4. **Update all client scripts** with new key

5. **Restart API server**

## 🛡️ Security Best Practices

### ✅ DO:
- Keep your API key secret (never share publicly)
- Use different keys for local and production
- Rotate keys periodically (every 3-6 months)
- Store keys in environment variables or secrets.toml
- Use strong, randomly generated keys (32+ characters)

### ❌ DON'T:
- Commit keys to Git
- Share keys in screenshots or logs
- Use simple/guessable keys like "password123"
- Hardcode keys in public code
- Reuse keys across different services

## 📊 Checking Authentication Status

**Health check shows auth status:**

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "authentication": "enabled",  // ← Shows if auth is on
  "checks": {
    "secret_key_configured": true
  }
}
```

## 🧪 Testing with Authentication

Use `test_api.py` - it auto-loads the key:

```bash
python test_api.py
```

It will:
1. Try to load key from `.streamlit/secrets.toml`
2. Try to load from environment variable
3. Run tests with authentication

## 💡 Tips

1. **Local Development:**
   - Store key in `.streamlit/secrets.toml`
   - Server auto-loads it
   - Client scripts read from same file

2. **Production (Render):**
   - Set as environment variable
   - Server loads from environment
   - Clients use hardcoded value

3. **Multiple Users:**
   - Each user needs the same key
   - Share securely (encrypted message, password manager)
   - Never share via email/Slack/public channels

## 🆘 Troubleshooting

**"Missing API key" error:**
- Add `X-API-Key` header to your request
- Check header name is exact: `X-API-Key` (case-sensitive)

**"Invalid API key" error:**
- Compare key in client vs server
- Check for extra spaces or newlines
- Regenerate and redeploy if needed

**Test script fails:**
- Make sure `.streamlit/secrets.toml` has `API_SECRET_KEY`
- Or set environment variable: `$env:API_SECRET_KEY="your-key"`
- Run `python start_api.py` to see what key server expects

**Remote API authentication fails:**
- Check Render environment variable is set
- Verify variable name is `API_SECRET_KEY` (exact)
- Redeploy after adding environment variable

## 📚 Related Files

- `.streamlit/secrets.toml` - Local key storage
- `automate_applications.py` - Update line 22
- `client_remote_example.py` - Update line 22
- `api_server.py` - Authentication logic
- `DEPLOY_RENDER.md` - Remote deployment

## ✅ Quick Checklist

Local Setup:
- [ ] Generate secret key: `python start_api.py`
- [ ] Add to `.streamlit/secrets.toml`
- [ ] Update `automate_applications.py`
- [ ] Test: `python test_api.py`

Remote Setup (Render):
- [ ] Add `API_SECRET_KEY` environment variable
- [ ] Redeploy service
- [ ] Update client scripts with same key
- [ ] Test remote endpoint

---

**🔐 Your API is now secure!** Only requests with the correct key will be accepted.
