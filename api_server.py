"""
Compatibility entrypoint for ASGI servers (e.g., Render).

Render commonly starts FastAPI with: `uvicorn api_server:app`.
In this repo the actual implementation lives in `scripts/api_server.py`.
"""

from __future__ import annotations

# Re-export the FastAPI app object for `uvicorn api_server:app`.
from scripts.api_server import app  # type: ignore  # noqa: F401

