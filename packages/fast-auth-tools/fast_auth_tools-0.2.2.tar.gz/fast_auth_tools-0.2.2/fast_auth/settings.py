import os
from dataclasses import dataclass

DEFAULTS = {
    "cors_origins": ["*"],
    "secret_key": "SoMeThInG_-sUp3Rs3kREt!!",
    "algorithm": "HS256",
    "access_token_expire_days": 5,
    "user_db_path": f"{os.path.dirname(__file__)}/users.sqlite3",
    "login_url": "login",
    "token_refresh_url": "refresh_token",
}


@dataclass
class Settings:
    cors_origins: list[str]
    secret_key: str
    algorithm: str
    access_token_expire_days: int
    user_db_path: str
    login_url: str
    token_refresh_url: str


settings = Settings(**DEFAULTS)
