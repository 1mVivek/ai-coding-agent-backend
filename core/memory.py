from __future__ import annotations

import time
import hashlib
from typing import List, Dict, Optional


# =========================
# SECURITY CONSTANTS
# =========================
MAX_MESSAGE_LENGTH = 4000
MAX_SESSIONS = 10_000


def _sanitize(text: str) -> str:
    """Basic input sanitation."""
    text = text.strip()
    if len(text) > MAX_MESSAGE_LENGTH:
        text = text[:MAX_MESSAGE_LENGTH]
    return text


def _hash_session(session_id: str) -> str:
    """Prevent raw session IDs from being stored."""
    return hashlib.sha256(session_id.encode()).hexdigest()


# =========================
# VECTOR MEMORY (PLACEHOLDER)
# =========================
class VectorMemory:
    """
    Long-term memory store.
    Replace internals with FAISS / Chroma / Weaviate later.
    """

    def __init__(self):
        self._store: List[Dict[str, str]] = []

    def add(self, text: str):
        self._store.append(
            {
                "text": text,
                "timestamp": time.time(),
            }
        )

    def search(self, query: str, k: int = 3) -> List[str]:
        # TEMP: naive similarity (replace with embeddings later)
        return [item["text"] for item in self._store[-k:]]

    def clear(self):
        self._store.clear()


# =========================
# SHORT + SUMMARY MEMORY
# =========================
class ShortTermMemory:
    """
    ChatGPT-style memory:
    - rolling recent messages
    - summarized older context
    - vector long-term memory
    """

    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self.messages: List[Dict[str, str]] = []
        self.summary: Optional[str] = None
        self.vector_memory = VectorMemory()

    # ---------- Core API ----------

    def add(self, role: str, content: str):
        content = _sanitize(content)

        self.messages.append(
            {
                "role": role,
                "content": content,
            }
        )

        if role == "assistant":
            self.vector_memory.add(content)

        self._trim()

    def build(self) -> List[Dict[str, str]]:
        """
        Build final context for LLM:
        system → summary → recent messages
        """
        context: List[Dict[str, str]] = []

        if self.summary:
            context.append(
                {
                    "role": "system",
                    "content": f"Conversation summary:\n{self.summary}",
                }
            )

        context.extend(self.messages)
        return context

    def clear(self):
        self.messages.clear()
        self.summary = None
        self.vector_memory.clear()

    # ---------- Internal ----------

    def _trim(self):
        """
        Trim old messages and summarize if needed.
        """
        system_msgs = [m for m in self.messages if m["role"] == "system"]
        convo = [m for m in self.messages if m["role"] != "system"]

        max_messages = self.max_turns * 2

        if len(convo) <= max_messages:
            return

        overflow = convo[:-max_messages]
        convo = convo[-max_messages:]

        self._summarize(overflow)
        self.messages = system_msgs + convo

    def _summarize(self, old_messages: List[Dict[str, str]]):
        """
        Lightweight summary generator.
        (Replace with LLM call later.)
        """
        text = " ".join(m["content"] for m in old_messages)
        if not text:
            return

        if self.summary:
            self.summary += " " + text[:800]
        else:
            self.summary = text[:800]


# =========================
# MEMORY STORE (SECURE)
# =========================
class MemoryStore:
    """
    Secure session-based memory store.
    """

    def __init__(self):
        self._store: Dict[str, ShortTermMemory] = {}

    def get(self, session_id: str) -> ShortTermMemory:
        if len(self._store) > MAX_SESSIONS:
            raise RuntimeError("Memory store limit exceeded")

        key = _hash_session(session_id)

        if key not in self._store:
            self._store[key] = ShortTermMemory()

        return self._store[key]

    def clear(self, session_id: str):
        key = _hash_session(session_id)
        self._store.pop(key, None)