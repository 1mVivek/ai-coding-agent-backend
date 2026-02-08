import os
import uuid
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agent.deepseek import stream_agent
from memory import ShortTermMemory

# =========================
# ENV VALIDATION (CRITICAL)
# =========================
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY")
if not INTERNAL_API_KEY:
    raise RuntimeError("INTERNAL_API_KEY is not set")

# =========================
# APP
# =========================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://aura-frontend-o3r.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

# =========================
# MEMORY STORE (TEMP)
# =========================
memory_store: dict[str, ShortTermMemory] = {}


def get_memory(session_id: str) -> ShortTermMemory:
    if session_id not in memory_store:
        memory_store[session_id] = ShortTermMemory()
    return memory_store[session_id]


# =========================
# SCHEMA
# =========================
class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


# =========================
# ROUTE
# =========================
@app.post("/chat")
async def chat(
    req: ChatRequest,
    x_api_key: str = Header(None),
):
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_msg = req.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Empty message")

    session_id = req.session_id or str(uuid.uuid4())
    memory = get_memory(session_id)

    # Add user message ONCE
    memory.add("user", user_msg)

    async def event_generator():
        assistant_text = ""

        async for event in stream_agent(memory.build()):
            if event["type"] == "token":
                assistant_text += event["data"]
                yield f"data: {event['data']}\n\n"

            elif event["type"] == "done":
                break

        # Persist assistant reply AFTER stream completes
        if assistant_text:
            memory.add("assistant", assistant_text)

        yield "event: done\ndata: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
