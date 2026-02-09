from typing import List, Dict

SUMMARY_SYSTEM_PROMPT = (
    "You are a system that summarizes conversations for memory retention. "
    "Preserve facts, decisions, user preferences, and goals. "
    "Remove chit-chat."
)

def summarize_messages(messages: List[Dict[str, str]]) -> str:
    """
    Placeholder summarizer.
    Later replace with model-based summarization.
    """
    important = []
    for m in messages:
        if m["role"] in ("user", "assistant"):
            important.append(m["content"])

    # HARD RULE: summary must be short
    joined = " ".join(important)
    return joined[:1200]  # safety cap