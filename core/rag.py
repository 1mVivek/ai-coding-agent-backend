from typing import List
from .vector_memory import VectorMemory

RAG_SYSTEM_PROMPT = (
    "You are provided with external knowledge. "
    "Use it ONLY if relevant. "
    "Do not mention that you are using documents."
)

class RAGEngine:
    def __init__(self, vector_store: VectorMemory):
        self.vector_store = vector_store

    def retrieve(self, query: str, k: int = 4) -> List[str]:
        return self.vector_store.search(query, k=k)

    def build_context(self, query: str) -> List[dict]:
        chunks = self.retrieve(query)

        if not chunks:
            return []

        joined = "\n\n".join(chunks)

        return [
            {
                "role": "system",
                "content": f"{RAG_SYSTEM_PROMPT}\n\nKnowledge:\n{joined}"
            }
        ]