from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.secret import MIDDLEWARE_SECRET_KEY
from src.routers import health_check
from services.postgre.models import database_migration
from services.postgre.connection import database_connection
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
from utils.error.exception_handler import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await database_migration()
        yield
    finally:
        await database_connection().dispose()


app = FastAPI(
    root_path='/api/v1',
    title='DiVA',
    description='Backend service for DFactory Image Retrieval.',
    version='1.0.0',
    lifespan=lifespan,
)

register_exception_handlers(app=app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

app.add_middleware(middleware_class=SessionMiddleware, secret_key=MIDDLEWARE_SECRET_KEY)
app.include_router(health_check.router)
