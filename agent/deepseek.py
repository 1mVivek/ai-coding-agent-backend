import os
import json
import httpx

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY is not set")

API_URL = "https://openrouter.ai/api/v1/chat/completions"


async def stream_agent(messages: list[dict]):
    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 2000,
        "stream": True,
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream(
            "POST",
            API_URL,
            headers=headers,
            json=payload,
        ) as response:

            if response.status_code != 200:
                raise RuntimeError(await response.aread())

            async for line in response.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue

                data = line.replace("data:", "").strip()

                if data == "[DONE]":
                    yield {"type": "done", "data": ""}
                    break

                try:
                    chunk = json.loads(data)
                    delta = chunk["choices"][0]["delta"]

                    if "content" in delta:
                        yield {"type": "token", "data": delta["content"]}

                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
