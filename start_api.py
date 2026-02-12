"""
Start the Resume Optimizer API Server
"""
import os
import sys
import secrets

# Set API keys from environment or use the one from secrets
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
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
                    print(f"✅ Loaded GEMINI_API_KEY from {secrets_path}")
                    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
            if not API_SECRET_KEY:
                API_SECRET_KEY = secrets_data.get("API_SECRET_KEY")
                if API_SECRET_KEY:
                    print(f"✅ Loaded API_SECRET_KEY from {secrets_path}")
                    os.environ["API_SECRET_KEY"] = API_SECRET_KEY
    except Exception as e:
        print(f"⚠️  Could not load from secrets.toml: {e}")

# Check for missing keys
missing_keys = []
if not GEMINI_API_KEY:
    missing_keys.append("GEMINI_API_KEY")
if not API_SECRET_KEY:
    missing_keys.append("API_SECRET_KEY")

if missing_keys:
    print("=" * 70)
    print("❌ ERROR: Required keys not found!")
    print("=" * 70)
    
    if "GEMINI_API_KEY" in missing_keys:
        print("\n📝 GEMINI_API_KEY (Google AI):")
        print("   Get your key from: https://aistudio.google.com/app/apikey")
    
    if "API_SECRET_KEY" in missing_keys:
        # Generate a recommended secret key
        recommended_key = secrets.token_urlsafe(32)
        print("\n🔐 API_SECRET_KEY (For authentication - protects your API):")
        print(f"   Recommended key: {recommended_key}")
    
    print("\n💡 To fix, add to .streamlit/secrets.toml:")
    print("   ┌─────────────────────────────────────────┐")
    if "GEMINI_API_KEY" in missing_keys:
        print('   │ GEMINI_API_KEY = "AIzaSyA3_T..."  │')
    if "API_SECRET_KEY" in missing_keys:
        print(f'   │ API_SECRET_KEY = "{recommended_key[:20]}..." │')
    print("   └─────────────────────────────────────────┘")
    
    print("\n   Or set environment variables:")
    if "GEMINI_API_KEY" in missing_keys:
        print('     $env:GEMINI_API_KEY="AIzaSyA3_T..."')
    if "API_SECRET_KEY" in missing_keys:
        print(f'     $env:API_SECRET_KEY="{recommended_key}"')
    
    print("\n" + "=" * 70)
    sys.exit(1)

print("\n" + "=" * 70)
print("🚀 Starting Resume Optimizer API Server")
print("=" * 70)
print(f"✅ GEMINI_API_KEY configured")
print(f"✅ API_SECRET_KEY configured")
print(f"🔐 Authentication: ENABLED")
print(f"\n📝 Your API Secret Key: {API_SECRET_KEY}")
print(f"   ⚠️  Keep this secret! Include it in X-API-Key header")
print(f"\n📚 API Documentation: http://localhost:8000/docs")
print(f"❤️  Health Check: http://localhost:8000/health")
print(f"🔄 Root Endpoint: http://localhost:8000/")
print("=" * 70)
print("\nPress CTRL+C to stop the server")
print("=" * 70 + "\n")

# Import and run the server
import uvicorn
from api_server import app

uvicorn.run(
    app,
    host="0.0.0.0",
    port=8000,
    log_level="info"
)
