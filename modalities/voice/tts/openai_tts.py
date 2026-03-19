import os
import io
import wave
import asyncio
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAITTS:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # 'onyx' is excellent for a professional male persona
        self.voice = "onyx" 

    async def synthesize(self, text: str) -> bytes:
        if not text.strip():
            return b""

        try:
            # Wrap the synchronous OpenAI call to avoid blocking the event loop
            def _generate():
                return self.client.audio.speech.create(
                    model="tts-1",
                    voice=self.voice,
                    input=text,
                    response_format="pcm" 
                )

            response = await asyncio.to_thread(_generate)
            raw_pcm_data = response.content
            
            # Wrap PCM in a WAV container for the browser's AudioContext
            buffer = io.BytesIO()
            with wave.open(buffer, "wb") as wav_file:
                wav_file.setnchannels(1)          # Mono
                wav_file.setsampwidth(2)         # 16-bit
                wav_file.setframerate(24000)      # OpenAI default
                wav_file.writeframes(raw_pcm_data)
            
            return buffer.getvalue()
            
        except Exception as e:
            print(f"❌ OpenAI TTS Error: {e}")
            return b""