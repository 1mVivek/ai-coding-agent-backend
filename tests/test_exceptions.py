"""Unit tests for custom exceptions."""
import pytest
from src.core.exceptions import (
    AIAgentException,
    ConfigurationError,
    APIError,
    StreamError,
    AuthenticationError,
    ValidationError,
)


def test_base_exception():
    """Test base exception."""
    exc = AIAgentException("Test error")
    assert str(exc) == "Test error"
    assert isinstance(exc, Exception)


def test_configuration_error():
    """Test configuration error."""
    exc = ConfigurationError("Config missing")
    assert isinstance(exc, AIAgentException)
    assert str(exc) == "Config missing"


def test_api_error_with_status():
    """Test API error with status code."""
    exc = APIError("API failed", status_code=500)
    assert exc.status_code == 500
    assert str(exc) == "API failed"
    assert isinstance(exc, AIAgentException)


def test_api_error_without_status():
    """Test API error without status code."""
    exc = APIError("API failed")
    assert exc.status_code is None
    assert str(exc) == "API failed"


def test_stream_error():
    """Test stream error."""
    exc = StreamError("Stream interrupted")
    assert isinstance(exc, AIAgentException)
    assert str(exc) == "Stream interrupted"


def test_authentication_error():
    """Test authentication error."""
    exc = AuthenticationError("Invalid credentials")
    assert isinstance(exc, AIAgentException)
    assert str(exc) == "Invalid credentials"


def test_validation_error():
    """Test validation error."""
    exc = ValidationError("Invalid input")
    assert isinstance(exc, AIAgentException)
    assert str(exc) == "Invalid input"


def test_exception_hierarchy():
    """Test exception inheritance hierarchy."""
    assert issubclass(ConfigurationError, AIAgentException)
    assert issubclass(APIError, AIAgentException)
    assert issubclass(StreamError, AIAgentException)
    assert issubclass(AuthenticationError, AIAgentException)
    assert issubclass(ValidationError, AIAgentException)
