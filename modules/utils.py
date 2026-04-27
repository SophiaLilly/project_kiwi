# utils.py
# Shared utility functions for the Kiwi project

# Local Imports

# Partial Imports

# Full Imports
import re


def split_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

