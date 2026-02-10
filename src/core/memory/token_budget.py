from typing import List, Dict

# Rough estimate (safe + fast)
TOKENS_PER_CHAR = 0.25  

def estimate_tokens(text: str) -> int:
    return int(len(text) * TOKENS_PER_CHAR)

def messages_token_count(messages: List[Dict[str, str]]) -> int:
    return sum(estimate_tokens(m["content"]) for m in messages)

def trim_to_token_budget(
    messages: List[Dict[str, str]],
    max_tokens: int,
) -> List[Dict[str, str]]:
    """
    Trim oldest non-system messages until within token budget.
    """
    system_msgs = [m for m in messages if m["role"] == "system"]
    convo_msgs = [m for m in messages if m["role"] != "system"]

    while convo_msgs and messages_token_count(system_msgs + convo_msgs) > max_tokens:
        convo_msgs.pop(0)

    return system_msgs + convo_msgs
