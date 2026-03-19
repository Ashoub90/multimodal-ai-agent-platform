import json
import base64
import asyncio
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect

from core.session_manager import session_manager
from services.conversation_service import ConversationService, PROMPTS
from modalities.voice.tts.elevenlabs_tts import ElevenLabsTTS 
from modalities.voice.tts.openai_tts import OpenAITTS 
from modalities.voice.stt.whisper_stt import WhisperSTT 
from modalities.voice.streaming.audio_stream_manager import AudioStreamManager

# Global Engines
arabic_tts = ElevenLabsTTS()
english_tts = OpenAITTS()
stt_engine = WhisperSTT()
conversation_service = ConversationService()

def log_diagnostic(session_id, category, message):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"DEBUG [{timestamp}] [{session_id}] [{category}] >> {message}")

async def voice_websocket(websocket: WebSocket):
    await websocket.accept()
    session = session_manager.create()
    stream_manager = AudioStreamManager()
    
    current_tts = english_tts 
    current_lang = "en" # Default

    log_diagnostic(session.session_id, "SESSION", "Connection established.")

    try:
        while True:
            # Receive message and check type immediately
            message = await websocket.receive()
            
            if message.get("type") == "websocket.disconnect":
                break

            # 1. Handle Language Selection (JSON)
            if "text" in message:
                try:
                    data = json.loads(message["text"])
                    if data.get("type") == "set_language":
                        current_lang = data.get("value")
                        
                        conversation_service.language[session.session_id] = current_lang
                        conversation_service.history[session.session_id] = [
                            {"role": "system", "content": PROMPTS[current_lang]}
                        ]
                        
                        current_tts = arabic_tts if current_lang == "ar" else english_tts
                        log_diagnostic(session.session_id, "CONFIG", f"Language locked to: {current_lang.upper()}")
                        continue
                except json.JSONDecodeError:
                    log_diagnostic(session.session_id, "ERROR", "Malformed JSON from frontend.")

            # 2. Handle Audio Processing
            if "bytes" in message:
                audio_chunk = message["bytes"]
                segment = await stream_manager.add_chunk(audio_chunk)

                if segment:
                    # FIX: Pass the current_lang to Whisper to prevent prompt hallucinations
                    user_text = await asyncio.to_thread(
                        stt_engine.transcribe, segment, language=current_lang
                    )
                    
                    if user_text and len(user_text.strip()) > 0:
                        log_diagnostic(session.session_id, "STT_OUT", f"User said: '{user_text}'")
                        await websocket.send_json({"type": "transcript", "text": user_text})

                        session.is_agent_speaking = True
                        sentence_buffer = ""
                        chunk_index = 0
                        
                        async for text_chunk in conversation_service.handle_message_stream(
                            session.session_id, user_text
                        ):
                            sentence_buffer += text_chunk

                            if any(p in sentence_buffer for p in [".", "!", "?", "،", "\n"]) or len(sentence_buffer) > 50:
                                current_task_text = sentence_buffer.strip()
                                sentence_buffer = ""
                                
                                if current_task_text:
                                    asyncio.create_task(
                                        process_and_send_audio(websocket, current_task_text, current_tts, chunk_index)
                                    )
                                    chunk_index += 1

                        if sentence_buffer.strip():
                            asyncio.create_task(
                                process_and_send_audio(websocket, sentence_buffer.strip(), current_tts, chunk_index)
                            )
                        
                        session.is_agent_speaking = False

    except WebSocketDisconnect:
        log_diagnostic(session.session_id, "SESSION", "WebSocket Disconnected.")
    except Exception as e:
        log_diagnostic(session.session_id, "CRITICAL", f"Error: {e}")
    finally:
        session_manager.remove(session.session_id)
        log_diagnostic(session.session_id, "SESSION", "Cleanup complete.")

async def process_and_send_audio(websocket, text, tts_engine, index):
    try:
        audio_bytes = await tts_engine.synthesize(text)
        if audio_bytes:
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
            # Check if websocket is still open before sending
            await websocket.send_json({
                "type": "assistant_audio_chunk",
                "text": text,
                "audio": audio_b64,
                "index": index 
            })
    except Exception as e:
        print(f"❌ TTS task error: {e}")