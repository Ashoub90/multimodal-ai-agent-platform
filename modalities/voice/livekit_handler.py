import os
from livekit.agents import Agent, AgentSession
from livekit.plugins import openai, silero, deepgram, elevenlabs

class RestaurantAssistant(Agent):
    def __init__(self):
        super().__init__(
            instructions="You are a helpful Egyptian restaurant assistant. Use Egyptian dialect (Ammiya). Be concise and friendly."
        )

def get_realtime_agent():
    llm = openai.LLM(model="gpt-4o-mini")

    # FIX: Using your specific Voice ID
    tts = elevenlabs.TTS(
        api_key=os.getenv("ELEVEN_API_KEY") or os.getenv("ELEVENLABS_API_KEY"),
        model="eleven_flash_v2_5",
        voice_id="9SPZl4Mlgwj7QT4gVprb" 
    )

    # Deepgram for fast Arabic STT
    stt = deepgram.STT(language="ar")

    # VAD speed fix (0.3s)
    vad = silero.VAD.load(min_silence_duration=0.3)
    
    session = AgentSession(
        llm=llm,
        tts=tts,
        stt=stt,
        vad=vad, 
    )
    
    return session, RestaurantAssistant()