import os
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse
from core.memory import ShortTermMemory
from core.context import build_messages
from core.stream import text_stream
from agent.deepseek import stream_agent

app = FastAPI()
memory = ShortTermMemory()

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
