from pydantic import BaseModel

class User_Model(BaseModel):
    user_id:int

class Message(BaseModel):
    room_id: str
    user_id: str
    content: str

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class TokenData(BaseModel):
    username: str


class User(BaseModel):
    id: int | None = None
    username: str


class UserInDB(User):
    password_hash: str
    model_config = {"from_attributes": True}