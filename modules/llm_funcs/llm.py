# llm.py
from pprint import pprint

# Local Imports
from modules.llm_funcs.config import get_char_config_file, get_model, get_system_message, format_message_for_memory
from modules.llm_funcs.memory import get_history, set_history, get_full_messages

# Partial Imports
from datetime import datetime

# Full Imports
import json
import requests


def get_stream(messages):
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": get_model(),
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": 0.5,
            }
        },
        stream=True
    )

    for line in response.iter_lines():
        if not line:
            continue

        data = json.loads(line.decode())
        yield data["message"]["content"]


def get_llm_response(role: str = "user", name: str = "console", user_id: int = 0, user_input: str = None):
    history = get_history()

    user_message = format_message_for_memory(role=role, name=name, user_id=user_id, content=user_input, timestamp=str(datetime.now()))

    messages = get_full_messages(user_message)
    pprint(messages)
    response = "".join(get_stream(messages))

    assistant_message = format_message_for_memory(role="assistant", name="Kiwi", content=response, timestamp=str(datetime.now()))

    updated_history = history + [user_message, assistant_message]
    set_history(updated_history)

    return response


if __name__ == "__main__":
    print('Running llm.py as main. Is this intended?')
    print(get_llm_response("Hello."))
