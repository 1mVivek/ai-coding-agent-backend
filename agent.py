import os
import json
import httpx
from prompts import SYSTEM_PROMPT

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

API_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
}

async def stream_agent(message: str):
    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        "temperature": 0.2,
        "max_tokens": 2000,
        "stream": True,
    }

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream(
            "POST",
            API_URL,
            headers=HEADERS,
            json=payload,
        ) as response:

            async for line in response.aiter_lines():
                if not line:
                    continue

                # OpenAI / OpenRouter stream format
                if not line.startswith("data:"):
                    continue

                data = line.replace("data:", "").strip()

                if data == "[DONE]":
                    break

                try:
                    chunk = json.loads(data)
                    delta = chunk["choices"][0]["delta"]

                    if "content" in delta:
                        # IMPORTANT: send BYTES
                        yield delta["content"].encode("utf-8")

                except Exception:
                    continue
