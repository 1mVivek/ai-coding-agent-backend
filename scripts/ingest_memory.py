# scripts/ingest_memory.py

import json
import argparse
from src.core.memory.redis_store import redis_client


def ingest_memory(file_path: str, ttl: int = 3600):
    """
    Ingest historical chat memory into Redis.
    JSON format:
    {
      "session_id": [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
      ]
    }
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for session_id, messages in data.items():
        key = f"chat:{session_id}"
        redis_client.setex(key, ttl, json.dumps(messages))
        print(f"✅ Ingested session: {session_id} ({len(messages)} messages)")


def main():
    parser = argparse.ArgumentParser(description="Ingest chat memory into Redis")
    parser.add_argument(
        "--file",
        required=True,
        help="Path to memory JSON file",
    )
    parser.add_argument(
        "--ttl",
        type=int,
        default=3600,
        help="TTL for session memory (seconds)",
    )
    args = parser.parse_args()

    ingest_memory(args.file, args.ttl)


if __name__ == "__main__":
    main()
