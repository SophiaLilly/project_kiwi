# asr_worker.py
# Main worker threads orchestrating the full pipeline

# Local Imports
from modules.llm_funcs import llm
from modules.asr_funcs.asr import get_text_queue
from modules.utils import split_sentences

# Partial Imports

# Full Imports
import time


def asr_consumer(ctx):
    while True:
        text = get_text_queue().get()
        print(f"> {text}")

        response = llm.run_llm_cycle(text)
        print(f"< {response}")

        chunks = split_sentences(response)
        for chunk in chunks:
            ctx.tts_queue.put(chunk)
            time.sleep(0.01)
