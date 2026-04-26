# Local Imports

# Partial Imports
from chatterbox.tts_turbo import ChatterboxTurboTTS

# Full Imports
import sounddevice as sd
import soundfile as sf
import torchaudio as ta
import torch


model = ChatterboxTurboTTS.from_pretrained(device="cuda")
model.t3.to(dtype=torch.bfloat16)


def generate_voice_clip(text):
    with torch.no_grad(), torch.amp.autocast("cuda"):
        wav = model.generate(text, audio_prompt_path="/home/elodie/Projects/riko_project_clone/character_files/main_sample.wav")
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()
    return wav


def save_voice_clip(wav, file_name="voice_clip.wav"):
    ta.save(file_name, wav, model.sr)


def play_voice_clip(path):
    data, samplerate = sf.read(path)
    sd.play(data, samplerate)
    sd.wait()


if __name__ == "__main__":
    print("Running tts.py as main. Is this intended?")
    vc = generate_voice_clip("Hi there, my name is Kiwi!")
    save_voice_clip(vc)
    play_voice_clip("/home/elodie/Projects/riko_project_clone/tts_funcs/voice_clip.wav")
