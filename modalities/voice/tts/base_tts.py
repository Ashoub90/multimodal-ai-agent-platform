"""Abstract base class for text-to-speech engines.

Defines a simple interface for converting text into audio streams. Concrete
implementations will support providers like ElevenLabs, Amazon Polly, etc.
"""

from abc import ABC, abstractmethod


class BaseTTS(ABC):
    @abstractmethod
    def synthesize(self, text: str):
        """Return audio bytes (or stream) for the given text."""
        pass
