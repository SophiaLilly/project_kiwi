# llm.py

# Local Imports
from .config import get_char_config_file, get_model, get_system_message, get_user_input
from .memory import get_history_file_contents, set_history, get_full_messages

# Partial Imports

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
        },
        stream=True
    )

    for line in response.iter_lines():
        if not line:
            continue

        data = json.loads(line.decode())
        yield data["message"]["content"]


def get_llm_response(user_input):
    history = get_history_file_contents()
    user_message = get_user_input(user_input)
    messages = get_full_messages(user_input)

    response = "".join(get_stream(messages))

    assistant_message = {
        "role": "assistant",
        "content": response
    }

    updated_history = history + [user_message, assistant_message]
    set_history(updated_history)

    return response


if __name__ == "__main__":
    print('Running llm.py as main. Is this intended?')
    print(get_llm_response("Hello."))
