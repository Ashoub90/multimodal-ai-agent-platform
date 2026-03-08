"""FastAPI application entrypoint.

Sets up routers, middleware, and application state. This module will be the
place to configure channels, CORS, and startup/shutdown events.
"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Multimodal AI Voice Agent API"}
