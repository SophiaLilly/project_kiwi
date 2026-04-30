# main.py
# Entry point for the Kiwi Project

# Local Imports

# Partial Imports

# Full Imports
import asyncio
import queue
import sys
import threading
import time


# MODE can be set to "voice" or "cli"
# - "voice": Full pipeline with voice input/output
# - "cli": Simple CLI mode with text input/output
MODE = "discord"


class VoiceContext:
    def __init__(self):
        self.tts_queue = queue.Queue(maxsize=32)
        self.play_queue = queue.Queue(maxsize=32)


def run_voice_mode():
    from modules.asr_funcs.asr import run_asr
    from modules.workers import asr_consumer, tts_consumer, audio_player

    ctx = VoiceContext()

    threading.Thread(target=run_asr, daemon=True).start()
    threading.Thread(target=asr_consumer, daemon=True, args=(ctx,)).start()
    threading.Thread(target=tts_consumer, daemon=True, args=(ctx,)).start()
    threading.Thread(target=audio_player, daemon=True, args=(ctx,)).start()


def run_cli_mode():
    from modules.workers import cli_consumer

    cli_consumer()


def run_discord_mode():
    from modules.discord.dsc import main

    asyncio.run(main())


if __name__ == "__main__":
    print(f'Running main.py in {MODE.upper()} mode.')

    if MODE.lower() == "voice":
        run_voice_mode()
    elif MODE.lower() == "cli":
        run_cli_mode()
    elif MODE.lower() == "discord":
        run_discord_mode()
    else:
        print(f"Error: Unknown mode '{MODE}'. Use 'voice' or 'cli'.")
        sys.exit()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down.")
        sys.exit()

