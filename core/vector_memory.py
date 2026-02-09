from typing import List
import hashlib

class VectorMemory:
    """
    Minimal vector memory interface.
    FAISS / RedisVector compatible later.
    """

    def __init__(self):
        self._store = []

    def _hash(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    def add(self, text: str):
        self._store.append({
            "id": self._hash(text),
            "text": text,
        })

    def search(self, query: str, k: int = 3) -> List[str]:
        # Placeholder: return most recent
        return [item["text"] for item in self._store[-k:]]