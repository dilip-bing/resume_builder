# Google Gemini API Setup Guide

## 🔑 Getting Your API Key

1. **Visit Google AI Studio**: https://makersuite.google.com/app/apikey
2. **Click "Create API Key"** (or use existing one)
3. **Copy the API key** to clipboard

---

## 📍 Where to Paste Your API Key

### For Local Development (Your Computer):

**File**: `.streamlit/secrets.toml`  
**Location**: Already created in your project

**Replace this line:**
```toml
GEMINI_API_KEY = "paste-your-api-key-here"
```

**With your actual key:**
```toml
GEMINI_API_KEY = "AIzaSyD-your-actual-key-here"
```

**✅ The file is already in `.gitignore` - your key will NOT be uploaded to GitHub**

---

### For Streamlit Cloud (Production):

1. Go to: https://share.streamlit.io/
2. Click on your app: **resumebuilder-dilip**
3. Click **⚙️ Settings** → **Secrets**
4. Paste this (with your actual key):

```toml
GEMINI_API_KEY = "AIzaSyD-your-actual-key-here"
```

5. Click **Save**
6. Your app will automatically restart with the new secret

---

## 🧪 Testing the Setup

After adding your API key:

1. **Local testing**: Run `streamlit run enhanced_app.py`
2. **Look for the new tab**: "🤖 AI Optimization"
3. **Paste a job description** and click "Optimize Resume for ATS"
4. **Check the output** - should see optimized resume with keyword matching

---

## 🔒 Security Notes

- ✅ `.streamlit/secrets.toml` is in `.gitignore` (safe)
- ✅ Streamlit Cloud secrets are encrypted (safe)
- ❌ NEVER paste your API key directly in code files
- ❌ NEVER commit secrets to GitHub

---

## 📊 Free Tier Limits

Google Gemini API Free Tier:
- **60 requests per minute**
- **1,500 requests per day**
- **100% FREE** (no credit card needed)

Perfect for resume optimization! 🎯
