import json
import httpx
from core.protocol import ChatEvent

async def stream_agent(messages):
    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": messages,
        "stream": True,
        "temperature": 0.2,
    }

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream(
            "POST",
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers={
                "Authorization": f"Bearer {YOUR_KEY}",
                "Content-Type": "application/json",
            },
        ) as response:
            async for line in response.aiter_lines():
                if not line.startswith("data:"):
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
                except:
                    continue
