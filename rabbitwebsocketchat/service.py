from typing import Annotated

from fastapi import Depends
from jose.exceptions import JWTError
from jose import jwt
from rabbitwebsocketchat.models import User
from rabbitwebsocketchat.repositories.repository import UserRepository
from rabbitwebsocketchat.repositories.auth_repository import AuthRepository
from rabbitwebsocketchat.schemas import User_Model
from rabbitwebsocketchat.auth import oauth2_scheme, pwd_context
from rabbitwebsocketchat.config import settings


class Service():
    def __init__(self, user_rep: UserRepository, auth_rep: AuthRepository):
        self._user_repository = user_rep
        self._auth_repository = auth_rep

    def create_user(self) -> User:
        return self._user_repository.create_user() #TODO добавить пагинацию

    def get_all_users(self) -> list[User]:
        return self._user_repository.get_all_users() #TODO добавить пагинацию
    
    @staticmethod
    def get_password_hash(password) -> str:
        return pwd_context.hash(password)
    
    def get_current_user(
        self, token: Annotated[str, Depends(oauth2_scheme)]
    ) -> User_Model:
        try: 
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError as e:
            raise credentials_exception from e
        user = await self._auth_repository.get_user(token_data.username)
        if user is None:
            raise credentials_exception
        return user