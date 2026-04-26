import sounddevice as sd
import numpy as np
import queue
import torch
from scipy.signal import resample_poly


MIC_SR = 44100
TARGET_SR = 16000

FRAME_MS = 20
FRAME_SIZE_16K = 512
FRAME_SIZE_MIC = int(MIC_SR * FRAME_MS / 1000)

CHUNK_MS = 500
CHUNK_SIZE = int(MIC_SR * CHUNK_MS / 1000)

audio_queue = queue.Queue()
buffer = []


model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad')
(get_speech_timestamps, _, read_audio, _, _) = utils


def audio_callback(in_data, frame_count, time_info, status_flags):
    if status_flags:
        print(f"Audio callback status: {status_flags}")

    audio = in_data[:, 0].copy()

    if len(audio) != FRAME_SIZE_MIC:
        print(f"Unexpected frame size: {len(audio)}")

    audio_16k = resample_poly(audio, TARGET_SR, MIC_SR)

    if len(audio_16k) > 512:
        audio_16k = audio_16k[:512]
    elif len(audio_16k) < 512:
        audio_16k = np.pad(audio_16k, (0, 512 - len(audio_16k)), mode='constant')

    audio_queue.put(audio_16k)


def audio_consumer():
    print("Listening.")
    while True:
        audio = audio_queue.get()
        peak = np.max(np.abs(audio))
        print(f"Audio frame received | {peak=:.4f}")


def vad_loop():
    print("Listening.")
    while True:
        frame = audio_queue.get()
        audio_tensor = torch.from_numpy(frame).float()
        speech_prob = model(audio_tensor, TARGET_SR).item()
        #print(f"{speech_prob=:.3f}")

        if speech_prob >= 0.6:
            print(f"Speech {speech_prob=:.3f}")
        else:
            print(f"No speech {speech_prob=:.3f}")


def run():
    with sd.InputStream(
            samplerate=MIC_SR,
            channels=1,
            dtype="float32",
            blocksize=FRAME_SIZE_MIC,
            callback=audio_callback,
            device=4,
    ):
        vad_loop()


if __name__ == "__main__":
    run()
