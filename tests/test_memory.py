"""Unit tests for memory management."""
import pytest
from src.core.memory.short_term import ShortTermMemory


def test_memory_initialization():
    """Test memory initialization with default max messages."""
    memory = ShortTermMemory()
    assert memory.max_messages == 10
    assert memory.messages == []


def test_memory_custom_max():
    """Test memory with custom max messages."""
    memory = ShortTermMemory(max_messages=5)
    assert memory.max_messages == 5


def test_add_message():
    """Test adding messages to memory."""
    memory = ShortTermMemory()
    memory.add("user", "Hello")
    memory.add("assistant", "Hi there")
    
    assert len(memory.messages) == 2
    assert memory.messages[0] == {"role": "user", "content": "Hello"}
    assert memory.messages[1] == {"role": "assistant", "content": "Hi there"}


def test_memory_truncation():
    """Test that memory truncates old messages."""
    memory = ShortTermMemory(max_messages=3)
    
    memory.add("user", "msg1")
    memory.add("assistant", "msg2")
    memory.add("user", "msg3")
    memory.add("assistant", "msg4")
    
    # Should only keep last 3
    assert len(memory.messages) == 3
    assert memory.messages[0]["content"] == "msg2"
    assert memory.messages[1]["content"] == "msg3"
    assert memory.messages[2]["content"] == "msg4"


def test_build_returns_copy():
    """Test that build returns a copy of messages."""
    memory = ShortTermMemory()
    memory.add("user", "Hello")
    
    messages = memory.build()
    messages.append({"role": "system", "content": "test"})
    
    # Original memory should be unchanged
    assert len(memory.messages) == 1
    assert len(messages) == 2


def test_empty_memory_build():
    """Test building from empty memory."""
    memory = ShortTermMemory()
    messages = memory.build()
    
    assert messages == []
    assert isinstance(messages, list)
