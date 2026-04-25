import time

import torch

from llm_funcs import llm_scr
from tts_funcs.tts import generate_voice_clip, save_voice_clip, play_voice_clip


import queue
import re


def split_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def run(user_input):
    response = llm_scr.get_llm_response(user_input)
    print(f"< {response}")

    chunks = split_sentences(response)

    for i, chunk in enumerate(chunks):
        print(f"< {chunk}")
        vc = generate_voice_clip(chunk)
        save_voice_clip(vc)
        play_voice_clip("voice_clip.wav")

        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

        time.sleep(0.1)


if __name__ == "__main__":
    print('Running main.py as main.')

    user_input = input("> ")
    run(user_input)
