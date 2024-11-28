from datetime import timedelta
from typing import Annotated
from fastapi import Depends, FastAPI, Form, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from rabbitwebsocketchat.router import router
from rabbitwebsocketchat.models import Base, User
from rabbitwebsocketchat.database import engine
from rabbitwebsocketchat.dependencies import get_current_user_from_service, get_service
from rabbitwebsocketchat.service import Service
from rabbitwebsocketchat.schemas import Token, User_Model, UserInDB
from rabbitwebsocketchat.exceptions import credentials_exception
from rabbitwebsocketchat.config import settings

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/auth/register")
def registration(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    service: Annotated[Service, Depends(get_service)], 
):
    user = service._auth_repository.get_user(username) 
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    password_hash = service.get_password_hash(password)
    user = service._auth_repository.create_user(username, password_hash)
    return user


@app.post("/auth/login")
def login_for_tokens(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: Annotated[Service, Depends(get_service)],
) -> Token:
    user = service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise credentials_exception
    access_token_expires = timedelta(
        minutes=settings.EXPIRE_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = service.create_access_token(
        {"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(days=settings.EXPIRE_REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = service.create_refresh_token(
        {"sub": user.username}, expires_delta=refresh_token_expires
    )
    service.store_refresh_token_in_redis(
        user.id, refresh_token, refresh_token_expires
    )
    return Token(
        access_token=access_token, token_type="bearer", refresh_token=refresh_token
    )





@app.post("/auth/refresh")
def refresh_access_token(
    service: Annotated[Service, Depends(get_service)],
    user: Annotated[UserInDB, Depends(get_current_user_from_service)],
    refresh_token: str = Form(...),
) -> Token:
    is_valid = service.validate_refresh_token_in_redis(user.id, refresh_token)
    if not is_valid:
        raise credentials_exception
    new_token = service.refresh_access_token(refresh_token)
    if not new_token:
        raise credentials_exception
    return new_token


@app.get("/users", response_model=list[UserInDB])
def get_all_users_eeeee(service: Annotated[Service, Depends(get_service)],
                        user: Annotated[UserInDB, Depends(get_current_user_from_service)],
                        )-> list[User]:
    return service.get_all_users()
