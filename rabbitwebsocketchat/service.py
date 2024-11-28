from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends
from jose.exceptions import JWTError
from jose import jwt
from rabbitwebsocketchat.models import User
from rabbitwebsocketchat.repositories.redis_repository import RedisRepository
from rabbitwebsocketchat.repositories.user_repository import UserRepository
from rabbitwebsocketchat.repositories.auth_repository import AuthRepository
from rabbitwebsocketchat.schemas import Token, TokenData, User_Model, UserInDB
from rabbitwebsocketchat.auth import oauth2_scheme, pwd_context
from rabbitwebsocketchat.config import settings
from rabbitwebsocketchat.exceptions import credentials_exception


class Service():
    def __init__(self, user_rep: UserRepository, auth_rep: AuthRepository, redis_rep: RedisRepository):
        self._user_repository = user_rep
        self._auth_repository = auth_rep
        self._redis_repository = redis_rep

    def create_user(self) -> User:
        return self._user_repository.create_user() #TODO добавить пагинацию

    def get_all_users(self) -> list[User]:
        return self._user_repository.get_all_users() #TODO добавить пагинацию
    
    @staticmethod
    def get_password_hash(password) -> str:
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password, password_hash) -> bool:
        return pwd_context.verify(plain_password, password_hash)

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
        user = self._auth_repository.get_user(token_data.username)
        if user is None:
            raise credentials_exception
        return user

    def authenticate_user(self, username: str, password: str) -> UserInDB | None:
        user = self._auth_repository.get_user(username)
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    def refresh_access_token(self, refresh_token: str) -> Token | None:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload is None:
            raise credentials_exception

        username = payload.get("sub")
        if username is None:
            raise credentials_exception

        access_token_expires = timedelta(
            minutes=settings.EXPIRE_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = self.create_access_token(
            {"sub": username}, expires_delta=access_token_expires
        )

        return Token(
            access_token=access_token, token_type="bearer", refresh_token=refresh_token
        )




    def store_refresh_token_in_redis(
        self, user_id: int | None, token: str, expires_days: timedelta
    ):
        self._redis_repository.store_refresh_token_in_redis(
            user_id, token, expires_days
        )

    def validate_refresh_token_in_redis(
        self, user_id: int | None, token: str
    ) -> bool:
        stored_token = self._redis_repository.validate_refresh_token_in_redis(
            user_id, token
        )
        return stored_token

    def delete_refresh_token_in_redis(self, user_id: int):
        self._redis_repository.delete_refresh_token_in_redis(user_id)