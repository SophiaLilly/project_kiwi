# api.py

# Local Internal Imports
from .config import get_model

# Local External Imports

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
            "options": {
                "temperature": 0.7,
            }
        },
        stream=True
    )

    for line in response.iter_lines():
        if not line:
            continue

        data = json.loads(line.decode())
        if "message" in data and "content" in data["message"]:
            yield data["message"]["content"]


def get_raw_response(messages):
    return "".join(get_stream(messages))