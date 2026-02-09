# Deploy Resume Optimizer API to Render (FREE)

**Render** is the easiest free cloud platform for deploying the API with remote access.

## ✅ Why Render?

- ✅ **Free tier** - 750 hours/month (enough for on-demand usage)
- ✅ **No credit card** required for free tier
- ✅ **Auto-deploys** from GitHub
- ✅ **HTTPS** included
- ✅ **Easy setup** - just a few clicks
- ✅ **Perfect for APIs** like ours

## 🚀 Deployment Steps (5 minutes)

### Step 1: Create Render Account

1. Go to https://render.com
2. Click **"Get Started"**
3. Sign up with **GitHub** (easiest)

### Step 2: Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Click **"Connect GitHub"** (if not already)
3. Find your repository: **`resume_builder`**
4. Click **"Connect"**

### Step 3: Configure Service

Fill in these settings:

| Setting | Value |
|---------|-------|
| **Name** | `resume-optimizer-api` (or any name) |
| **Region** | Choose closest to you |
| **Branch** | `main` |
| **Root Directory** | *(leave empty)* |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn api_server:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | **Free** |

### Step 4: Add Environment Variable

1. Scroll to **"Environment Variables"**
2. Click **"Add Environment Variable"**
3. Set:
   - **Key**: `GEMINI_API_KEY`
   - **Value**: `AIzaSyA3_TlXuEFkCnTN55CrhfusNffMCqXmzDA` (your key)

4. Click **"Add"**

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Wait 2-3 minutes for deployment
3. You'll get a URL like: `https://resume-optimizer-api.onrender.com`

### Step 6: Test Your API

Once deployed, test it:

```python
import requests

# Replace with YOUR Render URL
API_URL = "https://resume-optimizer-api.onrender.com"

# Health check
response = requests.get(f"{API_URL}/health")
print(response.json())

# Optimize resume
result = requests.post(
    f"{API_URL}/api/v1/optimize",
    json={
        "job_description": "Your job description...",
        "return_format": "base64"
    },
    timeout=120
)
print(result.json())
```

## 🎯 Using Your Remote API

### From Anywhere in the World

```python
import requests
import base64

# Your deployed API URL (access from anywhere!)
API_URL = "https://resume-optimizer-api.onrender.com"

def get_optimized_resume(job_description):
    """Get optimized resume from remote API"""
    
    response = requests.post(
        f"{API_URL}/api/v1/optimize",
        json={
            "job_description": job_description,
            "return_format": "base64"
        },
        timeout=120
    )
    
    result = response.json()
    
    # Decode and save
    resume_data = base64.b64decode(result['resume_base64'])
    with open('optimized_resume.docx', 'wb') as f:
        f.write(resume_data)
    
    return result

# Use from ANY computer, ANY location
job_desc = "Full Stack Developer role..."
result = get_optimized_resume(job_desc)
print(f"Match Score: {result['match_score']}")
```

## ⚠️ Important: Free Tier Limits

### Render Free Tier:
- **750 hours/month** - Plenty for on-demand use
- **Spins down after 15 minutes** of inactivity
- **First request ~30 seconds** (cold start) - subsequent requests are fast
- **Auto-deploys** on Git push

### Tips to Optimize Free Tier:

1. **API will sleep** after 15 min idle
   - First request takes ~30 seconds to wake up
   - Keep it awake with periodic pings (optional)

2. **Keep-alive script** (optional):
   ```python
   # Run this every 10 minutes to keep API awake
   import requests
   import time
   
   API_URL = "https://resume-optimizer-api.onrender.com"
   
   while True:
       requests.get(f"{API_URL}/health")
       time.sleep(600)  # 10 minutes
   ```

3. **Only use when needed** - 750 hours is plenty for job applications

## 🔄 Auto-Deploy on Git Push

After initial setup, every time you push to GitHub:

```bash
git add .
git commit -m "Update API"
git push origin main
```

Render automatically:
1. Detects the push
2. Rebuilds the API
3. Deploys updates (~2 minutes)

You'll see deployment status in Render dashboard.

## 📊 Monitor Your API

### Render Dashboard
- View logs in real-time
- See deployment status
- Monitor usage
- Check errors

### API Endpoints

| Endpoint | URL |
|----------|-----|
| Documentation | `https://your-api.onrender.com/docs` |
| Health Check | `https://your-api.onrender.com/health` |
| Optimize | `https://your-api.onrender.com/api/v1/optimize` |

