"""Unit tests for logger setup."""
import logging
from src.core.logger import setup_logger, get_logger, ColoredFormatter


def test_setup_logger_default():
    """Test logger setup with defaults."""
    logger = setup_logger("test_logger_1")
    
    assert logger.name == "test_logger_1"
    assert logger.level == logging.INFO
    assert len(logger.handlers) > 0


def test_setup_logger_with_level():
    """Test logger setup with custom level."""
    logger = setup_logger("test_logger_2", level="DEBUG")
    
    assert logger.level == logging.DEBUG


def test_get_logger():
    """Test get_logger singleton."""
    logger1 = get_logger("test_logger_3")
    logger2 = get_logger("test_logger_4")
    
    assert isinstance(logger1, logging.Logger)
    assert isinstance(logger2, logging.Logger)


def test_colored_formatter():
    """Test colored formatter."""
    formatter = ColoredFormatter(fmt='%(levelname)s - %(message)s')
    
    # Create a log record
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None,
    )
    
    formatted = formatter.format(record)
    assert "Test message" in formatted
    assert "\033[" in formatted  # Color code present


def test_logger_doesnt_duplicate_handlers():
    """Test that calling setup_logger twice doesn't add duplicate handlers."""
    logger = setup_logger("test_logger_5")
    handler_count_1 = len(logger.handlers)
    
    logger = setup_logger("test_logger_5")  # Call again
    handler_count_2 = len(logger.handlers)
    
    assert handler_count_1 == handler_count_2
