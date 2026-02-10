# src/core/rag/rag_engine.py

from typing import List, Dict
from src.core.rag.vector_store import VectorStore


class RAGEngine:
    """
    Retrieval-Augmented Generation context builder.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        top_k: int = 3,
    ):
        self.vector_store = vector_store
        self.top_k = top_k

    def build_context(self, query: str) -> List[Dict[str, str]]:
        if not query.strip():
            return []

        docs = self.vector_store.search(query, self.top_k)

        if not docs:
            return []

        context_blocks = []
        for d in docs:
            context_blocks.append(
                f"[Source: {d['metadata'].get('source', 'unknown')}]\n{d['text']}"
            )

        system_prompt = (
            "You are an AI assistant. Use ONLY the context below. "
            "If the answer is not present, say you don't know.\n\n"
            + "\n\n---\n\n".join(context_blocks)
        )

        return [
            {"role": "system", "content": system_prompt},
        ]
