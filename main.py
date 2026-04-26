# main.py

# Local Imports
import threading

from llm_funcs import llm_scr
from stt_funcs.vad import get_text_queue, run_asr
from tts_funcs.tts import generate_voice_clip, save_voice_clip, play_voice_clip

# Partial Imports

# Full Imports
import queue
import re
import sounddevice as sd
import soundfile as sf
import time
import torch


tts_queue = queue.Queue()
play_queue = queue.Queue()


def split_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def tts_worker():
    while True:
        chunk = tts_queue.get()
        try:
            vc = generate_voice_clip(chunk)
            save_voice_clip(vc)
            play_queue.put(vc)

            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()

        except Exception as e:
            print(f"TTS failed (continuing without voice): {e}")



def audio_player():
    current = None

    while True:
        try:
            current = play_queue.get_nowait()
        except queue.Empty:
            time.sleep(0.01)
            continue

        wav, sr = current
        sd.play(wav, sr, blocking=False)


def asr_consumer():
    while True:
        text = get_text_queue().get()
        print(f"> {text}")

        response = llm_scr.get_llm_response(text)
        print(f"< {response}")

        chunks = split_sentences(response)
        for chunk in chunks:
            tts_queue.put(chunk)
            time.sleep(0.01)


if __name__ == "__main__":
    print('Running main.py as main.')

    threading.Thread(target=run_asr).start()
    threading.Thread(target=asr_consumer).start()
    threading.Thread(target=tts_worker).start()
    threading.Thread(target=audio_player).start()

    while True:
        time.sleep(1)
