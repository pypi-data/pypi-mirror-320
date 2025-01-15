# Fast Auth Tools (for FastAPI)

> Adds oauth2 authentication to a FastApi app with a single function

### Install
```shell
pip install fast-auth-tools
```

### Create User DB

```shell
python -m fast_auth.create_sqlite_db ./my_user_db.sqlite3
```
_db path argument is optional and will default to .../site_packages/fast_auth/users.sqlite3_

### Example

```python
import os

from fastapi import FastAPI, Depends

from fast_auth import fast_auth, logged_in_user, User
from fast_auth import settings as auth_settings

auth_settings.user_db_path = "./my_user_db.sqlite3" # if the path was changed
auth_settings.secret_key = os.getenv("FAST_AUTH_SECRET_KEY")
auth_settings.cors_origins = ["myapp.com", "my-test-server.com"]

app = FastAPI()
fast_auth(app)


# Example authenticated routes:
@app.get("/secure/get/", dependencies=[Depends(logged_in_user)])
async def must_be_logged_in():
    return {}

@app.post("/secure/post/")
async def get_user_object(user: User = Depends(logged_in_user)):
    print(f"password hash: {user.password}")
    return {
        "data": f"{user.username} is already logged in"
    }
```

### Settings

| name                     | default                                     | description                                                                           |
|--------------------------|---------------------------------------------|---------------------------------------------------------------------------------------|
| cors_origins             | \["*"]                                      | allowed CORS origins                                                                  |
| secret_key               | "SoMeThInG_-sUp3Rs3kREt!!"                  | the key used to encrypt JWT                                                           |
| algorithm                | "HS256"                                     | the alogrithm used to encrypt JWT                                                     |
| access_token_expire_days | 5                                           | the maximum number of days JWT will be valid                                          |
| user_db_path             | ".../site_packages/fast_auth/users.sqlite3" | the path to the sqlite database that holds username/encrypted password information    |
| login_url                | "login"                                     | path to POST endpoint accepting username/password form data                           |
| token_refresh_url        | "refresh_token"                              | path to GET endpoint that takes a valid JWT and returns a new JWT with maximum expiry |
