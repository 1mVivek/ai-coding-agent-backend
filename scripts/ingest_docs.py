import os
from src.core.vector_memory import VectorMemory

DOC_PATH = "src/data/documents"

def ingest():
    vector = VectorMemory()

    for file in os.listdir(DOC_PATH):
        path = os.path.join(DOC_PATH, file)

        if not file.endswith((".txt", ".md")):
            continue

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        # Simple chunking (upgrade later)
        chunks = text.split("\n\n")

        for chunk in chunks:
            chunk = chunk.strip()
            if len(chunk) > 50:
                vector.add(chunk, source=file)

    print("✅ Documents ingested into vector memory")

if __name__ == "__main__":
    ingest()