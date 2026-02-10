from typing import List, Dict


class RAGEngine:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def build_context(self, query: str) -> List[Dict]:
        docs = self.vector_store.search(query, k=4)
        return [
            {"role": "system", "content": f"Context:\n{doc}"}
            for doc in docs
        ]