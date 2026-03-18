import json
import base64
import asyncio
from fastapi import WebSocket, WebSocketDisconnect

# Import your scripts
from core.session_manager import session_manager
from services.conversation_service import ConversationService
from modalities.voice.tts.piper_tts import PiperTTS
from modalities.voice.stt.whisper_stt import WhisperSTT 
from modalities.voice.streaming.audio_stream_manager import AudioStreamManager

# 1. Initialize Engines
# Start with English, but PiperTTS.set_language() will swap this dynamically
tts_engine = PiperTTS("modalities/voice/tts/en_US-lessac-medium.onnx")
stt_engine = WhisperSTT()
conversation_service = ConversationService(tts_engine=tts_engine)

def contains_arabic(text: str) -> bool:
    """Detects if the text contains Arabic script."""
    return any('\u0600' <= char <= '\u06FF' for char in text)

async def voice_websocket(websocket: WebSocket):
    await websocket.accept()
    
    session = session_manager.create()
    stream_manager = AudioStreamManager() 
    
    print(f"🚀 New session started: {session.session_id}")

    try:
        while True:
            message = await websocket.receive()
            
            if message["type"] == "websocket.disconnect":
                break

            if "bytes" in message:
                audio_chunk = message["bytes"]
                segment = await stream_manager.add_chunk(audio_chunk)

                if segment:
                    print("🎤 Silence detected, transcribing...")
                    
                    # 💡 FIX 1: Pass a language hint to Whisper in the executor if needed
                    # Or update your WhisperSTT.transcribe() to default to language="ar"
                    loop = asyncio.get_event_loop()
                    user_text = await loop.run_in_executor(None, stt_engine.transcribe, segment)

                    if user_text and len(user_text.strip()) > 1:
                        print(f"📝 You: {user_text}")
                        await websocket.send_json({"type": "transcript", "text": user_text})

                        # --- STEP A: Get Text from LLM ---
                        # Ensure your ConversationService.handle_message ONLY returns text now
                        session.is_agent_speaking = True
                        assistant_text = await conversation_service.handle_message(
                            session.session_id, user_text
                        )

                        # --- STEP B: Dynamic Voice Switch ---
                        # We check the LLM's response. If it's Arabic, we swap models BEFORE synthesis.
                        if contains_arabic(assistant_text):
                            print("🌐 Switching to Arabic (Kareem) model...")
                            tts_engine.set_language("ar")
                        else:
                            print("🌐 Switching to English (Lessac) model...")
                            tts_engine.set_language("en")

                        # --- STEP C: Synthesis with the CORRECT model ---
                        audio_bytes = await tts_engine.synthesize(assistant_text)

                        # --- STEP D: Send to Frontend ---
                        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
                        await websocket.send_json({
                            "type": "assistant_audio",
                            "text": assistant_text,
                            "audio": audio_b64
                        })
                        session.is_agent_speaking = False

    except WebSocketDisconnect:
        print(f"🔌 Session {session.session_id} disconnected.")
        session_manager.remove(session.session_id)
    except Exception as e:
        import traceback
        print(f"❌ Error in websocket: {e}")
        traceback.print_exc()
        session_manager.remove(session.session_id)