"""Repository classes encapsulate database access logic.

Example: ConversationRepository, UserRepository.
"""


class BaseRepository:
    def __init__(self, session):
        self.session = session

    def add(self, obj):
        self.session.add(obj)
        self.session.commit()

    def get(self, model, id):
        return self.session.query(model).get(id)
