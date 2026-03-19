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

        # --- UPDATED THRESHOLDS ---
        # 0.01 is often too low (background noise triggers it). 0.02 is safer.
        self.silence_threshold = 0.03 
        # 3 chunks is too fast (approx 60-100ms). 
        # 15-20 chunks allows for a natural 0.5s pause between words.
        self.max_silence_chunks = 7 
        # Safety limit for a single sentence (approx 10-15 seconds of speech)
        self.max_buffer_chunks = 300 

    def is_speech(self, audio_chunk: bytes):
        audio = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
        # RMS energy is more stable than absolute mean
        energy = np.sqrt(np.mean(audio**2))
        return energy > self.silence_threshold

    async def add_chunk(self, audio_chunk: bytes):
        speech = self.is_speech(audio_chunk)

        if speech:
            if not self.speech_active:
                print("🎙️ Speech detected...")
            self.speech_active = True
            self.silence_chunks = 0
            self.buffer.append(audio_chunk)
        else:
            if self.speech_active:
                # Still append silence chunks while speech is active 
                # to keep the natural rhythm for the STT engine.
                self.buffer.append(audio_chunk)
                self.silence_chunks += 1

        # Logic: Only return segment if we have collected speech AND 
        # enough silence has passed to indicate the user is done.
        if self.speech_active and self.silence_chunks >= self.max_silence_chunks:
            return self._flush_buffer()

        # safety max buffer
        if len(self.buffer) >= self.max_buffer_chunks:
            return self._flush_buffer()

        return None

    def _flush_buffer(self):
        """Helper to reset state and return the collected audio."""
        segment = b"".join(self.buffer)
        self.buffer = []
        self.silence_chunks = 0
        self.speech_active = False
        return segment