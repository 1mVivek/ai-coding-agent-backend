import os
import requests
from prompts import SYSTEM_PROMPT

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

API_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://your-app-name.com",
    "X-Title": "AI Coding Agent",
}

def run_agent_stream(message: str):
    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ],
        "temperature": 0.2,
        "max_tokens": 2000,
        "stream": True   # 🔥 CRITICAL
    }

    with requests.post(API_URL, headers=HEADERS, json=payload, stream=True) as r:
        if r.status_code != 200:
            yield f"[ERROR {r.status_code}] {r.text}"
            return

        for line in r.iter_lines():
            if not line:
                continue

            decoded = line.decode("utf-8")

            if decoded.startswith("data: "):
                data = decoded.replace("data: ", "").strip()

                if data == "[DONE]":
                    break

                try:
                    chunk = eval(data)  # OpenRouter sends JSON per chunk
                    delta = chunk["choices"][0]["delta"]

                    if "content" in delta:
                        yield delta["content"]

                except Exception:
                    continue
