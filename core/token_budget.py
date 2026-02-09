def estimate_tokens(text: str) -> int:
    # Safe heuristic: ~4 chars/token
    return max(1, len(text) // 4)


def messages_token_count(messages: list[dict]) -> int:
    return sum(estimate_tokens(m["content"]) for m in messages)