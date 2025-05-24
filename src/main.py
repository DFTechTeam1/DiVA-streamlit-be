import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
from src.secret import MIDDLEWARE_SECRET_KEY
from src.routers import health_check, stream, retrieve_image
from services.postgre.models import database_migration
from services.postgre.connection import database_connection
from utils.vector.faiss import FAISS
from utils.json import JSON
from utils.logger import logging
from utils.zero_shot.classifier import VectorDatabase
from utils.error.exception_handler import register_exception_handlers

PROJECT_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = os.path.join(PROJECT_DIR, 'models')
PREVIEW_PATH = os.path.join(PROJECT_DIR, 'json', 'client_preview.json')


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        CLIENT_PREVIEW = JSON.load_json(PREVIEW_PATH)['paths']
        TOTAL_IMAGE = len(CLIENT_PREVIEW)
        index_path, metadata_path = VectorDatabase.load(MODEL_PATH, TOTAL_IMAGE)
        faiss_index = FAISS()
        faiss_index.load(index_path, metadata_path)
        logging.info(f'FAISS loaded with {faiss_index.index.ntotal} entries')
        app.state.faiss_index = faiss_index
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

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

app.add_middleware(SessionMiddleware, secret_key=MIDDLEWARE_SECRET_KEY)
app.include_router(health_check.router)
app.include_router(retrieve_image.router)
app.include_router(stream.router)
