# 🚀 Remote API Access - Complete Setup Guide

## 🎯 Your Goal
Access the Resume Optimizer API from **anywhere** (turn on whenever/wherever you want) for **FREE**.

## ✅ Best FREE Option: Render

**Why Render?**
- ✅ **Completely FREE** (750 hours/month - plenty for job applications)
- ✅ **No credit card** required
- ✅ **5-minute setup**
- ✅ **Access from anywhere** - home, work, phone, anywhere
- ✅ **Auto-deploys** from GitHub (just push code, it updates)

## 🚀 Quick Setup (5 Minutes)

### 1. Deploy to Render

```
1. Go to: https://render.com
2. Sign up with GitHub (free)
3. Click "New +" → "Web Service"
4. Connect your repository: resume_builder
5. Fill in:
   - Name: resume-optimizer-api
   - Build Command: pip install -r requirements.txt
   - Start Command: uvicorn api_server:app --host 0.0.0.0 --port $PORT
   - Instance Type: FREE
6. Add Environment Variable:
   - Key: GEMINI_API_KEY
   - Value: your-gemini-api-key-here
7. Click "Create Web Service"
8. Wait 2-3 minutes
9. Get your URL: https://resume-optimizer-api.onrender.com
```

**That's it!** Your API is now accessible from anywhere.

Full guide: [DEPLOY_RENDER.md](DEPLOY_RENDER.md)

### 2. Test Your Remote API

```bash
python client_remote_example.py
```

This will:
- Check if your API is online
- Test optimization
- Save a test resume

Update the `API_URL` in the file first:
```python
API_URL = "https://resume-optimizer-api.onrender.com"  # Your Render URL
```

### 3. Use for Actual Job Applications

Edit [`automate_applications.py`](automate_applications.py):

```python
# 1. Set your API URL
API_URL = "https://resume-optimizer-api.onrender.com"

# 2. Add job descriptions
JOBS = [
    {
        "company": "Google",
        "role": "Software Engineer",
        "job_url": "https://...",
        "description": """
        Full job description here...
        """
    },
    {
        "company": "Microsoft",
        "role": "Backend Developer",
        "job_url": "https://...",
        "description": """
        Another job description...
        """
    },
    # Add as many as you want...
]
```

Run it:
```bash
python automate_applications.py
```

You'll get:
- ✅ Optimized resume for EACH job
- ✅ Match score for each
- ✅ All saved in `generated_resumes/` folder
- ✅ Ready to apply!

## 🌐 Use from ANYWHERE

Once deployed, you can call the API from:

### From Your Computer (Windows/Mac/Linux)
```python
import requests
import base64

response = requests.post(
    "https://resume-optimizer-api.onrender.com/api/v1/optimize",
    json={"job_description": "...", "return_format": "base64"}
)

resume = base64.b64decode(response.json()['resume_base64'])
with open('resume.docx', 'wb') as f:
    f.write(resume)
```

### From Any Script/Automation Tool
- Python scripts
- Node.js scripts
- Browser console
- Postman
- cURL commands
- Anywhere with internet!

### From Your Phone (via API client app)
- Use HTTP client apps
- Call the API endpoint
- Download resume

## 📊 What You Get

```
INPUT: Job description
OUTPUT: Optimized resume (.docx file)

Response includes:
- Match score: "85-90%"
- Keywords added: 15
- Resume file (base64 or download link)
```

## 💰 Cost: $0 (FREE)

**Render Free Tier:**
- 750 hours/month (more than enough)
- Sleeps after 15 min idle (wakes up in ~30 sec on first request)
- Perfect for on-demand use (job applications)

**Usage estimate:**
- Each optimization: ~30 seconds
- 100 job applications/month: ~50 minutes total
- **Cost: $0**

## 🔄 Auto-Updates

Every time you push to GitHub:
```bash
git push origin main
```

Render automatically:
1. Detects the push
2. Rebuilds API
3. Deploys updates (~2 min)

No manual deployment needed!

## 📱 Complete Workflow

### Your Job Application Process:

```
1. Find jobs on LinkedIn/Indeed/etc
   ↓
2. Copy job description
   ↓
3. Add to automate_applications.py
   ↓
4. Run: python automate_applications.py
   ↓
5. Get optimized resume for each job
   ↓
6. Apply with tailored resumes
   ↓
7. Track responses
```

## 🎯 Files You Need

| File | Purpose |
|------|---------|
| **[automate_applications.py](automate_applications.py)** | **MAIN SCRIPT** - Add jobs, run, get resumes |
| [DEPLOY_RENDER.md](DEPLOY_RENDER.md) | Deployment guide |
| [client_remote_example.py](client_remote_example.py) | Remote API examples |
| [api_config.py](api_config.py) | Switch local/remote easily |

## ⚡ Quick Reference

### Start Local API (for testing)
```bash
python start_api.py
```

### Test Local API
```bash
python test_api.py
```

### Deploy to Render
See [DEPLOY_RENDER.md](DEPLOY_RENDER.md)

### Use Remote API
1. Edit `automate_applications.py`
2. Set `API_URL = "https://your-url.onrender.com"`
3. Add job descriptions to `JOBS` list
4. Run: `python automate_applications.py`

### Switch Between Local/Remote
Edit `api_config.py`:
```python
USE_REMOTE = False  # Local
USE_REMOTE = True   # Remote
```

## 🆓 Other FREE Options

If Render doesn't work for you:

| Platform | Free Tier | Setup Time | Best For |
|----------|-----------|------------|----------|
| **Render** ⭐ | 750 hrs/mo | 5 min | Easiest, recommended |
| **Fly.io** | 3 VMs | 10 min | Better cold start |
| **Railway** | $5 credit/mo | 5 min | Similar to Render |
| **Replit** | Always on* | 3 min | Quick testing |
| **Cloud Run** | 2M req/mo | 20 min | Production scale |

All free! See [DEPLOY_RENDER.md](DEPLOY_RENDER.md) for comparisons.

## ❓ Troubleshooting

**API not responding?**
- Wait 30 seconds (cold start)
- Check Render dashboard for errors
- Verify GEMINI_API_KEY is set

**Optimization fails?**
- Check your Gemini API quota
- Ensure job description is valid
- Try with shorter description

**Can't deploy?**
- Make sure GitHub repo is public
- Check if all files are pushed
- See Render build logs for errors

## 🎉 You're Ready!

1. ✅ API code is ready
2. ✅ Deployment guide created
3. ✅ Automation script ready
4. ✅ All pushed to GitHub

**Next Step:**
1. Deploy to Render (5 minutes): [DEPLOY_RENDER.md](DEPLOY_RENDER.md)
2. Test with: `python client_remote_example.py`
3. Start applying: `python automate_applications.py`

**Need Help?**
- Local testing: `python start_api.py` then `python test_api.py`
- API docs: http://localhost:8000/docs (local) or https://your-url.onrender.com/docs (remote)
- Deployment: See [DEPLOY_RENDER.md](DEPLOY_RENDER.md)

## 💡 Pro Tips

1. **Batch processing**: Add 10-20 jobs at once, run script, get all resumes
2. **Keep-alive** (optional): Ping API every 10 min to avoid cold starts
3. **Track applications**: Add job URLs to `JOBS` list for reference
4. **Version control**: Different resumes for different job types
5. **A/B testing**: Compare match scores, use best performing resume

---

**🚀 You now have a fully remote, free, AI-powered resume optimization API!**

Use it whenever and wherever you want to apply for jobs. Good luck! 🎯
