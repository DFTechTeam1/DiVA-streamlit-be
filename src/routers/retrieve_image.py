import os
from pathlib import Path
from fastapi import APIRouter, status, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from services.postgre.connection import get_db
from services.postgre.models import ImageMetadata, UploadedImage
from src.schema.response import ResponseDefault, ResponsePage
from src.schema.request_format import QueryPayload
from src.secret import APPLICATION_PORT, IP_HOST
from utils.zero_shot.processor import ImageProcessor
from utils.zero_shot.classifier import MODEL, FAISS_IDX, VectorDatabase, TOTAL_IMAGE
from utils.logger import logging
from utils.helper import format
from utils.database.query import QueryDatabase
from utils.error.custom_error import ServiceError, DiVA, DataNotFoundError

router = APIRouter(tags=['Query'], prefix='/query')


async def query(request: Request, schema: QueryPayload, db: AsyncSession = Depends(get_db)) -> ResponseDefault:
    logging.info('Endpoint query.')

    # API response
    response = ResponseDefault()
    page = ResponsePage()

    # DB session
    session = QueryDatabase(session=db)

    # Image processor
    processor = ImageProcessor()

    # Path management
    BASE_URL = f'http://{IP_HOST}:{APPLICATION_PORT}/api/v1/query/stream?image_path='
    FAISS_IDX = request.app.state.faiss_index

    # Query image
    EXTRACT_IMAGE = 50
    try:
        # Decode and hashing
        decoded_image = processor.decode(schema.encoded_image)
        hash_image = processor.hash(decoded_image)

        # Extract image feature
        extracted_features = MODEL.extract_feature(decoded_image)

        # Retrieve similar image
        all_entry = FAISS_IDX.search(extracted_features, schema.threshold)
        retrieved = FAISS_IDX.move_page(schema.page, EXTRACT_IMAGE)
        total_pages = (len(all_entry) + (EXTRACT_IMAGE-1)) // EXTRACT_IMAGE

        # Query db
        saved_image = await session.find(ImageMetadata, checksum=hash_image)
        if saved_image:
            logging.info(f"Query existing client preview: {saved_image['filename']}")
            await session.insert(UploadedImage, {
                'checksum': hash_image,
                "threshold": schema.threshold,
                "upload_id": saved_image['id'],
                "total_page": total_pages,
                "is_image_saved": False,

            })
        else:
            logging.info(f"Query new data: {hash_image}")
            processor.save(decoded_image, hash_image)
            await session.insert(UploadedImage, {
                'checksum': hash_image,
                "threshold": schema.threshold,
                "total_page": total_pages,
                "is_image_saved": True,
            })
            
        
        # Check if retrieved is empty
        if not retrieved:
            raise DataNotFoundError(f"Similar image not found.")
        
        similar_image = [format(entry, BASE_URL) for entry in retrieved]

        page.total_page = total_pages
        page.similar_image = similar_image
        response.data = page.model_dump()


    except DiVA:
        raise

    except Exception as e:
        logging.error(f'Error in query endpoint: {e}')
        raise ServiceError(detail='Internal Server Error.', name='DiVA')
    return response


router.add_api_route(
    methods=['POST'],
    path='',
    endpoint=query,
    summary='Query similar image.',
    status_code=status.HTTP_200_OK,
)
