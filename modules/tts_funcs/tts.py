# tts.py
# Local Imports

# Partial Imports
from chatterbox.tts_turbo import ChatterboxTurboTTS

# Full Imports
import sounddevice as sd
import soundfile as sf
import torchaudio as ta
import torch


model = None
original_path = "character_files/main_sample.wav"


def get_model():
    global model
    if model is None:
        print("Loading TTS model...")
        model = ChatterboxTurboTTS.from_pretrained(device="cuda")
        model.t3.to(device="cuda")
        model.t3.eval()
        print("TTS model loaded.")
    return model


def generate_voice_clip(text):
    print("Generating voice clip.")
    model = get_model()

    with torch.no_grad(), torch.amp.autocast("cuda"):
        wav = model.generate(
            text,
            audio_prompt_path=original_path,
        )
    return wav.detach().cpu().clone(), model.sr


def save_voice_clip(wav, file_name="voice_clip.wav"):
    model = get_model()
    ta.save(file_name, wav, model.sr)


def play_voice_clip(path):
    data, samplerate = sf.read(path)
    sd.play(data, samplerate)
    sd.wait()


if __name__ == "__main__":
    print("Running tts.py as main. Is this intended?")
    vc = generate_voice_clip("Hi there, my name is Kiwi!")
    save_voice_clip(vc)
    play_voice_clip("/modules/tts_funcs/voice_clip.wav")