## 🆓 Alternative FREE Options

### 1. **Fly.io** (Also Free)
- Free tier: 3 VMs
- Better cold start times
- Setup: https://fly.io/docs/languages-and-frameworks/python/

### 2. **Railway** (Free $5 credit/month)
- Similar to Render
- Good for APIs
- Setup: https://railway.app

### 3. **Replit** (Free tier)
- Code + hosting in browser
- Always on in paid tier
- Good for testing

### 4. **Google Cloud Run** (Free tier)
- 2 million requests/month free
- More technical setup
- Excellent for production

### Comparison:

| Platform | Free Tier | Cold Start | Ease of Setup |
|----------|-----------|------------|---------------|
| **Render** ⭐ | 750 hrs/mo | ~30 sec | ⭐⭐⭐⭐⭐ Easiest |
| **Fly.io** | 3 VMs | ~10 sec | ⭐⭐⭐⭐ Easy |
| **Railway** | $5 credit/mo | ~20 sec | ⭐⭐⭐⭐⭐ Easy |
| **Replit** | Always on* | None | ⭐⭐⭐⭐⭐ Easiest |
| **Cloud Run** | 2M req/mo | ~15 sec | ⭐⭐⭐ Medium |

**Recommendation: Start with Render** - easiest, no credit card, perfect for your use case.

## 🔐 Security Notes

1. **API Key Protection**
   - Your `GEMINI_API_KEY` is stored securely in Render
   - Never exposed in code or logs
   - Can rotate anytime in dashboard

2. **Optional: Add API Authentication**
   - Add a secret token to prevent unauthorized use
   - See `api_authentication.md` (if needed)

3. **Rate Limiting** (if you want)
   - Limit requests per minute
   - Prevent abuse
   - Easy to add later

## 🎉 Complete Workflow

### Deploy Once:
```bash
# 1. Push to GitHub
git push origin main

# 2. Deploy on Render (one-time setup)
# Follow steps above

# 3. Get your URL
https://resume-optimizer-api.onrender.com
```

### Use Anywhere:
```python
# From ANY computer, ANY location
import requests

API = "https://resume-optimizer-api.onrender.com"

# Get optimized resume
response = requests.post(
    f"{API}/api/v1/optimize",
    json={
        "job_description": "...",
        "return_format": "base64"
    }
)
```

### Update API:
```bash
# Make changes locally
git add .
git commit -m "Update"
git push origin main

# Render auto-deploys in ~2 minutes
```

## 💡 Your Use Case: Automated Job Applications

Perfect workflow:

1. **Deploy API to Render** (one time, 5 minutes)
2. **Get your URL**: `https://resume-optimizer-api.onrender.com`
3. **Use in automation** from anywhere:

```python
# Run this script from ANY computer
import requests

API = "https://resume-optimizer-api.onrender.com"

jobs = get_jobs_from_linkedin()  # Your job scraper

for job in jobs:
    # Get optimized resume
    resume = requests.post(
        f"{API}/api/v1/optimize",
        json={"job_description": job.description}
    ).json()
    
    # Apply with tailored resume
    apply_to_job(job, resume)
```

4. **Turn on/off**: Just use the API when needed (no server management!)

## 🆘 Troubleshooting

**Deployment fails:**
- Check build logs in Render dashboard
- Ensure `requirements.txt` is correct
- Verify `GEMINI_API_KEY` is set

**API returns 500 error:**
- Check logs in Render dashboard
- Verify API key is valid
- Test locally first: `python start_api.py`

**Slow first request:**
- Normal! Free tier spins down after 15 min
- Subsequent requests are fast
- Optional: Use keep-alive script

**Out of free hours:**
- 750 hours = 31 days if always on
- Turn off when not needed
- Or upgrade to paid ($7/month for always-on)

## 📞 Support

- Render Docs: https://render.com/docs
- Status: https://status.render.com
- Community: https://community.render.com

## ✅ Quick Checklist

- [ ] Create Render account
- [ ] Connect GitHub repository
- [ ] Configure service settings
- [ ] Add `GEMINI_API_KEY` environment variable
- [ ] Deploy
- [ ] Test health endpoint
- [ ] Test optimize endpoint
- [ ] Use in your automation!

**Next:** See `client_remote_example.py` for remote usage examples.
