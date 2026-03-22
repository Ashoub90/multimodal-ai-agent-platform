import os
from livekit.agents import Agent, AgentSession
from livekit.agents.llm import LLM
from livekit.plugins import silero, deepgram, elevenlabs
from contextlib import asynccontextmanager


from simple_agent import run_agent


# 🔥 CLEAN CUSTOM LLM
class AgentLLM(LLM):

    @asynccontextmanager
    async def chat(self, *, messages=None, input=None, **kwargs):
        try:
            chat_ctx = kwargs.get("chat_ctx")

            user_text = ""

            if chat_ctx:
                msgs = chat_ctx.messages()

                if msgs:
                    last_msg = msgs[-1]

                    raw = getattr(last_msg, "content", None) or getattr(last_msg, "text", "")

                    # 🔥 FIX: normalize to string
                    if isinstance(raw, list):
                        user_text = " ".join(str(x) for x in raw)
                    else:
                        user_text = str(raw)

            print("🔥 CALLED WITH:", user_text)

            response = await run_agent(user_text)

            async def stream():
                for word in response.split():
                    yield word + " "

            yield stream()

        except Exception as e:
            async def error_stream():
                yield f"حصل خطأ: {str(e)}"

            yield error_stream()


class RestaurantAssistant(Agent):
    def __init__(self):
        super().__init__(
            instructions="You are a helpful Egyptian restaurant assistant. Use Egyptian dialect (Ammiya). Be concise and friendly."
        )


def get_realtime_agent():
    llm = AgentLLM()  # 🔥 REPLACED

    tts = elevenlabs.TTS(
        api_key=os.getenv("ELEVEN_API_KEY") or os.getenv("ELEVENLABS_API_KEY"),
        model="eleven_flash_v2_5",
        voice_id="9SPZl4Mlgwj7QT4gVprb"
    )

    stt = deepgram.STT(language="ar")

    vad = silero.VAD.load(min_silence_duration=0.3)

    session = AgentSession(
        llm=llm,
        tts=tts,
        stt=stt,
        vad=vad,
    )

    return session, RestaurantAssistant()