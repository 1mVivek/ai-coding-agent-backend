from typing import List, Dict
from .token_budget import trim_to_token_budget
from .summary import summarize_messages
from .vector_memory import VectorMemory

class ShortTermMemory:
    def __init__(
        self,
        max_turns: int = 8,
        max_tokens: int = 3000,
    ):
        self.max_turns = max_turns
        self.max_tokens = max_tokens

        self.messages: List[Dict[str, str]] = []
        self.summary: str | None = None
        self.vector = VectorMemory()

    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        self._trim()

        # Only persist assistant replies into vector store
        if role == "assistant":
            self.vector.add(content)

    def _trim(self):
        # Turn-based trim
        convo = [m for m in self.messages if m["role"] != "system"]
        system = [m for m in self.messages if m["role"] == "system"]

        if len(convo) > self.max_turns * 2:
            old = convo[:-self.max_turns * 2]
            convo = convo[-self.max_turns * 2:]

            # Summarize removed messages
            self.summary = summarize_messages(old)

        merged = system + convo

        # Token-budget trim (hard limit)
        merged = trim_to_token_budget(merged, self.max_tokens)

        self.messages = merged

    def build(self) -> List[Dict[str, str]]:
        final = []

        # System-controlled summary (NOT user editable)
        if self.summary:
            final.append({
                "role": "system",
                "content": f"Conversation summary:\n{self.summary}"
            })

        final.extend(self.messages)

        return final.copy()

    def retrieve_context(self, query: str) -> List[str]:
        return self.vector.search(query)

    def clear(self):
        self.messages.clear()
        self.summary = None