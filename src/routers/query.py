import base64
import math
from PIL import Image
from typing import Optional
from pathlib import Path
from fastapi import APIRouter, status, Depends
from services.postgre.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.secret import APPLICATION_PORT, IP_HOST
from src.schema.response import ResponseDefault, ResponsePage
from src.schema.request_format import QueryPayload
from services.custom_model.siglip import cls_model
from services.postgre.connection import get_db
from services.postgre.models import ClientPreview
from utils.logger import logging
from utils.query import QueryDatabase
from utils.helper import extract_path, format_clip_pred
from utils.processor import ImageProcessor
from utils.clip import query_model

router = APIRouter(tags=['Query'], prefix='/query')

async def query(schema: QueryPayload, db: AsyncSession = Depends(get_db)) -> ResponseDefault:
    logging.info('Endpoint query.')

    # API response
    response = ResponseDefault()
    page = ResponsePage()

    # DB session
    session = QueryDatabase(session=db)

    # Image processor
    processor = ImageProcessor()

    # Path management
    BASE_DIR = Path(__file__).resolve().parents[2]
    MODEL_PATH = BASE_DIR / 'models' / 'SIGLIP_custom_model.pth'
    TRAINED_LABEL = BASE_DIR / 'json' / 'trained_label.json'
    BASE_URL = f'http://{IP_HOST}:{APPLICATION_PORT}/api/v1/query/stream?image_path='
    
    # DB query utils
    IMAGE_PER_PAGE = 50
    QUERY_PER_PAGE = 100

    current_image = None

    if schema.filename:
        logging.info("Fetching existing client preview.")
        current_image = await session.find(table=ClientPreview, filename=schema.filename)

    if schema.page == 1:
        # Image processing
        decoded = processor.decode(schema.encoded_image)
        resized = processor.resize(decoded)

        # Predict uploaded image
        predictions = cls_model.predict(images=resized, threshold=schema.threshold, batch_size=10)

        # Format prediction label
        formatted_result = cls_model.to_dict(predictions[0])

        # Query db
        filtered_image = await session.find(table=ClientPreview, fetch="all", filter='or', **formatted_result)
        
        if current_image:
            filtered_image.insert(0, current_image)
    
        if not filtered_image:
            response.success = False
            response.message = "No similar entries on database."
            return response
        
        extracted_filepath = extract_path(filtered_image)

        # Process filtered image
        converted_image = processor.resize(extracted_filepath[:QUERY_PER_PAGE])

        # CLIP encoding
        query_image = query_model.encode(resized, batch_size=4)
        encoded_image = query_model.encode(converted_image, batch_size=4)

        # Query similar images
        rangked_image = query_model.query(query_image, encoded_image, IMAGE_PER_PAGE)
        similar_images = format_clip_pred(rangked_image, extracted_filepath, BASE_URL)

        # Pagination response
        page.predictions = predictions[0]
        page.total_image = len(filtered_image)
        page.total_page = math.ceil(len(filtered_image) / QUERY_PER_PAGE)
        page.similar_images = similar_images

        # Default response
        response.data = page.model_dump()
    else:
        response.data = page.model_dump()
    return response


router.add_api_route(
    methods=['POST'],
    path='',
    endpoint=query,
    summary='Query similar image.',
    status_code=status.HTTP_200_OK,
)
