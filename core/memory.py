import json
import hashlib
import redis
from typing import List, Dict

from .vector_memory import VectorMemory
from .summary import summarize_messages
from .token_budget import messages_token_count

MAX_TOKENS = 3000
MAX_TURNS = 10

redis_client = redis.Redis(
    host="REDIS_HOST",
    port=6379,
    decode_responses=True
)


def hash_session(session_id: str) -> str:
    return hashlib.sha256(session_id.encode()).hexdigest()


class Memory:
    def __init__(self, session_id: str):
        self.session = hash_session(session_id)
        self.vector = VectorMemory()

    # ---------- Redis helpers ----------

    def _key(self, suffix: str) -> str:
        return f"session:{self.session}:{suffix}"

    # ---------- Core API ----------

    def add(self, role: str, content: str):
        msg = {"role": role, "content": content}

        redis_client.rpush(self._key("messages"), json.dumps(msg))

        if role == "assistant":
            self.vector.add(content)

        self._trim()

    def build(self) -> List[Dict[str, str]]:
        messages = self._load_messages()
        summary = redis_client.get(self._key("summary"))

        context = []

        if summary:
            context.append({
                "role": "system",
                "content": f"Conversation summary:\n{summary}"
            })

        context.extend(messages)
        return context

    # ---------- Internal ----------

    def _load_messages(self) -> List[Dict]:
        raw = redis_client.lrange(self._key("messages"), 0, -1)
        return [json.loads(m) for m in raw]

    def _save_messages(self, messages: List[Dict]):
        redis_client.delete(self._key("messages"))
        for m in messages:
            redis_client.rpush(self._key("messages"), json.dumps(m))

    def _trim(self):
        messages = self._load_messages()

        # Turn-based trimming
        non_system = [m for m in messages if m["role"] != "system"]
        if len(non_system) > MAX_TURNS * 2:
            overflow = non_system[:-MAX_TURNS * 2]
            summary = summarize_messages(overflow)
            redis_client.set(self._key("summary"), summary)
            messages = non_system[-MAX_TURNS * 2:]
            self._save_messages(messages)

        # Token-based trimming (HARD LIMIT)
        while messages_token_count(messages) > MAX_TOKENS:
            messages.pop(0)

        self._save_messages(messages)

    def clear(self):
        redis_client.delete(
            self._key("messages"),
            self._key("summary"),
        )
        self.vector.clear()