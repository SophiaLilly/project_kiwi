# memory_extraction.py


# Local Internal Imports
from .api import get_raw_response

# Local External Imports

# Partial Imports

# Full Imports


def extract_memory(user_message, response):
    prompt = f"""
Extract a useful long-term memory from this interaction.

Only return a memory if it is:
- a fact about a user
- a preference
- a definition
- a stable trait

Otherwise return NONE.

Message: {user_message.get("content", "")}
Response: {response}
"""
    messages = {
        "role": "user",
        "content": prompt
    }
    response = get_raw_response(messages)
    return response
