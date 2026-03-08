"""Pydantic schemas for conversation-related data structures."""

from pydantic import BaseModel


class Message(BaseModel):
    sender: str
    text: str


class Conversation(BaseModel):
    id: str
    messages: list[Message]
