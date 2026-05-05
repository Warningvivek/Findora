"""
core/config.py
──────────────
Pydantic-settings based configuration.
Values are read from environment variables / .env file.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    # ── Security ──────────────────────────────────────────────────────────────
    SECRET_KEY: str = Field(default="change-me-in-production-32-char-minimum!!")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./memory_assistant.db"

    # ── AI Models ─────────────────────────────────────────────────────────────
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    SUMMARIZER_MODEL: str = "facebook/bart-large-cnn"

    # ── File Storage ──────────────────────────────────────────────────────────
    UPLOAD_DIR: Path = Path("./uploads")
    MAX_FILE_SIZE_MB: int = 50

    # ── FAISS ─────────────────────────────────────────────────────────────────
    FAISS_INDEX_DIR: Path = Path("./faiss_indexes")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

# Ensure required directories exist at import time
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.FAISS_INDEX_DIR.mkdir(parents=True, exist_ok=True)
