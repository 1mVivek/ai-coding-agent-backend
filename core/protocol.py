from typing import Literal, TypedDict

EventType = Literal[
    "token",
    "error",
    "done",
    "system",
    "tool",
    "plan"
]

class ChatEvent(TypedDict):
    type: EventType
    data: str
