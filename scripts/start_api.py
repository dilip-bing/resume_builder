"""
Start the Resume Optimizer API Server
"""
import os
import sys
import secrets

# Load .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- Load keys ---------------------------------------------------------------

def _from_toml(key: str):
    try:
        import toml
        return toml.load(".streamlit/secrets.toml").get(key)
    except Exception:
        return None

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or _from_toml("GEMINI_API_KEY")
API_SECRET_KEY = os.getenv("API_SECRET_KEY") or _from_toml("API_SECRET_KEY")

if GEMINI_API_KEY:
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
if API_SECRET_KEY:
    os.environ["API_SECRET_KEY"] = API_SECRET_KEY

# --- Validate ----------------------------------------------------------------

missing = []
if not GEMINI_API_KEY:
    missing.append("GEMINI_API_KEY")
if not API_SECRET_KEY:
    missing.append("API_SECRET_KEY")

if missing:
    print("=" * 65)
    print("[ERROR] Required keys not found: " + ", ".join(missing))
    print("=" * 65)
    print("\nAdd them to .env (or .streamlit/secrets.toml):")
    for k in missing:
        if k == "API_SECRET_KEY":
            suggested = secrets.token_urlsafe(32)
            print(f"  {k}={suggested}")
        else:
            print(f"  {k}=your_value_here")
    print("\nOr set environment variables:")
    for k in missing:
        print(f"  $env:{k}=your_value_here   (PowerShell)")
    print("=" * 65)
    sys.exit(1)

# --- Start -------------------------------------------------------------------

print("\n" + "=" * 65)
print("  Resume Optimizer API Server")
print("=" * 65)
print("  [OK] GEMINI_API_KEY configured")
print("  [OK] API_SECRET_KEY configured")
print("  [OK] Authentication: ENABLED")
print()
print("  API Docs   : http://localhost:8000/docs")
print("  Health     : http://localhost:8000/health")
print("=" * 65)
print("\nPress CTRL+C to stop.\n")

import uvicorn
from scripts.api_server import app

uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
