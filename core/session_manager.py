from core.agent_session import AgentSession
import uuid


class SessionManager:

    def __init__(self):
        self.sessions = {}

    def create(self):
        session_id = str(uuid.uuid4())
        session = AgentSession(session_id)
        self.sessions[session_id] = session
        return session

    def get(self, session_id):
        return self.sessions.get(session_id)

    def remove(self, session_id):
        self.sessions.pop(session_id, None)


session_manager = SessionManager()