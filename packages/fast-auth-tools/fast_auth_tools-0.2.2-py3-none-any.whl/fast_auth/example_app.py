"""
from fastapi import FastAPI, Depends

from fast_auth import (
    add_auth_routes,
    get_current_user,
    User,
    set_cors_origins,
)

app = FastAPI()
add_auth_routes(app)
set_cors_origins(app)


@app.get("/", dependencies=[Depends(get_current_user)])
async def root():
    return {"message": "Hello World"}


@app.get("/hello/")
async def say_hello(user: User = Depends(get_current_user)):
    return {"message": f"Hello {user.username}"}
"""
