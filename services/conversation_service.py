from openai import OpenAI
from modalities.voice.tts.base_tts import BaseTTS
from observability.logger import log_event
import time

SYSTEM_PROMPT = (
    "You are a professional Egyptian Customer Service assistant. "
    "1. Respond in short, helpful spoken sentences. "
    "2. Use polite Egyptian Arabic (Ammiya) like 'صباح الخير يا فندم', 'تحت أمرك', 'أقدر أساعدك إزاي؟'. "
    "3. Use full diacritics (Tashkeel) on all Arabic text so the voice engine pronounces it naturally. "
    "4. If the user speaks English, respond in English."
)

class ConversationService:
    """
    Handles user messages and generates AI responses using pluggable TTS.
    """

    def __init__(self, tts_engine: BaseTTS):
        self.client = OpenAI()
        # Dependency Injection: We pass the engine in from the outside
        self.tts = tts_engine

    async def handle_message(self, session_id: str, user_message: str):
        start_total = time.time()

        # 1. LLM Generation
        llm_start = time.time()
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        assistant_reply = response.choices[0].message.content
        log_event("llm_latency", {"duration": time.time() - llm_start, "text_length": len(assistant_reply)})


        return assistant_reply