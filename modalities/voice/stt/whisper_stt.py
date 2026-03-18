"""OpenAI Whisper STT implementation.

This module will call the Whisper API or local model to convert incoming audio
to text.
"""

import whisper
import numpy as np

class WhisperSTT:
    def __init__(self):

        self.model = whisper.load_model("tiny")

    def transcribe(self, audio_bytes: bytes):
        if not audio_bytes:
            return ""

        # Convert the raw Int16 bytes back into a Float32 array for Whisper
        audio_data = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        
        # Transcribe directly from the array
        # We set fp16=False because your logs show you are on a CPU
        result = self.model.transcribe(audio_data, fp16=False)
        
        text = result.get("text", "").strip()
        return text
