from rabbitwebsocketchat.database import get_db
from rabbitwebsocketchat.models import User
from rabbitwebsocketchat.schemas import User_Model


class UserRepository:
    def __init__(self, session: get_db):
        self._session = session

    def create_user(self) -> User:
        new_user = User()
        self._session.add(new_user)
        self._session.commit()
        self._session.refresh(new_user)
        return new_user

    def get_all_users(self) -> list[User]:
        return self._session.query(User)

