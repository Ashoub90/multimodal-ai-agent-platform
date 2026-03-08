"""Base class for speech-to-text providers.

Defines the interface that all STT implementations must follow. Providers such
as Whisper or Deepgram will subclass this.
"""


from abc import ABC, abstractmethod


class BaseSTT(ABC):
    @abstractmethod
    def transcribe(self, audio_stream):
        """Convert audio stream chunks into text."""
        pass
