"""Configuration management with environment variable validation."""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, ConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        populate_by_name=True,
        extra="ignore",
    )
    
    # API Keys (required)
    openrouter_api_key: str = Field(..., validation_alias="OPENROUTER_API_KEY")
    internal_api_key: str = Field(..., validation_alias="INTERNAL_API_KEY")
    
    # API Configuration
    api_url: str = Field(
        default="https://openrouter.ai/api/v1/chat/completions",
        validation_alias="OPENROUTER_API_URL"
    )
    
    # Model Configuration
    model_name: str = Field(default="deepseek/deepseek-chat", validation_alias="MODEL_NAME")
    model_temperature: float = Field(default=0.2, validation_alias="MODEL_TEMPERATURE", ge=0.0, le=2.0)
    model_max_tokens: int = Field(default=2000, validation_alias="MODEL_MAX_TOKENS", gt=0)
    
    # Logging
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    
    # CORS Configuration
    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "https://aura-frontend-o3r.onrender.com"],
        validation_alias="CORS_ORIGINS"
    )
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is valid."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v_upper


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def init_settings():
    """Initialize settings at startup."""
    try:
        return get_settings()
    except Exception as e:
        raise RuntimeError(f"Failed to load configuration: {e}")
