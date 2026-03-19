import time
from openai import OpenAI

PROMPTS = {
    "ar": (
        "You are a sophisticated Egyptian Customer Service Lead. "
        "Use White-Collar Egyptian Ammiya. Be polite and concise (max 15 words). "
        "Use 'تمام يا فندم', 'من عينيا'."
    ),
    "en": (
        "You are a professional Customer Service Lead. Use a helpful, elegant tone. "
        "Keep responses under 15 words."
    )
}

class ConversationService:
    def __init__(self):
        self.client = OpenAI()
        self.history = {}
        self.language = {} # session_id -> 'ar' or 'en'

    async def handle_message_stream(self, session_id: str, user_message: str):
        # Default to English if not set
        lang = self.language.get(session_id, "en")
        
        if session_id not in self.history:
            self.history[session_id] = [{"role": "system", "content": PROMPTS[lang]}]
        
        self.history[session_id].append({"role": "user", "content": user_message})

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.history[session_id][-6:],
            stream=True 
        )

        full_content = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_content += content
                yield content 

        self.history[session_id].append({"role": "assistant", "content": full_content})