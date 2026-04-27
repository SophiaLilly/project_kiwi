# main.py
# Entry point for the Kiwi Project


# Local Imports
from modules.asr_funcs.asr import run_asr
from modules.tts_funcs.workers import tts_worker, audio_player
from modules.asr_funcs.workers import asr_consumer

# Full Imports
import queue
import threading
import time


if __name__ == "__main__":
    print('Running main.py as main.')

    # Create queues for inter-thread communication
    tts_queue = queue.Queue()
    play_queue = queue.Queue()

    # Start all worker threads
    threading.Thread(target=run_asr).start()
    threading.Thread(target=asr_consumer, args=(tts_queue,)).start()
    threading.Thread(target=tts_worker, args=(tts_queue, play_queue)).start()
    threading.Thread(target=audio_player, args=(play_queue,)).start()

    # Keep the main thread alive
    while True:
        time.sleep(1)
