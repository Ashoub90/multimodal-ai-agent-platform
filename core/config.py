"""Configuration management for the application.

Loads settings from environment variables, configuration files, or a
centralized config service. Uses pydantic or similar for structured settings.
"""

from pydantic import BaseSettings


class Settings(BaseSettings):
    # database
    DATABASE_URL: str
    # redis
    REDIS_URL: str
    # openai/whisper
    OPENAI_API_KEY: str
    # elevenlabs
    ELEVENLABS_API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
