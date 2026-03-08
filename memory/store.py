"""Conversation memory store interface.

Wraps persistence for chat history and related context. Could be backed by
Redis, database, or other stores.
"""


class MemoryStore:
    def save(self, conversation_id: str, data: dict):
        pass

    def load(self, conversation_id: str):
        pass
