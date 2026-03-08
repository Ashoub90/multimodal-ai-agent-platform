"""ElevenLabs text-to-speech implementation.

Interacts with the ElevenLabs API to generate spoken audio from text.
"""

from .base_tts import BaseTTS


class ElevenLabsTTS(BaseTTS):
    def __init__(self, api_key: str, voice: str = "default"):
        self.api_key = api_key
        self.voice = voice

    def synthesize(self, text: str):
        # placeholder for API call
        pass
