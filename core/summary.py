def summarize_messages(messages: list[dict], max_chars: int = 800) -> str:
    """
    Deterministic fallback summary.
    Replace with LLM later.
    """
    chunks = []
    for m in messages:
        role = m["role"]
        content = m["content"]
        chunks.append(f"{role}: {content}")

    text = " ".join(chunks)
    return text[:max_chars]