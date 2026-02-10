# src/core/rag/vector_store.py

import os
import json
import hashlib
from typing import List, Dict, Any, Optional

import numpy as np
import faiss


class VectorStore:
    """
    Lightweight FAISS vector store with metadata.
    """

    def __init__(
        self,
        dim: int = 384,
        persist_path: Optional[str] = None,
    ):
        self.dim = dim
        self.persist_path = persist_path

        self.index = faiss.IndexFlatL2(dim)
        self.texts: List[str] = []
        self.metadatas: List[Dict[str, Any]] = []

        if persist_path:
            self._load()

    # -------------------------
    # Embedding (deterministic)
    # -------------------------
    def _embed(self, text: str) -> np.ndarray:
        """
        Deterministic hash-based embedding (safe for tests & prod bootstrap).
        Replace later with HF/OpenAI if needed.
        """
        h = hashlib.sha256(text.encode()).digest()
        vec = np.frombuffer(h, dtype=np.uint8).astype("float32")
        return np.pad(vec, (0, self.dim - len(vec)))[: self.dim]

    # -------------------------
    # Ingestion
    # -------------------------
    def add(self, text: str, metadata: Dict[str, Any]):
        vector = self._embed(text).reshape(1, -1)
        self.index.add(vector)
        self.texts.append(text)
        self.metadatas.append(metadata)

    def ingest_directory(self, path: str):
        for root, _, files in os.walk(path):
            for file in files:
                if not file.endswith((".txt", ".md")):
                    continue
                full = os.path.join(root, file)
                with open(full, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if content:
                    self.add(
                        content,
                        {"source": file},
                    )
        self._persist()

    # -------------------------
    # Retrieval
    # -------------------------
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if self.index.ntotal == 0:
            return []

        qv = self._embed(query).reshape(1, -1)
        distances, indices = self.index.search(qv, top_k)

        results = []
        for idx in indices[0]:
            if idx < len(self.texts):
                results.append(
                    {
                        "text": self.texts[idx],
                        "metadata": self.metadatas[idx],
                    }
                )
        return results

    def count(self) -> int:
        return self.index.ntotal

    # -------------------------
    # Persistence
    # -------------------------
    def _persist(self):
        if not self.persist_path:
            return

        os.makedirs(self.persist_path, exist_ok=True)
        faiss.write_index(self.index, os.path.join(self.persist_path, "index.faiss"))
        with open(os.path.join(self.persist_path, "store.json"), "w") as f:
            json.dump(
                {"texts": self.texts, "metadatas": self.metadatas},
                f,
            )

    def _load(self):
        index_path = os.path.join(self.persist_path, "index.faiss")
        meta_path = os.path.join(self.persist_path, "store.json")

        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)

        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                data = json.load(f)
                self.texts = data.get("texts", [])
                self.metadatas = data.get("metadatas", [])
