"""Placeholder for Deepgram STT provider.

Not implemented yet; future extension point for alternate STT services.
"""

from .base_stt import BaseSTT


class DeepgramSTT(BaseSTT):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def transcribe(self, audio_stream):
        pass
