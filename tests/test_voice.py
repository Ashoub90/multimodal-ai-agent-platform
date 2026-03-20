import os
import wave
import numpy as np
from piper.voice import PiperVoice

# 1. Setup paths
model_path = "modalities/voice/tts/ar_JO-kareem-medium.onnx"
# Update this to your absolute path if it fails
piper_dir = os.path.abspath("Piper")
os.environ["ESPEAK_DATA_PATH"] = os.path.join(piper_dir, "espeak-ng-data")
os.environ["PATH"] = piper_dir + os.pathsep + os.environ["PATH"]

# 2. Load Voice
print("Loading model...")
voice = PiperVoice.load(model_path)

# 3. Test Synthesis
print("Synthesizing 'صباح الخير'...")
with wave.open("test_output.wav", "wb") as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(voice.config.sample_rate)
    
    for result in voice.synthesize("صباح الخير يا فندم"):
        audio_data = np.array(result.audio, dtype=np.int16)
        wav_file.writeframes(audio_data.tobytes())

print("✅ Success! Open 'test_output.wav' to hear it.")