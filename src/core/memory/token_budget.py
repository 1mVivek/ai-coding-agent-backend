MAX_TOKENS = 6000

def trim(messages: list[dict]) -> list[dict]:
    total = 0
    trimmed = []
    for msg in reversed(messages):
        total += len(msg["content"])
        if total > MAX_TOKENS:
            break
        trimmed.insert(0, msg)
    return trimmed
