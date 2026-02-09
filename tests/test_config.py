"""Unit tests for configuration management."""
import os
import pytest
from pydantic import ValidationError
from src.core.config import Settings


def test_settings_with_all_required_env_vars(monkeypatch):
    """Test that settings load correctly with all required variables."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_openrouter_key")
    monkeypatch.setenv("INTERNAL_API_KEY", "test_internal_key")
    
    settings = Settings()
    
    assert settings.openrouter_api_key == "test_openrouter_key"
    assert settings.internal_api_key == "test_internal_key"
    assert settings.model_name == "deepseek/deepseek-chat"
    assert settings.model_temperature == 0.2
    assert settings.model_max_tokens == 2000


def test_settings_missing_required_env_vars():
    """Test that settings fail without required variables."""
    # Clear any existing env vars
    for key in ["OPENROUTER_API_KEY", "INTERNAL_API_KEY"]:
        os.environ.pop(key, None)
    
    with pytest.raises(ValidationError):
        Settings()


def test_settings_with_custom_values(monkeypatch):
    """Test that custom values override defaults."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "key1")
    monkeypatch.setenv("INTERNAL_API_KEY", "key2")
    monkeypatch.setenv("MODEL_TEMPERATURE", "0.5")
    monkeypatch.setenv("MODEL_MAX_TOKENS", "4000")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    
    settings = Settings()
    
    assert settings.model_temperature == 0.5
    assert settings.model_max_tokens == 4000
    assert settings.log_level == "DEBUG"


def test_invalid_log_level(monkeypatch):
    """Test that invalid log level raises error."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "key1")
    monkeypatch.setenv("INTERNAL_API_KEY", "key2")
    monkeypatch.setenv("LOG_LEVEL", "INVALID")
    
    with pytest.raises(ValidationError):
        Settings()


def test_temperature_bounds(monkeypatch):
    """Test that temperature is validated within bounds."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "key1")
    monkeypatch.setenv("INTERNAL_API_KEY", "key2")
    
    # Valid temperature
    monkeypatch.setenv("MODEL_TEMPERATURE", "1.5")
    settings = Settings()
    assert settings.model_temperature == 1.5
    
    # Invalid temperature (too high)
    monkeypatch.setenv("MODEL_TEMPERATURE", "3.0")
    with pytest.raises(ValidationError):
        Settings()
