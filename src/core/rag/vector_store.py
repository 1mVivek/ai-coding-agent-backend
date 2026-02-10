import numpy as np
from typing import List


class VectorStore:
    def __init__(self, backend=None):
        self.backend = backend  # Redis / FAISS injected later

    def search(self, query: str, k: int = 4) -> List[str]:
        if not self.backend:
            return []
        return self.backend.search(query, k)