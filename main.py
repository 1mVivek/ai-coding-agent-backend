from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from agent import run_agent_stream

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def sse_generator(message: str):
    for token in run_agent_stream(message):
        yield f"data: {token}\n\n"

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    message = body.get("message", "")

    return StreamingResponse(
        sse_generator(message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
