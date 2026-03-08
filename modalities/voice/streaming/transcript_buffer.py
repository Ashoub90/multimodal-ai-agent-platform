"""Buffer transcripts generated during streaming sessions.

Useful for providing partial transcripts to the frontend or for context
passing into the agent pipeline.
"""


class TranscriptBuffer:
    def __init__(self):
        self._buffer = []

    def append(self, text: str):
        self._buffer.append(text)

    def get_all(self):
        return "".join(self._buffer)

    def clear(self):
        self._buffer.clear()
