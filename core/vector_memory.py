from typing import List
import hashlib

class VectorMemory:
    def __init__(self):
        self._store = []

    def _hash(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    def add(self, text: str, source: str = "doc"):
        self._store.append({
            "id": self._hash(text),
            "text": text,
            "source": source,
        })

    def search(self, query: str, k: int = 4) -> List[str]:
        # TEMP similarity: keyword overlap
        query_words = set(query.lower().split())

        scored = []
        for item in self._store:
            words = set(item["text"].lower().split())
            score = len(query_words & words)
            scored.append((score, item["text"]))

        scored.sort(reverse=True)
        return [text for score, text in scored[:k] if score > 0]