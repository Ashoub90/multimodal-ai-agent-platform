"""OpenAI Whisper STT implementation.

This module will call the Whisper API or local model to convert incoming audio
to text.
"""

from .base_stt import BaseSTT


class WhisperSTT(BaseSTT):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def transcribe(self, audio_stream):
        # placeholder for actual transcription logic
        pass
