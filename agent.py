import os
import requests
from prompts import SYSTEM_PROMPT

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY is missing")

API_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://your-app-name.com",
    "X-Title": "AI Coding Agent",
}

def run_agent(message: str):
    payload = {
        "model": "deepseek/deepseek-coder",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ],
        "temperature": 0.2,
        "max_tokens": 2000
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()

    data = response.json()
    return data["choices"][0]["message"]["content"]
