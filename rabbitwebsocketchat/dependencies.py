from typing import Annotated
from fastapi import Depends, HTTPException
from rabbitwebsocketchat.config import settings
from fastapi.security.api_key import APIKeyHeader
from fastapi import status 
from rabbitwebsocketchat.repositories.redis_repository import RedisRepository
from rabbitwebsocketchat.repositories.user_repository import UserRepository
from rabbitwebsocketchat.repositories.auth_repository import AuthRepository
from rabbitwebsocketchat.database import get_db
from sqlalchemy.orm import Session
from rabbitwebsocketchat.schemas import UserInDB
from rabbitwebsocketchat.service import Service
from rabbitwebsocketchat.auth import oauth2_scheme



def get_user_repository(db: Annotated[Session, Depends(get_db)]) -> UserRepository:
    return UserRepository(db)

def get_auth_repository(db: Annotated[Session, Depends(get_db)]) -> AuthRepository:
    return AuthRepository(db)

def get_redis_repository():
    return RedisRepository()

def get_service(user_rep: Annotated[Service, Depends(get_user_repository)], 
                auth_rep: Annotated[AuthRepository, Depends(get_auth_repository)],
                redis_rep: Annotated[RedisRepository, Depends(get_redis_repository)],
                ) -> Service:  
    return Service(user_rep, auth_rep, redis_rep)


def get_current_user_from_service(
    token: Annotated[str, Depends(oauth2_scheme)],
    service: Annotated[Service, Depends(get_service)],
) -> UserInDB:
    user = service.get_current_user(token)
    return user
