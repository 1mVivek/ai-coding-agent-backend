import os
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agent import stream_agent

INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(
    request: Request,
    req: ChatRequest,
    x_api_key: str = Header(None)
):
    # 🔐 AUTH CHECK
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    message = req.message.strip()

    # STEP 3 happens here ↓↓↓
    if not message:
        return StreamingResponse(
            iter(["Please enter a message."]),
            media_type="text/plain"
        )

    if len(message) > 4000:
        return StreamingResponse(
            iter(["Message too long. Please shorten it."]),
            media_type="text/event-stream"
        )

    return StreamingResponse(
    stream_agent(message),
    media_type="text/plain; charset=utf-8"
    )
