from datetime import timedelta
from typing import Annotated
from fastapi import Depends, FastAPI, Form, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from rabbitwebsocketchat.models import Base, User
from rabbitwebsocketchat.database import engine
from rabbitwebsocketchat.dependencies import get_service, get_api_key
from rabbitwebsocketchat.service import Service
from rabbitwebsocketchat.schemas import User_Model
from rabbitwebsocketchat.exceptions import credentials_exception
from rabbitwebsocketchat.config import settings

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
async def login_for_tokens(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: Annotated[Service, Depends(get_service)],
) -> Token:
    user = await service.authenticate_user(form_data.username, form_data.password)
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
    await service.store_refresh_token_in_redis(
        user.id, refresh_token, refresh_token_expires
    )
    return Token(
        access_token=access_token, token_type="bearer", refresh_token=refresh_token
    )





@app.post("/auth/refresh")
async def refresh_access_token(
    service: Annotated[Service, Depends(get_service)],
    user: Annotated[UserInDB, Depends(get_current_user_from_service)],
    refresh_token: str = Form(...),
) -> Token:
    is_valid = await service.validate_refresh_token_in_redis(user.id, refresh_token)
    if not is_valid:
        raise credentials_exception
    new_token = await service.refresh_access_token(refresh_token)
    if not new_token:
        raise credentials_exception
    return new_token








@app.post("/users", response_model=User_Model)
def create_user(service: Annotated[Service, Depends(get_service)]) -> dict:
    return service.create_user()

@app.get("/users", response_model=list[User_Model])
def get_all_users(service: Annotated[Service, Depends(get_service)])-> list[User]:
    return service.get_all_users()
