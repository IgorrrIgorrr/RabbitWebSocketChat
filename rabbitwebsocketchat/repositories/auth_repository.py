from rabbitwebsocketchat.database import get_db
from rabbitwebsocketchat.schemas import UserInDB
from rabbitwebsocketchat.models import User


class AuthRepository:
    def __init__(self, session: get_db):
        self._session = session

    def get_user(self, username: str) -> UserInDB | None:
        user = self._session.query(User).filter(User.username == username).first()
        if user:
            return UserInDB.model_validate(user)
        return None

    def create_user(self, username: str, password_hash: str) -> UserInDB | None:
        user = User(username=username, password_hash=password_hash)
        self._session.add(user)
        self._session.commit()
        self._session.refresh(user)
        return UserInDB.model_validate(user)    
