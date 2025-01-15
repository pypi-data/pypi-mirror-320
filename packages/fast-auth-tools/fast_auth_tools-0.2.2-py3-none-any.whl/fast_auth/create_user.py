from getpass import getpass

from .user import User
from .funcs import run


async def create_user(username, password):
    await User.create(username=username, password=password)


def run_create_user_with_event_loop():
    run(create_user(input("username: "), getpass("password: ")))


if __name__ == "__main__":
    run_create_user_with_event_loop()
