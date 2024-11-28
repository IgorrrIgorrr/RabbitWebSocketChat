import json
from faststream.rabbit.fastapi import RabbitRouter
from fastapi import WebSocket, Depends, HTTPException
from rabbitwebsocketchat.schemas import User_Model, Message, UserInDB
from typing import Annotated
from rabbitwebsocketchat.dependencies import get_current_user_from_service
from rabbitwebsocketchat.repositories.redis_repository import redis

router = RabbitRouter("amqp://guest:guest@localhost:5672/")

MAX_USERS_PER_ROOM = 2

@router.post("/message")
def send_message_to_rabbit(message: Message, 
                           user: Annotated[UserInDB, Depends(get_current_user_from_service)]):
    room_key = f"room:{message.room_id}"
    users_in_room = redis.smembers(room_key)
    if len(users_in_room)>= MAX_USERS_PER_ROOM:
        raise HTTPException(detail="room is fool")
    if user.username not in users_in_room:
        redis.sadd(room_key, user.username)
    try:
        router.publish(message.model_dump(), queue = message.room_id)
        return {"status":"message sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=" Error while sending message: {e}")
    

@router.websocket("/updates/{room_id}")
def get_updates_from_rabbit(websocket: WebSocket, 
                                  room_id: str, 
                                  user: Annotated[UserInDB, Depends(get_current_user_from_service)]):
    room_key = f"room:{room_id}"
    is_member = redis.sismember(room_key, user.username)
    if not is_member:
        websocket.close(code=1000)
    try:
        while True:
            message = router.subscribe("room_updates")
            message_data = json.loads(message)
            if message_data["room_id"] == room_id:
                websocket.send_text(f"{message_data['user']}: {message_data['content']}")
    except Exception as e:
        redis.srem(room_key, user.username)  
        raise e

