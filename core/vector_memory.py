from typing import List
import time
import math

class VectorMemory:
    """
    Lightweight semantic memory.
    Replace similarity() with embeddings later.
    """

    def __init__(self, max_items: int = 200):
        self.max_items = max_items
        self.store: List[dict] = []

    def add(self, text: str):
        self.store.append({
            "text": text,
            "timestamp": time.time()
        })

        if len(self.store) > self.max_items:
            self.store.pop(0)

    def similarity(self, a: str, b: str) -> float:
        a, b = a.lower(), b.lower()
        common = set(a.split()) & set(b.split())
        return len(common) / max(len(set(a.split())), 1)

    def search(self, query: str, k: int = 3) -> List[str]:
        scored = [
            (self.similarity(query, item["text"]), item["text"])
            for item in self.store
        ]
        scored.sort(reverse=True)
        return [text for score, text in scored[:k]]

    def clear(self):
        self.store.clear()