from core.system_prompt import SYSTEM_PROMPT

def build_messages(memory, user_message: str):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(memory.get())
    messages.append({"role": "user", "content": user_message})
    return messages
