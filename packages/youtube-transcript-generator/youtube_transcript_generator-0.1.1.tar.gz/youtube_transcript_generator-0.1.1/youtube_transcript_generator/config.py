"""
Configuration management for YouTube Transcript Generator.
"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings and environment variables."""
    
    # API Keys and Credentials
    GEMINI_API_KEY: str
    YOUTUBE_API_KEY: Optional[str] = None
    
    # AI Model Configuration
    MODEL_NAME: str = "gemini-pro"
    MAX_RETRIES: int = 3
    TIMEOUT: int = 30
    
    # YouTube Configuration
    MAX_VIDEO_LENGTH: int = 14400  # 4 hours in seconds
    SUPPORTED_LANGUAGES: list[str] = ["en", "es", "fr", "de", "it"]
    
    # Application Configuration
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    CACHE_DIR: str = ".cache"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 3600  # 1 hour in seconds
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    Returns:
        Settings: Application settings instance
    """
    return Settings()