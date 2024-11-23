from typing import Annotated
from fastapi import Depends, FastAPI
from rabbitwebsocketchat.models import Base, User
from rabbitwebsocketchat.database import engine
from rabbitwebsocketchat.dependencies import get_service, get_api_key
from rabbitwebsocketchat.service import Service

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/users", response_model=User)
def create_user(service: Annotated[Service, Depends(get_service)],
             api_key: Annotated[str, Depends(get_api_key)]) -> dict:
    return service.create_user()

@app.get("/users", response_model=list[User])
def get_all_users(service: Annotated[Service, Depends(get_service)],
                  api_key: Annotated[str, Depends(get_api_key)])-> list[User]:
    return service.get_all_users()
