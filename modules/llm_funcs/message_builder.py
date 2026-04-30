# message_builder.py

# Local Imports
from modules.llm_funcs.config import format_message_for_memory
from modules.memory.memory import get_full_messages
from modules.memory.vector_db import is_enabled, search_memories

# Partial Imports
from datetime import datetime

# Full Imports


def inject_semantic_context(messages, user_input):
    if not is_enabled():
        return messages

    results = search_memories(user_input, n_results=5)
    filtered = [
        r for r in results
        if r.get("relevance_score", 0) > 0.75
    ]
    if not filtered:
        return messages

    context_text = "Relevant past context (may be imperfect):\n"
    for r in filtered:
        meta = r.get("metadata", {})
        content = meta.get("content", "")
        context_text += f"- {content}\n"

    messages.insert(1, {
        "role": "system",
        "content": context_text
    })
    return messages


def build_user_message(role, name, user_id, content):
    return format_message_for_memory(
        role=role,
        name=name,
        user_id=user_id,
        content=content,
        timestamp=str(datetime.now())
    )


def build_assistant_message(response):
    return format_message_for_memory(
        role="assistant",
        name="Kiwi",
        user_id=0,
        content=response,
        timestamp=str(datetime.now())
    )


def build_messages(user_message, user_input):
    messages = get_full_messages(user_message)
    return inject_semantic_context(messages, user_input)


if __name__ == "__main__":
    print("Running message_builder.py as main. Is this intended?")
