"""Custom exception classes for better error handling."""
from typing import Optional


class AIAgentException(Exception):
    """Base exception for AI agent errors."""
    pass


class ConfigurationError(AIAgentException):
    """Raised when configuration is invalid or missing."""
    pass


class APIError(AIAgentException):
    """Raised when external API call fails."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(message)


class StreamError(AIAgentException):
    """Raised when stream processing fails."""
    pass


class AuthenticationError(AIAgentException):
    """Raised when authentication fails."""
    pass


class ValidationError(AIAgentException):
    """Raised when input validation fails."""
    pass
