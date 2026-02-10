class ShortTermMemory:
    def __init__(self, max_messages: int = 10):
        self.max_messages = max_messages
        self.messages = []

    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        self.messages = self.messages[-self.max_messages :]

    def get(self):
        """Return the internal messages list directly."""
        return self.messages

    def build(self):
        """Return a copy of messages list (safe for modification)."""
        return list(self.messages)
