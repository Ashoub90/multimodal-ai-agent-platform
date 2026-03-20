from livekit.agents import Agent, AgentSession
from livekit.plugins import openai, silero
import os

class RestaurantAssistant(Agent):
    def __init__(self):
        super().__init__(
            instructions="You are a helpful Egyptian restaurant assistant. Use Egyptian dialect."
        )

def get_realtime_agent():
    # session no longer takes 'agent' as an argument in 1.5.0
    session = AgentSession(
        stt=openai.STT(),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(),
        vad=silero.VAD.load(),
    )
    # Return both so the entrypoint can use them
    return session, RestaurantAssistant()