import os
from openai import OpenAI
from prompts import SYSTEM_PROMPT

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY") or OPENROUTER_KEY

client = OpenAI(
    api_key=OPENAI_KEY,   # 👈 force non-empty key
    base_url="https://openrouter.ai/api/v1",
)

def run_agent(message: str):
    response = client.chat.completions.create(
        model="deepseek/deepseek-coder",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ],
        temperature=0.2,
        max_tokens=2000
    )
    return response.choices[0].message.content
