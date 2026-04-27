# tts_funcs/workers.py
# TTS worker threads for voice generation and playback

# Local Imports
from modules.tts_funcs.tts import generate_voice_clip, save_voice_clip

# Partial Imports

# Full Imports
import queue
import sounddevice as sd
import time
import torch




def tts_worker(tts_queue, play_queue):
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


def audio_player(play_queue):
    current = None

    while True:
        try:
            current = play_queue.get_nowait()
        except queue.Empty:
            time.sleep(0.01)
            continue

        wav, sr = current
        sd.play(wav, sr, blocking=False)

