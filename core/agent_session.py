class AgentSession:
    def __init__(self, session_id: str):
        self.session_id = session_id

        self.is_agent_speaking = False
        self.interrupt_flag = False

        self.messages = []