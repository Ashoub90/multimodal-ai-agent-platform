import httpx
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

class ElevenLabsTTS:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID")
        
        # --- STEP 3: Add the optimization parameter to the URL ---
        # Value 4: Max latency optimizations + disables unnecessary text normalization.
        self.url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}?optimize_streaming_latency=4"
        
        # Limit to 2 concurrent requests to stay under the tier limit
        self._semaphore = asyncio.Semaphore(2)

    async def synthesize(self, text: str) -> bytes:
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg"
        }
        
        data = {
            "text": text,
            # --- STEP 2: Switch to the ultra-low latency Flash model ---
            "model_id": "eleven_flash_v2_5", 
            "voice_settings": {
                "stability": 0.45,
                "similarity_boost": 0.8, 
                "style": 0.0,            
                "use_speaker_boost": True
            }
        }

        async with self._semaphore:
            # Re-using the client or setting a lower timeout can also help
            async with httpx.AsyncClient(timeout=10.0) as client:
                try:
                    response = await client.post(self.url, json=data, headers=headers)
                    if response.status_code == 200:
                        return response.content
                    else:
                        print(f"❌ ElevenLabs Error: {response.text}")
                        return None
                except Exception as e:
                    print(f"❌ TTS Connection Error: {e}")
                    return None