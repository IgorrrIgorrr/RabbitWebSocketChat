from pydantic import BaseModel

class User_Model(BaseModel):
    user_id:str

class Message(BaseModel):
    room_id: str
    user_id: str
    content: str