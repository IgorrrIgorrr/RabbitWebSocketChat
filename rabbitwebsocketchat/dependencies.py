from typing import Annotated
from fastapi import Depends, HTTPException
from rabbitwebsocketchat.config import settings
from fastapi.security.api_key import APIKeyHeader
from fastapi import status 
from rabbitwebsocketchat.repositories.repository import UserRepository
from rabbitwebsocketchat.repositories.auth_repository import AuthRepository
from rabbitwebsocketchat.database import get_db
from sqlalchemy.orm import Session
from rabbitwebsocketchat.service import Service

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

API_KEY = settings.API_KEY


async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate API key",
        )

def get_user_repository(db: Annotated[Session, Depends(get_db)]) -> Session:
    return UserRepository(db)

def get_auth_repository():
    return AuthRepository()

def get_service(user_rep: Annotated[Service, Depends(get_user_repository)], 
                auth_rep: Annotated[AuthRepository, Depends(get_auth_repository)]) -> Service:  
    return Service(user_rep, auth_rep)


def get_user():
    pass
