# scripts/ingest.py

import argparse
from src.core.rag.vector_store import VectorStore


def main():
    parser = argparse.ArgumentParser(description="RAG document ingestion")
    parser.add_argument("--docs", required=True, help="Path to documents folder")
    parser.add_argument(
        "--store",
        default="vector_store",
        help="Path to persist vector store",
    )
    args = parser.parse_args()

    store = VectorStore(
        persist_path=args.store,
    )

    store.ingest_directory(args.docs)

    print(f"✅ Ingested {store.count()} documents")
    print(f"📦 Vector store saved to: {args.store}")


if __name__ == "__main__":
    main()
