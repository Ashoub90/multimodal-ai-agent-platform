"""Manage audio streams between frontend and backend.

Responsible for buffering, multiplexing, and providing hooks for
transcription and TTS services.
"""


import numpy as np


class AudioStreamManager:

    def __init__(self):
        self.buffer = []
        self.silence_chunks = 0
        self.speech_active = False

        # thresholds
        self.silence_threshold = 0.01
        self.max_silence_chunks = 3
        self.max_buffer_chunks = 40

    def is_speech(self, audio_chunk: bytes):
        audio = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
        energy = np.abs(audio).mean()
        return energy > self.silence_threshold

    async def add_chunk(self, audio_chunk: bytes):

        speech = self.is_speech(audio_chunk)

        if speech:
            self.speech_active = True
            self.silence_chunks = 0
            self.buffer.append(audio_chunk)

        else:
            if self.speech_active:
                self.silence_chunks += 1

        # speech ended
        if self.speech_active and self.silence_chunks >= self.max_silence_chunks:
            segment = b"".join(self.buffer)

            self.buffer = []
            self.silence_chunks = 0
            self.speech_active = False

            return segment

        # safety max buffer
        if len(self.buffer) >= self.max_buffer_chunks:
            segment = b"".join(self.buffer)

            self.buffer = []
            self.silence_chunks = 0
            self.speech_active = False

            return segment

        return None
