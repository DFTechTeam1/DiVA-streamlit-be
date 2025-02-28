from fastapi import FastAPI
from src.secret import Config
from src.routers import health_check, stream_image
from src.routers.query import search_by_image
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from services.postgres.models import database_migration
from services.postgres.connection import database_connection
from starlette.middleware.sessions import SessionMiddleware
from utils.error.exception_handler import register_exception_handlers


config = Config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await database_migration()
        yield
    finally:
        await database_connection().dispose()


app = FastAPI(
    root_path="/api/v1",
    title="DiVA",
    description="Backend service for DFactory Image Retrieval.",
    version="1.0.0",
    lifespan=lifespan,
)

register_exception_handlers(app=app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    middleware_class=SessionMiddleware, secret_key=config.MIDDLEWARE_SECRET_KEY
)

app.include_router(health_check.router)
app.include_router(stream_image.router)
app.include_router(search_by_image.router)
