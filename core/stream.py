from typing import Iterable
from core.protocol import ChatEvent

def text_stream(events: Iterable[ChatEvent]):
    for event in events:
        if event["type"] == "token":
            yield event["data"].encode("utf-8")
