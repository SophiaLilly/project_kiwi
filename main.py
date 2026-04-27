# main.py
# Entry point for the Kiwi Project

# Local Imports

# Partial Imports

# Full Imports
import queue
import sys
import threading
import time


# MODE can be set to "voice" or "cli"
# - "voice": Full pipeline with voice input/output
# - "cli": Simple CLI mode with text input/output
MODE = "CLI"


class VoiceContext:
    def __init__(self):
        self.tts_queue = queue.Queue(maxsize=32)
        self.play_queue = queue.Queue(maxsize=32)


def run_voice_mode():
    from modules.asr_funcs.asr import run_asr
    from modules.tts_funcs.workers import tts_worker, audio_player
    from modules.asr_funcs.workers import asr_consumer

    ctx = VoiceContext()

    threading.Thread(target=run_asr, daemon=True).start()
    threading.Thread(target=asr_consumer, daemon=True, args=(ctx,)).start()
    threading.Thread(target=tts_worker, daemon=True, args=(ctx,)).start()
    threading.Thread(target=audio_player, daemon=True, args=(ctx,)).start()


def run_cli_mode():
    from modules.llm_funcs.cli_worker import cli_consumer

    cli_consumer()


if __name__ == "__main__":
    print(f'Running main.py in {MODE.upper()} mode.')

    if MODE.lower() == "voice":
        run_voice_mode()
    elif MODE.lower() == "cli":
        run_cli_mode()
    else:
        print(f"Error: Unknown mode '{MODE}'. Use 'voice' or 'cli'.")
        sys.exit()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down.")
        sys.exit()

