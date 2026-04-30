# llm.py

# Local Internal Imports
from .api import get_raw_response
from .memory_extraction import extract_memory
from .message_builder import (
    build_user_message,
    build_assistant_message,
    build_messages
)

# Local External Imports
from modules.memory import (
    get_history,
    store_vector_memory,
    update_json_history
)

# Partial Imports

# Full Imports


def run_llm_cycle(
        role: str = "user",
        name: str = "console",
        user_id: int = 0,
        user_input: str = None
):
    history = get_history()

    user_message = build_user_message(role, name, user_id, user_input)
    messages = build_messages(user_message, user_input)

    response = get_raw_response(messages)

    assistant_message = build_assistant_message(response)

    update_json_history(history, user_message, assistant_message)
    memory = extract_memory(user_message, response)
    store_vector_memory(memory, user_id)

    return response


if __name__ == "__main__":
    print('Running llm.py as main. Is this intended?')
