# llm.py

# Local Imports

# Partial Imports

# Full Imports
import json
import requests
import yaml


def get_char_config_file():
    with open("character_config.yaml", 'r') as f:
        return yaml.safe_load(f)


def get_model():
    return get_char_config_file()['model']


def get_history_file_path():
    return get_char_config_file()['history_file']


def get_history_file_contents():
    try:
        with open(get_history_file_path(), 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def get_system_message():
    return {
        "role": "system",
        "content": get_char_config_file()['presets']['default']['system_prompt']
    }


def get_user_input(user_input):
    return {
        "role": "user",
        "content": user_input
    }


def get_full_messages(user_input):
    messages = [get_system_message()]
    messages.extend(get_history_file_contents())
    messages.append(get_user_input(user_input))
    return messages


def set_history(history):
    with open(get_history_file_path(), "w") as f:
        json.dump(history, f, indent=2)


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
