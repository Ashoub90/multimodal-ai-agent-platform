from openai import OpenAI
from modalities.voice.tts.piper_tts import PiperTTS


class ConversationService:
    """
    Handles user messages and generates AI responses.
    """

    def __init__(self):
        self.client = OpenAI()
        self.tts = PiperTTS("modalities/voice/tts/en_US-lessac-medium.onnx")

    async def handle_message(self, session_id: str, user_message: str):

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant. Respond in short spoken sentences."},
                {"role": "user", "content": user_message},
            ],
        )

        assistant_reply = response.choices[0].message.content

        # generate speech
        audio_bytes = await self.tts.synthesize(assistant_reply)

        return assistant_reply, audio_bytes