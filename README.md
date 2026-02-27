# Resume Builder

AI-powered resume optimization and cover letter generation with complete format preservation.

## Features

- **Format Preservation** — Exact replication of original resume formatting (fonts, spacing, margins, bold/italic patterns)
- **AI Optimization** — Gemini-powered ATS keyword optimization
- **Cover Letter Generation** — Single-API-call cover letter generation in one shot
- **REST API** — FastAPI server with authentication, CORS, rate limiting, and security headers
- **Chrome Extension** — Browser extension for quick job application assistance

## Project Structure

```
ResumeBuilder/
├── scripts/                    # All Python source code
│   ├── enhanced_app.py         # Streamlit web app (main entry point)
│   ├── api_server.py           # FastAPI REST API server
│   ├── start_api.py            # API server launcher
│   ├── gemini_optimizer.py     # AI resume optimizer
│   ├── cover_letter_generator.py
│   ├── enhanced_format_system.py
│   ├── char_limiter.py
│   └── simple_cover_letter_builder.py
├── templates/                  # Resume & cover letter JSON templates
├── reference_docx/             # Original resume/cover letter templates
├── metadata/                   # Extracted formatting metadata
├── output/                     # Generated files (gitignored)
├── chrome-extension/           # Browser extension
├── .streamlit/                 # Streamlit config
├── .env.example                # Environment variable template
├── requirements.txt
└── README.md
```

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API keys

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Or add them to `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
API_SECRET_KEY = "your_api_secret_key_here"
```

Get your Gemini API key from: https://aistudio.google.com/app/apikey

### 3. Run the Streamlit app

```bash
streamlit run scripts/enhanced_app.py
```

Opens at http://localhost:8501

### 4. Run the API server (optional)

```bash
python scripts/start_api.py
```

API available at http://localhost:8000  
Docs at http://localhost:8000/docs

## Security

- API key authentication on all endpoints (`X-API-Key` header)
- Constant-time key comparison (prevents timing attacks)
- CORS restricted to allowed origins
- Rate limiting (30 req/min per IP)
- Security headers on all responses (`X-Content-Type-Options`, `X-Frame-Options`, etc.)
- Input validation with length limits
- Path traversal protection on file downloads
- Secrets loaded from environment / `.env` / `.streamlit/secrets.toml` — never hardcoded

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `API_SECRET_KEY` | Yes | Secret key for REST API authentication |
| `ALLOWED_ORIGINS` | No | Comma-separated CORS origins (default: `http://localhost:8501`) |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/optimize` | Optimize resume for a job description |
| `POST` | `/api/v1/generate-cover-letter` | Generate cover letter |
| `GET` | `/api/v1/download/{filename}` | Download generated file |
| `GET` | `/api/v1/template` | Get resume template JSON |

All write endpoints require `X-API-Key` header.

## Requirements

- Python 3.10+
- See `requirements.txt` for package list
