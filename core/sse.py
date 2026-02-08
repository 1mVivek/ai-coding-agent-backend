from typing import Iterable
from core.protocol import ChatEvent

def sse_stream(events: Iterable[ChatEvent]):
    for event in events:
        yield f"event: {event['type']}\n".encode("utf-8")
        yield f"data: {event['data']}\n\n".encode("utf-8")
