from rabbitwebsocketchat.database import get_db
from rabbitwebsocketchat.models import User
from rabbitwebsocketchat.schemas import User_Model


class UserRepository:
    def __init__(self, session: get_db):
        self.session = session

    def add user(self)

