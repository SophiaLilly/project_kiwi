# config.py
# Configuration management functions

# Full Imports
import yaml


def get_char_config_file():
    with open("character_config.yaml", 'r') as f:
        return yaml.safe_load(f)


def get_model():
    return get_char_config_file()['model']


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
