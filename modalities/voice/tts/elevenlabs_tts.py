import httpx
import os
from dotenv import load_dotenv

load_dotenv()

class ElevenLabsTTS:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID")
        self.url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"

    async def synthesize(self, text: str) -> bytes:
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg"
        }
        
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2", 
            "voice_settings": {
                "stability": 0.45,       # Slightly lower for more natural Egyptian intonation
                "similarity_boost": 0.8, 
                "style": 0.0,            
                "use_speaker_boost": True
            }
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
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