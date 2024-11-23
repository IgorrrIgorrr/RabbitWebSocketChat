from rabbitwebsocketchat.models import User
from rabbitwebsocketchat.repository import UserRepository

class Service():
    def __init__(self, user_rep: UserRepository):
        self._user_repository = user_rep

    def create_user(self) -> dict:
        return self._user_repository.create_user() #TODO добавить пагинацию

    def get_all_users(self) -> list[User]:
        return self._user_repository.get_all_users() #TODO добавить пагинацию
    
    