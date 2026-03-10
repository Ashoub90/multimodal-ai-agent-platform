"""Web channel adapter using WebSockets.

Handles incoming websocket connections from the browser and translates
events into the internal message format used by the agent.
"""


from fastapi import WebSocket, WebSocketDisconnect
from modalities.voice.streaming.audio_stream_manager import AudioStreamManager
from modalities.voice.stt.whisper_stt import WhisperSTT
import asyncio


async def run_stt(segment, stt, websocket):
    loop = asyncio.get_running_loop()
    text = await loop.run_in_executor(None, stt.transcribe, segment)

    if text:
        print("Transcript:", repr(text))
        await websocket.send_text(text)



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
