import os
from openai import OpenAI
from prompts import SYSTEM_PROMPT

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
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
