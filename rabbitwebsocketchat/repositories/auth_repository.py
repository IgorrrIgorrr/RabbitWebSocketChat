from rabbitwebsocketchat.database import get_db
from rabbitwebsocketchat.schemas import UserInDB
from rabbitwebsocketchat.models import User

class AuthRepository:
    def __init__(self, session: get_db):
        self._session = session

    def get_user(self, username: str) -> UserInDB | None:
        user = self._session.query(User).filter(User.name == username).scalar_one_or_none()
        if user:
            user_dict = dict(user)
            return UserInDB(**user_dict)
        return None

    async def create_user(self, username: str, password_hash: str) -> UserInDB | None:
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                    INSERT INTO users(username, password_hash)
                    VALUES($1, $2)
                    RETURNING id, username, password_hash
                    """,
                username,
                password_hash,
            )
            if row:
                user_dict = dict(row)
                return UserInDB(**user_dict)
            return None