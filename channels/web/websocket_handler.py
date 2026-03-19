import json
import base64
import asyncio
import time  # Added for duration tracking
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

def log_duration(session_id, category, message, start_time):
    """Logs the duration of an event in seconds."""
    duration = time.time() - start_time
    print(f"⏱️  [{session_id}] [{category}] >> {message} (Took: {duration:.2f}s)")

async def voice_websocket(websocket: WebSocket):
    await websocket.accept()
    session = session_manager.create()
    stream_manager = AudioStreamManager()
    
    current_tts = english_tts 
    current_lang = "en"

    print(f"DEBUG [{session.session_id}] [SESSION] >> Connection established.")

    try:
        while True:
            message = await websocket.receive()
            
            if message.get("type") == "websocket.disconnect":
                break

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
                        continue
                except json.JSONDecodeError:
                    pass

            if "bytes" in message:
                audio_chunk = message["bytes"]
                segment = await stream_manager.add_chunk(audio_chunk)

                if segment:
                    # --- STT TIMING ---
                    stt_start = time.time()
                    user_text = await asyncio.to_thread(
                        stt_engine.transcribe, segment, language=current_lang
                    )
                    log_duration(session.session_id, "STT", f"Transcribed: '{user_text}'", stt_start)
                    
                    if user_text and user_text.strip():
                        await websocket.send_json({"type": "transcript", "text": user_text})

                        session.is_agent_speaking = True
                        sentence_buffer = ""
                        tts_tasks = [] 
                        
                        # --- LLM TIMING ---
                        llm_start = time.time()
                        first_sentence_found = False
                        
                        async for text_chunk in conversation_service.handle_message_stream(
                            session.session_id, user_text
                        ):
                            sentence_buffer += text_chunk

                            if any(p in sentence_buffer for p in [".", "!", "?", "،", "\n"]) or len(sentence_buffer) > 60:
                                if not first_sentence_found:
                                    log_duration(session.session_id, "LLM_FIRST_SENTENCE", "First sentence ready", llm_start)
                                    first_sentence_found = True

                                current_task_text = conversation_service.clean_text(sentence_buffer)
                                sentence_buffer = ""
                                
                                if current_task_text:
                                    # We wrap the synthesize call in a helper to track its individual timing
                                    task = asyncio.create_task(
                                        tracked_synthesis(current_tts, current_task_text, len(tts_tasks), session.session_id)
                                    )
                                    tts_tasks.append((task, current_task_text))

                        # Handle remaining buffer
                        final_text = conversation_service.clean_text(sentence_buffer)
                        if final_text:
                            task = asyncio.create_task(
                                tracked_synthesis(current_tts, final_text, len(tts_tasks), session.session_id)
                            )
                            tts_tasks.append((task, final_text))

                        # --- DELIVERY TIMING ---
                        delivery_start = time.time()
                        for index, (task, text) in enumerate(tts_tasks):
                            try:
                                audio_bytes = await task 
                                if audio_bytes:
                                    audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
                                    await websocket.send_json({
                                        "type": "assistant_audio_chunk",
                                        "text": text,
                                        "audio": audio_b64,
                                        "index": index 
                                    })
                            except Exception as e:
                                print(f"❌ Delivery error: {e}")
                        
                        log_duration(session.session_id, "TOTAL_RESPONSE", "All audio sent", llm_start)
                        session.is_agent_speaking = False

    except WebSocketDisconnect:
        print(f"DEBUG [{session.session_id}] [SESSION] >> Disconnected.")
    except Exception as e:
        print(f"❌ CRITICAL: {e}")
    finally:
        session_manager.remove(session.session_id)

async def tracked_synthesis(tts_engine, text, index, session_id):
    """Wrapper to time how long each specific TTS chunk takes."""
    start = time.time()
    audio = await tts_engine.synthesize(text)
    log_duration(session_id, f"TTS_CHUNK_{index}", f"Synthesized chunk {index}", start)
    return audio