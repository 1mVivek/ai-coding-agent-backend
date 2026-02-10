import os
import tempfile
import shutil
import pytest

from src.core.rag.vector_store import VectorStore
from src.core.rag.rag_engine import RAGEngine


@pytest.fixture(scope="module")
def temp_docs_dir():
    """
    Create a temporary documents directory for RAG ingestion tests.
    """
    tmp_dir = tempfile.mkdtemp()

    docs = {
        "doc1.txt": "Python is a programming language created by Guido van Rossum.",
        "doc2.txt": "FastAPI is a modern web framework for building APIs with Python.",
        "doc3.txt": "FAISS is a library for efficient similarity search and clustering of vectors."
    }

    for name, content in docs.items():
        with open(os.path.join(tmp_dir, name), "w", encoding="utf-8") as f:
            f.write(content)

    yield tmp_dir
    shutil.rmtree(tmp_dir)


@pytest.fixture(scope="module")
def vector_store(temp_docs_dir):
    """
    Build a vector store from test documents.
    """
    store = VectorStore(
        persist_path=None,      # in-memory for tests
        embedding_model="test"  # deterministic embeddings
    )

    store.ingest_directory(temp_docs_dir)
    return store


@pytest.fixture(scope="module")
def rag_engine(vector_store):
    """
    Initialize RAG engine with vector store.
    """
    return RAGEngine(vector_store=vector_store, top_k=2)


def test_vector_store_ingestion(vector_store):
    """
    Ensure documents were embedded and indexed.
    """
    assert vector_store.count() >= 3


def test_vector_similarity_search(vector_store):
    """
    Validate semantic search returns relevant chunks.
    """
    results = vector_store.search("What is FastAPI?", top_k=2)

    assert len(results) > 0
    joined = " ".join(r["text"] for r in results).lower()
    assert "fastapi" in joined
    assert "python" in joined


def test_rag_context_building(rag_engine):
    """
    Ensure RAG engine builds context correctly.
    """
    context = rag_engine.build_context("Explain FAISS")

    assert isinstance(context, list)
    assert len(context) > 0

    roles = {m["role"] for m in context}
    assert "system" in roles or "assistant" in roles

    combined = " ".join(m["content"].lower() for m in context)
    assert "faiss" in combined


def test_rag_handles_empty_query(rag_engine):
    """
    RAG should fail safely on empty input.
    """
    context = rag_engine.build_context("")
    assert context == []


def test_rag_is_deterministic(rag_engine):
    """
    Same query should yield stable retrieval.
    """
    c1 = rag_engine.build_context("What is Python?")
    c2 = rag_engine.build_context("What is Python?")

    assert c1 == c2
