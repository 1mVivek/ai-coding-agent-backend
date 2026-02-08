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

async def sse_stream(generator):
    for token in generator:
        yield f"data: {token}\n\n"

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    message = body.get("message", "")

    return StreamingResponse(
        sse_stream(run_agent_stream(message)),
        media_type="text/event-stream"
    )
