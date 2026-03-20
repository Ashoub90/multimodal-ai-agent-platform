import asyncio
from modalities.voice.tts.piper_tts import PiperTTS

async def test():
    tts = PiperTTS("modalities/voice/tts/en_US-lessac-medium.onnx")
    audio = await tts.synthesize("Hello world, testing audio synthesis.")
    print(f"Final Audio Size: {len(audio)} bytes")

if __name__ == "__main__":
    asyncio.run(test())