import os
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

from core.memory import ShortTermMemory
from core.context import build_messages
from core.stream import text_stream
from core.sse import sse_stream
from agent.deepseek import stream_agent

import os

# =====================
# App setup
# =====================

app = FastAPI(
    title="Aura AI Backend",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "dev-key")

memory = ShortTermMemory()

# =====================
# Health check
# =====================

@app.get("/")
async def root():
    return {"status": "ok"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# =====================
# Normal chat (plain text stream)
# =====================

@app.post("/chat")
async def chat(req: dict, x_api_key: str = Header(None)):
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_msg = req.get("message", "").strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Empty message")

    memory.add("user", user_msg)
    messages = build_messages(memory, user_msg)

    async def event_generator():
        async for event in stream_agent(messages):
            if event["type"] == "token":
                yield event["data"].encode("utf-8")

    return StreamingResponse(
        event_generator(),
        media_type="text/plain; charset=utf-8",
    )

# =====================
# SSE chat (modern clients)
# =====================

@app.post("/chat/stream")
async def chat_stream(req: dict, x_api_key: str = Header(None)):
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_msg = req.get("message", "").strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Empty message")

    memory.add("user", user_msg)
    messages = build_messages(memory, user_msg)

    async def event_generator():
        async for event in stream_agent(messages):
            yield event
        yield {"type": "done", "data": ""}

    return StreamingResponse(
        sse_stream(event_generator()),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
