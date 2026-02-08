from typing import Literal, TypedDict

EventType = Literal["token", "error", "done"]

class ChatEvent(TypedDict):
    type: EventType
    data: str
