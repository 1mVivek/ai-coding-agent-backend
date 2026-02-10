"""
FastAPI application for AI coding agent backend.

- SSE streaming
- Session memory
- RAG (vector search)
- Secure API key auth
"""

import uuid
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.agent.deepseek import stream_agent
from src.core.config import init_settings
from src.core.logger import get_logger
from src.core.memory.short_term import ShortTermMemory
from src.core.memory.vector_memory import VectorMemory
from src.core.rag.rag_engine import RAGEngine

# ---------------------------------------------------------------------
# Settings & Logger
# ---------------------------------------------------------------------

settings = init_settings()
logger = get_logger(level=settings.log_level)

# ---------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Coding Agent Backend")
    logger.info(f"Model: {settings.model_name}")
    logger.info(f"Temperature: {settings.model_temperature}")
    logger.info(f"Max Tokens: {settings.model_max_tokens}")
    yield
    logger.info("Shutting down AI Coding Agent Backend")

# ---------------------------------------------------------------------
# App
# ---------------------------------------------------------------------

app = FastAPI(
    title="AI Coding Agent Backend",
    description="Streaming chat API with SSE + Memory + RAG",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------
# Global Stores (SAFE singletons)
# ---------------------------------------------------------------------

# Long-term vector store (RAG)
vector_memory = VectorMemory()
rag_engine = RAGEngine(vector_memory)

# Per-session short-term memory
memory_store: Dict[str, ShortTermMemory] = {}

def get_memory(session_id: str) -> ShortTermMemory:
    if session_id not in memory_store:
        memory_store[session_id] = ShortTermMemory()
        logger.debug(f"Created memory for session={session_id}")
    return memory_store[session_id]

# ---------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str | None = None

class HealthResponse(BaseModel):
    status: str
    model: str
    version: str

# ---------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------

@app.get("/", response_model=HealthResponse)
async def root():
    return HealthResponse(
        status="ok",
        model=settings.model_name,
        version="1.0.0",
    )

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        model=settings.model_name,
        version="1.0.0",
    )

@app.post("/chat")
async def chat(
    req: ChatRequest,
    request: Request,
    x_api_key: str = Header(None, alias="x-api-key"),
):
    # ------------------ Auth ------------------
    if not x_api_key or x_api_key != settings.internal_api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_msg = req.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Empty message")

    session_id = req.session_id or str(uuid.uuid4())
    memory = get_memory(session_id)

    logger.info(
        f"Chat request session={session_id}, message_length={len(user_msg)}"
    )

    # ------------------ Store user message ------------------
    memory.add("user", user_msg)

    # ------------------ RAG Context ------------------
    rag_context = rag_engine.build_context(user_msg)

    # ------------------ Final messages ------------------
    messages = (
        rag_context
        + memory.build()
        + [{"role": "user", "content": user_msg}]
    )

    # ------------------ SSE Generator ------------------
    async def event_generator():
        assistant_text = ""

        try:
            yield "event: start\ndata: {}\n\n"

            async for event in stream_agent(messages):
                if await request.is_disconnected():
                    logger.info(f"Client disconnected: session={session_id}")
                    break

                if event["type"] == "token":
                    assistant_text += event["data"]
                    yield f"event: token\ndata: {event['data']}\n\n"

                elif event["type"] == "done":
                    break

            if assistant_text:
                memory.add("assistant", assistant_text)
                logger.info(
                    f"Chat completed session={session_id}, "
                    f"response_length={len(assistant_text)}"
                )

            yield "event: done\ndata: {}\n\n"

        except Exception as e:
            logger.exception("Unexpected SSE error")
            yield f"event: error\ndata: {str(e)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
        )
