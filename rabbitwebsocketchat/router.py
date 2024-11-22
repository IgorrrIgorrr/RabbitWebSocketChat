from faststream.rabbit.fastapi import RabbitRouter
from fastapi import WebSocket, Depends, HTTPException
from schemas import User_Model, Message
from typing import Annotated
from rabbitwebsocketchat.dependencies import get_user


router = RabbitRouter("amqp://guest:guest@localhost:5672/")

@router.post("/message")
async def send_message(message: Message):
    try:
        await router.publish(message.model_dump(), queue = message.room_id)
        return {"status":"message sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=" Error while sending message: {e}")
    

@router.websocket("/updates/{room_id}")
async def get_updates(websoket: WebSocket, room_id: str, user: Annotated[User_Model, Depends(get_user)]):
