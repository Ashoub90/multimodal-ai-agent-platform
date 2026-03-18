import base64
from fastapi import WebSocket, WebSocketDisconnect
from modalities.voice.streaming.audio_stream_manager import AudioStreamManager
from modalities.voice.stt.whisper_stt import WhisperSTT
import asyncio
from services.conversation_service import ConversationService

conversation_service = ConversationService()


async def run_stt(segment, stt, websocket):

    loop = asyncio.get_running_loop()
    text = await loop.run_in_executor(None, stt.transcribe, segment)

    if not text:
        return

    # send transcript
    await websocket.send_json({
        "type": "transcript",
        "text": text
    })

    # call LLM + TTS
    response_text, audio_bytes = await conversation_service.handle_message(
        session_id="voice_session",
        user_message=text
    )

    # send text
    await websocket.send_json({
        "type": "assistant",
        "text": response_text
    })

    # send audio
    await websocket.send_json({
        "type": "assistant_audio",
        "audio": base64.b64encode(audio_bytes).decode()
    })


async def voice_websocket(websocket: WebSocket):

    await websocket.accept()

    manager = AudioStreamManager()
    stt = WhisperSTT()

    while True:
        try:
            data = await websocket.receive()

            if "bytes" in data and data["bytes"] is not None:

                audio_chunk = data["bytes"]

                segment = await manager.add_chunk(audio_chunk)

                if segment:

                    print("Transcribing audio...")

                    asyncio.create_task(run_stt(segment, stt, websocket))

        except WebSocketDisconnect:
            print("Voice websocket disconnected")
            break
        except RuntimeError:
            break