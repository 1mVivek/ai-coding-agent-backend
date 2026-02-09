"""
FastAPI application for AI coding agent backend.

Provides streaming chat API with authentication and memory management.
"""
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

from agent.deepseek import stream_agent
from core.memory import ShortTermMemory
from src.core.config import init_settings
from src.core.logger import get_logger
from src.core.exceptions import APIError, StreamError, ValidationError

# Initialize settings at startup
settings = init_settings()
logger = get_logger(level=settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting AI Coding Agent Backend")
    logger.info(f"Model: {settings.model_name}")
    logger.info(f"Temperature: {settings.model_temperature}")
    logger.info(f"Max Tokens: {settings.model_max_tokens}")
    yield
    logger.info("Shutting down AI Coding Agent Backend")


# =========================
# APP
# =========================
app = FastAPI(
    title="AI Coding Agent Backend",
    description="Streaming chat API with DeepSeek model",
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

# =========================
# MEMORY STORE (TEMP)
# =========================
memory_store: dict[str, ShortTermMemory] = {}


def get_memory(session_id: str) -> ShortTermMemory:
    """Get or create memory for a session."""
    if session_id not in memory_store:
        memory_store[session_id] = ShortTermMemory()
        logger.debug(f"Created new memory for session: {session_id}")
    return memory_store[session_id]


# =========================
# SCHEMA
# =========================
class ChatRequest(BaseModel):
    """Chat request schema."""
    message: str = Field(..., min_length=1, description="User message")
    session_id: str | None = Field(None, description="Session ID for conversation continuity")


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str
    model: str
    version: str


# =========================
# ROUTES
# =========================
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with API information."""
    return HealthResponse(
        status="ok",
        model=settings.model_name,
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    logger.debug("Health check requested")
    return HealthResponse(
        status="healthy",
        model=settings.model_name,
        version="1.0.0"
    )


@app.post("/chat")
async def chat(
    req: ChatRequest,
    request: Request,
    x_api_key: str = Header(None, alias="x-api-key"),
):
    """
    Stream chat completions.
    
    Requires x-api-key header for authentication.
    """
    # Authentication
    if not x_api_key or x_api_key != settings.internal_api_key:
        client_host = request.client.host if request.client else "unknown"
        logger.warning(f"Unauthorized access attempt from {client_host}")
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_msg = req.message.strip()
    if not user_msg:
        logger.warning("Empty message received")
        raise HTTPException(status_code=400, detail="Empty message")

    session_id = req.session_id or str(uuid.uuid4())
    memory = get_memory(session_id)
    
    logger.info(f"Chat request: session={session_id}, message_length={len(user_msg)}")

    # Add user message ONCE
    memory.add("user", user_msg)

    async def event_generator():
        """Generate SSE events from agent stream."""
        assistant_text = ""
        
        try:
            async for event in stream_agent(memory.build()):
                if event["type"] == "token":
                    assistant_text += event["data"]
                    yield f"data: {event['data']}\n\n"

                elif event["type"] == "done":
                    break

            # Persist assistant reply AFTER stream completes
            if assistant_text:
                memory.add("assistant", assistant_text)
                logger.info(f"Chat completed: session={session_id}, response_length={len(assistant_text)}")

            yield "event: done\ndata: [DONE]\n\n"
            
        except APIError as e:
            error_msg = f"API Error: {str(e)}"
            logger.error(f"Stream error for session {session_id}: {error_msg}")
            yield f"event: error\ndata: {error_msg}\n\n"
        except StreamError as e:
            error_msg = f"Stream Error: {str(e)}"
            logger.error(f"Stream error for session {session_id}: {error_msg}")
            yield f"event: error\ndata: {error_msg}\n\n"
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected error for session {session_id}: {error_msg}", exc_info=True)
            yield f"event: error\ndata: {error_msg}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
