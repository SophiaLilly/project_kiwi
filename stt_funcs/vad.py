# Local Imports

# Partial Imports
from faster_whisper import WhisperModel
from scipy.signal import resample_poly

# Full Imports
import numpy as np
import queue
import sounddevice as sd
import threading
import time
import torch


MIC_SR = 44100
TARGET_SR = 16000

FRAME_MS = 20
FRAME_SIZE_16K = 512
FRAME_SIZE_MIC = int(MIC_SR * FRAME_MS / 1000)

CHUNK_MS = 500
CHUNK_SIZE = int(MIC_SR * CHUNK_MS / 1000)

audio_queue = queue.Queue(maxsize=256)
buffer = []


silero_model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad')
(get_speech_timestamps, _, read_audio, _, _) = utils

whisper_model = WhisperModel("base", device="cuda", compute_type="float16")


def audio_callback(in_data, frame_count, time_info, status_flags):
    if status_flags:
        print(f"Audio callback status: {status_flags}")

    audio = in_data[:, 0].copy()
    try:
        audio_queue.put_nowait(audio)
    except queue.Full:
        audio_queue.get_nowait()
        audio_queue.put_nowait(audio)


def audio_consumer():
    print("Listening.")
    while True:
        audio = audio_queue.get()
        peak = np.max(np.abs(audio))
        print(f"Audio frame received | {peak=:.4f}")


# def vad_loop():
#     print("Listening.")
#     frame_buffer = []
#
#     while True:
#         frame = audio_queue.get()
#         frame_buffer.append(frame)
#
#         if len(frame_buffer) < 10:
#             continue
#
#         raw = np.concatenate(frame_buffer)
#         frame_buffer.clear()
#
#         audio_16k = resample_poly(raw, TARGET_SR, MIC_SR)
#
#         peak = np.max(np.abs(audio_16k)) + 1e-6
#         audio_16k = audio_16k / peak
#
#         num_chunks = len(audio_16k) // 512
#         if num_chunks == 0:
#             continue
#
#         trimmed = audio_16k[:num_chunks * 512]
#         chunks = trimmed.reshape(num_chunks, 512)
#
#         audio_tensor = torch.from_numpy(chunks).float()
#         speech_probs = silero_model(audio_tensor, TARGET_SR)
#
#         for prob in speech_probs:
#             speech_prob = prob.item()
#             if speech_prob > 0.7:
#                 print(f"SPEECH {speech_prob=:.3f}")
#             else:
#                 print(f"noise  {speech_prob=:.3f}")


def process_speech(audio_16k):
    peak = np.max(np.abs(audio_16k)) + 1e-6
    audio_16k = audio_16k / peak

    segments, _ = whisper_model.transcribe(audio_16k, language="en")
    text = "".join(s.text for s in segments).strip()

    if text:
        print("HEARD:", text)


def asr_loop():
    print("Listening.")
    frame_buffer = []
    triggered = False
    speech_buffer = []
    silence_count = 0

    START_THRESHOLD = 0.6
    END_THRESHOLD = 0.3
    MAX_SILENCE_FRAMES = 10

    while True:
        frame = audio_queue.get()
        frame_buffer.append(frame)

        if len(frame_buffer) < 10:
            continue

        raw = np.concatenate(frame_buffer)
        frame_buffer.clear()

        audio_16k = resample_poly(raw, TARGET_SR, MIC_SR)

        peak = np.max(np.abs(audio_16k)) + 1e-6
        audio_16k = audio_16k / peak

        num_chunks = len(audio_16k) // 512
        if num_chunks == 0:
            continue

        trimmed = audio_16k[:num_chunks * 512]
        chunks = trimmed.reshape(num_chunks, 512)

        audio_tensor = torch.from_numpy(chunks).float()
        speech_probs = silero_model(audio_tensor, TARGET_SR)

        for prob, chunk in zip(speech_probs, chunks):
            p = prob.item()

            if p > START_THRESHOLD:
                if not triggered:
                    print("Speech START")
                    triggered = True
                    speech_buffer = []

                speech_buffer.append(chunk)
                silence_count = 0

            else:
                if triggered:
                    silence_count += 1
                    speech_buffer.append(chunk)

                    if silence_count > MAX_SILENCE_FRAMES:
                        print("Speech END")

                        audio = np.concatenate(speech_buffer)
                        process_speech(audio)

                        triggered = False
                        speech_buffer = []
                        silence_count = 0



def run_asr():
    #vad_thread = threading.Thread(target=vad_loop, daemon=True)
    #vad_thread.start()
    asr_thread = threading.Thread(target=asr_loop)
    asr_thread.start()

    with sd.InputStream(
            samplerate=MIC_SR,
            channels=1,
            dtype="float32",
            blocksize=0,
            callback=audio_callback,
            device=4,
            latency="high"
    ):
        while True:
            time.sleep(1)


if __name__ == "__main__":
    run_asr()
