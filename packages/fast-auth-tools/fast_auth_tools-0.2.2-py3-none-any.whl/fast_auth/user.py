from typing import Optional

import aiosqlite
from fastapi import Depends
from pydantic import BaseModel, constr, ValidationError

from .constants import oauth2_scheme
from .exceptions import credentials_exception
from .funcs import replace, get_data_from_token, insert
from .funcs import get_password_hash as _hash
from .funcs import verify_password as _verify
from .settings import settings


class User(BaseModel):
    __table__ = "users"
    username: str
    password: str

    def check_password(self, password):
        return _verify(password, self.password)

    @staticmethod
    def hash_password(password):
        return _hash(password)

    @classmethod
    async def get(cls, username):
        username = username.split(" ")[0]
        async with aiosqlite.connect(settings.user_db_path) as db:
            async with db.execute(
                f"SELECT * FROM users WHERE username = '{username}'"
            ) as cursor:
                from_db = await cursor.fetchone()
                if from_db is None:
                    return None
                return cls(username=from_db[0], password=from_db[1])

    async def save(self):
        if len(self.password) != 60:
            self.password = self.hash_password(self.password)
        await replace(
            self.__table__, {"username": self.username, "password": self.password}
        )

    @classmethod
    async def create(cls, username: str, password: constr(max_length=59)):
        password = cls.hash_password(password)
        await insert(cls.__table__, {"username": username, "password": password})
        return cls(username=username, password=password)

    async def update_password(self, old_password, password: constr(max_length=59)):
        if not self.check_password(old_password):
            raise ValidationError("Incorrect password")
        self.password = self.hash_password(password)
        await self.save()

    @classmethod
    async def authenticate_user(cls, username: str, password: str) -> Optional["User"]:
        user = await cls.get(username=username)
        try:
            if not _verify(password, user.password):
                raise credentials_exception
            return user
        except Exception:
            raise credentials_exception


async def logged_in_user(token: str = Depends(oauth2_scheme)):
    data = await get_data_from_token(token)
    user = await User.get(username=data.username)
    if user is None:
        raise credentials_exception
    return user
