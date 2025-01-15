from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .routes import router
from .settings import settings


def set_cors_origins(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def add_auth_routes(app: FastAPI):
    app.include_router(router)


def fast_auth(app: FastAPI):
    add_auth_routes(app)
    set_cors_origins(app)
