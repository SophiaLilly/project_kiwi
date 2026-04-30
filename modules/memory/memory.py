# memory.py
# Memory management functions for conversation history

# Local Imports
from modules.llm_funcs.config import get_char_config_file, get_system_message, format_message_for_memory

# Partial Imports
from typing import Optional

# Full Imports
import json
import os
import tempfile
import threading


_config_cache = None
_history_file_path_cache = None
_history_cache = None
_cache_lock = threading.RLock()  # Reentrant lock for thread safety


def _get_cached_config():
    global _config_cache
    if _config_cache is None:
        _config_cache = get_char_config_file()
    return _config_cache


def get_history_file_path() -> str:
    global _history_file_path_cache
    if _history_file_path_cache is None:
        _history_file_path_cache = _get_cached_config()['history_file']
    return _history_file_path_cache


def get_history() -> list:
    global _history_cache
    with _cache_lock:
        if _history_cache is None:
            try:
                with open(get_history_file_path(), 'r', encoding='utf-8') as f:
                    _history_cache = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError, IOError):
                _history_cache = []
        return _history_cache.copy()  # Return copy to prevent external modification


def set_history(history) -> None:
    global _history_cache
    with _cache_lock:
        tmp_fd, tmp_path = tempfile.mkstemp()
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, separators=(',', ':'), indent=2)
            os.replace(tmp_path, get_history_file_path())
            _history_cache = history.copy()
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


def update_json_history(history, user_message, assistant_message) -> None:
    updated_history = history + [user_message, assistant_message]
    set_history(updated_history)


def get_working_memory(limit: int = 10) -> list:
    global _history_cache
    with _cache_lock:
        history = _history_cache or get_history()
        return history[-limit:]


def get_full_messages(user_message) -> list:
    messages = [get_system_message()]
    # messages.extend(get_history())
    messages.extend(get_working_memory())

    current_name = user_message["content"].split(":")[0]
    messages.append({
        "role": "system",
        "content": f"Current speaker: {current_name}"
    })

    messages.append(user_message)
    return messages


def clear_memory_cache() -> None:
    global _config_cache, _history_file_path_cache, _history_cache
    with _cache_lock:
        _config_cache = None
        _history_file_path_cache = None
        _history_cache = None
