from openai import OpenAI
from prompts import SYSTEM_PROMPT
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_agent(user_message: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content
