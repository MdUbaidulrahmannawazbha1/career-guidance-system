"""
Application configuration.

Settings are loaded from environment variables (and an optional .env file)
using pydantic-settings.  Every attribute maps 1-to-1 to a key defined in
backend/.env.example.
"""

import binascii
from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration object for the entire application."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------
    APP_NAME: str = "Secure AI-Based Career Guidance & Counselling System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = Field(default="development", pattern="^(development|staging|production)$")

    # ------------------------------------------------------------------
    # Server
    # ------------------------------------------------------------------
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    # ------------------------------------------------------------------
    # Database – PostgreSQL
    # ------------------------------------------------------------------
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/career_guidance_db"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "career_guidance_db"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "password"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # ------------------------------------------------------------------
    # JWT Authentication
    # ------------------------------------------------------------------
    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ------------------------------------------------------------------
    # Google OAuth 2.0
    # ------------------------------------------------------------------
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"

    # ------------------------------------------------------------------
    # Encryption (Fernet: AES-128-CBC + HMAC-SHA256)
    # ENCRYPTION_KEY must be a 32-byte hex-encoded string (64 hex chars).
    # The raw bytes are base64url-encoded to form the Fernet key.
    # ENCRYPTION_IV  must be a 16-byte hex-encoded string (32 hex chars).
    # ------------------------------------------------------------------
    ENCRYPTION_KEY: str = Field(..., min_length=64, max_length=64)
    ENCRYPTION_IV: str = Field(..., min_length=32, max_length=32)

    @field_validator("ENCRYPTION_KEY", mode="after")
    @classmethod
    def validate_encryption_key(cls, v: str) -> str:
        try:
            decoded = binascii.unhexlify(v)
        except binascii.Error as exc:
            raise ValueError("ENCRYPTION_KEY must be a valid 64-character hex string (32 bytes)") from exc
        if len(decoded) != 32:
            raise ValueError("ENCRYPTION_KEY must decode to exactly 32 bytes for Fernet encryption")
        return v

    @field_validator("ENCRYPTION_IV", mode="after")
    @classmethod
    def validate_encryption_iv(cls, v: str) -> str:
        try:
            decoded = binascii.unhexlify(v)
        except binascii.Error as exc:
            raise ValueError("ENCRYPTION_IV must be a valid 32-character hex string (16 bytes)") from exc
        if len(decoded) != 16:
            raise ValueError("ENCRYPTION_IV must decode to exactly 16 bytes")
        return v

    # ------------------------------------------------------------------
    # Groq LLM API
    # ------------------------------------------------------------------
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama3-8b-8192"
    GROQ_MAX_TOKENS: int = 2048
    GROQ_TEMPERATURE: float = 0.7

    # ------------------------------------------------------------------
    # ChromaDB – Vector Store
    # ------------------------------------------------------------------
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_COLLECTION_CAREERS: str = "career_embeddings"
    CHROMA_COLLECTION_RESUMES: str = "resume_embeddings"

    # ------------------------------------------------------------------
    # Rate Limiting
    # ------------------------------------------------------------------
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_AUTH_PER_MINUTE: int = 10

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    ALLOWED_METHODS: List[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    ALLOWED_HEADERS: List[str] = ["*"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("ALLOWED_METHODS", mode="before")
    @classmethod
    def parse_allowed_methods(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [m.strip() for m in v.split(",") if m.strip()]
        return v

    # ------------------------------------------------------------------
    # File Storage
    # ------------------------------------------------------------------
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "doc", "docx", "txt"]

    @field_validator("ALLOWED_FILE_TYPES", mode="before")
    @classmethod
    def parse_allowed_file_types(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [ft.strip() for ft in v.split(",") if ft.strip()]
        return v

    # ------------------------------------------------------------------
    # Email (SMTP)
    # ------------------------------------------------------------------
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_NAME: str = "Career Guidance System"
    EMAILS_FROM_ADDRESS: str = "noreply@careerguidance.com"

    # ------------------------------------------------------------------
    # Redis
    # ------------------------------------------------------------------
    REDIS_URL: str = "redis://localhost:6379/0"

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    LOG_LEVEL: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    LOG_FORMAT: str = Field(default="json", pattern="^(json|text)$")
    LOG_FILE: str = "logs/app.log"

    # ------------------------------------------------------------------
    # ML Models
    # ------------------------------------------------------------------
    ML_MODELS_DIR: str = "ml_models"
    SENTENCE_TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"
    SPACY_MODEL: str = "en_core_web_sm"

    # ------------------------------------------------------------------
    # Derived / computed helpers
    # ------------------------------------------------------------------
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def api_v1_prefix(self) -> str:
        return "/api/v1"


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton of the application settings."""
    return Settings()


# Convenience export used throughout the application:
#   from app.config import settings
settings: Settings = get_settings()
