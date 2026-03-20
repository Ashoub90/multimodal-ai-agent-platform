import os
from piper.voice import PiperVoice

model_path = "modalities/voice/tts/ar_JO-kareem-medium.onnx"
piper_dir = os.path.abspath("Piper")
os.environ["ESPEAK_DATA_PATH"] = os.path.join(piper_dir, "espeak-ng-data")
os.environ["PATH"] = piper_dir + os.pathsep + os.environ["PATH"]

voice = PiperVoice.load(model_path)

# Grab just one chunk and look inside
for result in voice.synthesize("صباح الخير"):
    print(f"Object Type: {type(result)}")
    print(f"Available Attributes/Keys: {dir(result)}")
    try:
        print(f"Dictionary view: {result.__dict__}")
    except:
        pass
    break