import os
import requests
import json
from prompts import SYSTEM_PROMPT

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
}

def stream_agent(message: str):
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

    try:
        with requests.post(
            API_URL,
            headers=HEADERS,
            json=payload,
            stream=True,
            timeout=60,
        ) as r:

            if r.status_code != 200:
                yield "The AI service is temporarily unavailable."
                return

            for line in r.iter_lines(decode_unicode=True):
                if not line:
                    continue

                # OpenAI-style SSE lines
                if line.startswith("data:"):
                    data = line.replace("data:", "").strip()

                    if data == "[DONE]":
                        break

                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0]["delta"]

                        if "content" in delta:
                            yield delta["content"]

                    except Exception:
                        continue

    except Exception:
        yield "The AI service is temporarily unavailable."
