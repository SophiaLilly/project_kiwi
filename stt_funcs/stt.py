from faster_whisper import WhisperModel

model = WhisperModel("base", device="cuda", compute_type="float16")
segments, info = model.transcribe("input.wav")
text = "".join([seg.text for seg in segments])
print(text)