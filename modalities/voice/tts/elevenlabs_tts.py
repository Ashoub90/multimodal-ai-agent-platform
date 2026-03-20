import httpx
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

class ElevenLabsTTS:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID")
        
        # Optimization parameter added to URL (Step 3)
        self.url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}?optimize_streaming_latency=4"
        
        # Limit to 2 concurrent requests to stay under tier limits
        self._semaphore = asyncio.Semaphore(2)

        # PERSISTENT CLIENT: Created once at initialization
        # This keeps the TCP/TLS connection open for reuse (Keep-Alive)
        self.client = httpx.AsyncClient(timeout=10.0)

    async def synthesize(self, text: str) -> bytes:
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg"
        }
        
        data = {
            "text": text,
            "model_id": "eleven_flash_v2_5", # Ultra-low latency model
            "voice_settings": {
                "stability": 0.45,
                "similarity_boost": 0.8, 
                "style": 0.0,            
                "use_speaker_boost": True
            }
        }

        async with self._semaphore:
            try:
                # Use the pre-existing self.client instead of creating a new one with 'async with'
                response = await self.client.post(self.url, json=data, headers=headers)
                if response.status_code == 200:
                    return response.content
                else:
                    print(f"❌ ElevenLabs Error: {response.text}")
                    return None
            except Exception as e:
                print(f"❌ TTS Connection Error: {e}")
                return None

    async def close(self):
        """Optional: Call this during app shutdown to clean up resources."""
        await self.client.aclose()