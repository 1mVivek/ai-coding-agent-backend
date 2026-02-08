import os
from fastapi.responses import StreamingResponse
from core.sse import sse_stream
from core.context import build_messages
from core.memory import ShortTermMemory
from agent.deepseek import stream_agent

memory = ShortTermMemory()

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
