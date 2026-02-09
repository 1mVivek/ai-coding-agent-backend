"""
DeepSeek agent implementation with streaming support.

This module provides streaming chat functionality using the OpenRouter API
with the DeepSeek model. It includes proper error handling, logging, and
configurable parameters.
"""
import json
from typing import AsyncGenerator, Dict, Any, Optional
import httpx

from src.core.config import init_settings
from src.core.logger import get_logger
from src.core.exceptions import APIError, StreamError

# Initialize settings
settings = init_settings()
logger = get_logger(level=settings.log_level)


async def stream_agent(
    messages: list[dict],
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    model: Optional[str] = None,
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Stream chat completions from the DeepSeek model via OpenRouter.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        temperature: Model temperature (0-2). Defaults to config value.
        max_tokens: Maximum tokens to generate. Defaults to config value.
        model: Model name. Defaults to config value.
        
    Yields:
        Dict with 'type' and 'data' keys:
        - {"type": "token", "data": "text content"}
        - {"type": "done", "data": ""}
        
    Raises:
        APIError: When API request fails
        StreamError: When stream processing fails
    """
    # Use config defaults if not provided
    temperature = temperature if temperature is not None else settings.model_temperature
    max_tokens = max_tokens if max_tokens is not None else settings.model_max_tokens
    model = model or settings.model_name
    
    logger.info(
        f"Starting stream request: model={model}, "
        f"temperature={temperature}, max_tokens={max_tokens}, "
        f"messages_count={len(messages)}"
    )
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                settings.api_url,
                headers=headers,
                json=payload,
            ) as response:
                
                # Check for HTTP errors
                if response.status_code != 200:
                    error_body = await response.aread()
                    error_msg = f"API request failed with status {response.status_code}: {error_body.decode()}"
                    logger.error(error_msg)
                    raise APIError(error_msg, status_code=response.status_code)
                
                logger.debug("Stream connection established")
                token_count = 0

                async for line in response.aiter_lines():
                    if not line or not line.startswith("data:"):
                        continue

                    data = line.replace("data:", "").strip()

                    if data == "[DONE]":
                        logger.info(f"Stream completed. Total tokens: {token_count}")
                        yield {"type": "done", "data": ""}
                        break

                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0]["delta"]

                        if "content" in delta:
                            token_count += 1
                            yield {"type": "token", "data": delta["content"]}

                    except (json.JSONDecodeError, KeyError, IndexError) as e:
                        # Log but continue processing - partial failures shouldn't stop stream
                        logger.warning(f"Failed to parse stream chunk: {e}")
                        continue
                        
    except httpx.HTTPError as e:
        error_msg = f"HTTP error during streaming: {str(e)}"
        logger.error(error_msg)
        raise APIError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error during streaming: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise StreamError(error_msg) from e
