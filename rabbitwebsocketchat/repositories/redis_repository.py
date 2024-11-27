from datetime import timedelta
from rabbitwebsocketchat.config import settings
import redis


class RedisRepository:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)

    def store_refresh_token_in_redis(
        self, user_id: int | None, token: str, expires_days: timedelta
    ):
        expires_seconds = int(expires_days.total_seconds())
        self.redis.setex(f"refresh_token:{user_id}", expires_seconds, token)

    def validate_refresh_token_in_redis(
        self, user_id: int | None, token: str
    ) -> bool:
        stored_token = self.redis.get(f"refresh_token:{user_id}")
        return stored_token == token

    def delete_refresh_token_in_redis(self, user_id: int):
        self.redis.delete(f"refresh_token:{user_id}")