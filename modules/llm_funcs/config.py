# config.py
# Configuration management functions

# Local Imports

# Partial Imports
from datetime import datetime

# Full Imports
import pathlib
import yaml


def get_char_config_file():
    with open("/home/elodie/Projects/project_kiwi/character_config.yaml", 'r') as f:
        return yaml.safe_load(f)


def get_model():
    return get_char_config_file()['model']


def get_system_message():
    return {
        "role": "system",
        "content": get_char_config_file()['presets']['default']['system_prompt']
    }


def format_message_for_memory(
        role: str = "user",
        name: str = "console",
        user_id: int = 0,
        content: str = None,
        timestamp: str = str(datetime.now()),
) -> dict[str, str | int | None]:
    if role == "user":
        content = f"{name}: {content}"

    return {
        "role": role,
        "content": content,
        "user_id": user_id,
        "timestamp": timestamp
    }
