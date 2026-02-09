"""
API Configuration
Easily switch between local and remote API
"""

# ============================================================
# API URL Configuration
# ============================================================

# Local API (when running on your computer)
LOCAL_API = "http://localhost:8000"

# Remote API (after deploying to Render)
# Replace this URL after deploying!
REMOTE_API = "https://resume-optimizer-api.onrender.com"

# ============================================================
# Active Configuration
# ============================================================

# Change this to switch between local and remote
USE_REMOTE = False  # Set to True to use remote API

# Active API URL
API_URL = REMOTE_API if USE_REMOTE else LOCAL_API

# ============================================================
# Usage in your scripts
# ============================================================

"""
Import and use:

    from api_config import API_URL
    
    response = requests.post(
        f"{API_URL}/api/v1/optimize",
        json={"job_description": "..."}
    )
"""

# ============================================================
# Helper Functions
# ============================================================

def get_api_url():
    """Get the current API URL"""
    return API_URL

def use_local():
    """Switch to local API"""
    global API_URL, USE_REMOTE
    USE_REMOTE = False
    API_URL = LOCAL_API
    return API_URL

def use_remote():
    """Switch to remote API"""
    global API_URL, USE_REMOTE
    USE_REMOTE = True
    API_URL = REMOTE_API
    return API_URL

def set_remote_url(url: str):
    """Set custom remote URL"""
    global REMOTE_API, API_URL, USE_REMOTE
    REMOTE_API = url
    if USE_REMOTE:
        API_URL = url
    return API_URL

if __name__ == "__main__":
    print(f"Current API URL: {API_URL}")
    print(f"Mode: {'Remote' if USE_REMOTE else 'Local'}")
