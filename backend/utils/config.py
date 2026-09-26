import os
from pathlib import Path
from dotenv import load_dotenv

# Try to load .env from backend directory first, then root directory
backend_dir = Path(__file__).resolve().parent.parent
root_dir = backend_dir.parent

if (backend_dir / ".env").exists():
    load_dotenv(backend_dir / ".env")
elif (root_dir / ".env").exists():
    load_dotenv(root_dir / ".env")
else:
    load_dotenv()

class Settings:
    PROJECT_NAME: str = "FINNEWS AI"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Financial News Simplifier API - Turn complex financial news into simple insights."
    
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "").strip()
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
    
    # Defaults & Constraints
    MAX_ARTICLES_TO_FETCH: int = 15
    DEFAULT_SUMMARIZE_COUNT: int = 6
    MAX_CONTENT_CHARS: int = 2500
    
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "*").split(",")
        if origin.strip()
    ]

settings = Settings()
