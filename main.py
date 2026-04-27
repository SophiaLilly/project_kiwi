# main.py
# Entry point for the Kiwi Project

# Local Imports

# Partial Imports

# Full Imports
import queue
import threading
import time


# MODE can be set to "voice" or "cli"
# - "voice": Full pipeline with voice input/output
# - "cli": Simple CLI mode with text input/output
MODE = "CLI"


def run_voice_mode():
    from modules.asr_funcs.asr import run_asr
    from modules.tts_funcs.workers import tts_worker, audio_player
    from modules.asr_funcs.workers import asr_consumer

    tts_queue = queue.Queue()
    play_queue = queue.Queue()

    threading.Thread(target=run_asr).start()
    threading.Thread(target=asr_consumer, args=(tts_queue,)).start()
    threading.Thread(target=tts_worker, args=(tts_queue, play_queue)).start()
    threading.Thread(target=audio_player, args=(play_queue,)).start()


def run_cli_mode():
    from modules.llm_funcs.cli_worker import cli_consumer

    threading.Thread(target=cli_consumer, daemon=True).start()


if __name__ == "__main__":
    print(f'Running main.py in {MODE.upper()} mode.')

    if MODE.lower() == "voice":
        run_voice_mode()
    elif MODE.lower() == "cli":
        run_cli_mode()
    else:
        print(f"Error: Unknown mode '{MODE}'. Use 'voice' or 'cli'.")
        exit(1)

    while True:
        time.sleep(1)
