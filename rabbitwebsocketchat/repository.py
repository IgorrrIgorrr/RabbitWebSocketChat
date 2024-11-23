from rabbitwebsocketchat.database import get_db
from rabbitwebsocketchat.models import User
from rabbitwebsocketchat.schemas import User_Model


class UserRepository:
    def __init__(self, session: get_db):
        self._session = session

    def create_user(self) -> dict:
        new_user = User()
        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)
        return {"success":"User added with id {new_user.id}"}

    def get_all_users(self) -> list[User]:
        return self._session.query(User)

