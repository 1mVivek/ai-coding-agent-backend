from typing import List, Dict

class ShortTermMemory:
    def __init__(self, max_turns: int = 8):
        self.max_turns = max_turns
        self.messages: List[Dict[str, str]] = []

    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        self._trim()

    def _trim(self):
        """
        Keep system messages + last N user/assistant turns
        """
        system_messages = [m for m in self.messages if m["role"] == "system"]
        convo_messages = [m for m in self.messages if m["role"] != "system"]

        max_messages = self.max_turns * 2
        if len(convo_messages) > max_messages:
            convo_messages = convo_messages[-max_messages:]

        self.messages = system_messages + convo_messages

    def build(self) -> List[Dict[str, str]]:
        """
        Final messages sent to the model
        """
        return self.messages.copy()
        def clear(self):
        self.messages.clear()
