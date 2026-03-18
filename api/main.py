"""FastAPI application entrypoint.

Sets up routers, middleware, and application state. This module will be the
place to configure channels, CORS, and startup/shutdown events.
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, WebSocket
from channels.web.websocket_handler import voice_websocket


app = FastAPI()


@app.websocket("/ws/voice")
async def websocket_endpoint(websocket: WebSocket):
    await voice_websocket(websocket)


@app.get("/")
def root():
    return {"message": "Multimodal AI Voice Agent API"}
