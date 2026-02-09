"""
Start the Resume Optimizer API Server
"""
import os
import sys

# Set API key from environment or use the one from secrets
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
                print(f"✅ Loaded API key from {secrets_path}")
                os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
    except Exception as e:
        print(f"⚠️  Could not load from secrets.toml: {e}")

if not GEMINI_API_KEY:
    print("=" * 70)
    print("❌ ERROR: GEMINI_API_KEY not found!")
    print("=" * 70)
    print("\nPlease set your API key:")
    print("\n  Option 1: Environment variable")
    print("    Windows (PowerShell):")
    print("      $env:GEMINI_API_KEY='your-api-key-here'")
    print("      python start_api.py")
    print("\n    Linux/Mac:")
    print("      export GEMINI_API_KEY='your-api-key-here'")
    print("      python start_api.py")
    print("\n  Option 2: .streamlit/secrets.toml (already exists)")
    print("    Just run: python start_api.py")
    print("\n  Option 3: Create .env file")
    print("    Create a .env file with:")
    print("      GEMINI_API_KEY=your-api-key-here")
    print("=" * 70)
    sys.exit(1)

print("\n" + "=" * 70)
print("🚀 Starting Resume Optimizer API Server")
print("=" * 70)
print(f"✅ API Key configured")
print(f"📝 API Documentation: http://localhost:8000/docs")
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
