import math
from fastapi import APIRouter, status, Depends
from services.postgre.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.secret import APPLICATION_PORT, IP_HOST
from src.schema.response import ResponseDefault, ResponsePage
from src.schema.request_format import QueryPayload
from services.custom_model.siglip import cls_model
from services.postgre.models import ClientPreview
from utils.logger import logging
from utils.query import QueryDatabase
from utils.helper import extract_path, format_clip_pred
from utils.processor import ImageProcessor
from utils.clip import query_model
from utils.error.custom_error import DataNotFoundError, ServiceError, DiVA

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
    BASE_URL = f'http://{IP_HOST}:{APPLICATION_PORT}/api/v1/query/stream?image_path='

    # DB query utils
    IMAGE_PER_PAGE = 50
    QUERY_PER_PAGE = 100

    current_image = None

    logging.info(f'Processing page {schema.page}.')

    try:
        if schema.page == 1:
            # Image processing
            decoded = processor.decode(schema.encoded_image)

            # Predict uploaded image
            prediction = cls_model.predict(
                images=[decoded], threshold=schema.threshold, batch_size=1
            )

            # Format prediction label
            formatted_result = cls_model.to_dict(prediction[0])

            # Query db
            filtered_image = await session.find(
                table=ClientPreview, fetch='all', filter='or', **formatted_result
            )

            if not filtered_image:
                raise DataNotFoundError(detail=f'Page {schema.page} dont have any data.')

            extracted_filepath = list(set(extract_path(filtered_image)))

            if schema.filename:
                logging.info(f'Query database using filter {schema.filename}.')
                current_image = await session.find(table=ClientPreview, filename=schema.filename)
                if current_image:
                    extracted_filepath.insert(0, current_image['filepath'])
                    logging.info('Query image inserted.')
                else:
                    logging.warning('Using new image.')
                    processor.save_image(
                        encoded_data=schema.encoded_image, filename=schema.filename
                    )

            # Process filtered image
            converted_image = processor.resize(extracted_filepath[:QUERY_PER_PAGE])

            # CLIP encoding
            query_image = query_model.encode(decoded, batch_size=1)
            encoded_image = query_model.encode(converted_image, batch_size=4)

            # Query similar images
            rangked_image = query_model.query(query_image, encoded_image, IMAGE_PER_PAGE)
            similar_image = format_clip_pred(rangked_image, extracted_filepath, BASE_URL)

            # Pagination response
            page.prediction = prediction[0]
            page.total_image = len(filtered_image)
            page.total_page = math.ceil(len(filtered_image) / QUERY_PER_PAGE)
            page.similar_image = similar_image

            # Default response
            response.data = page.model_dump()

        else:
            # Image processing
            decoded = processor.decode(schema.encoded_image)

            # Format prediction label
            formatted_result = cls_model.to_dict(schema.prediction)

            # Query db
            filtered_image = await session.find(
                table=ClientPreview,
                fetch='all',
                filter='or',
                limit=QUERY_PER_PAGE,
                offset=(schema.page * QUERY_PER_PAGE) - QUERY_PER_PAGE,
                **formatted_result,
            )

            query_all = await session.find(
                table=ClientPreview,
                fetch='all',
                filter='or',
                **formatted_result,
            )

            if not filtered_image:
                raise DataNotFoundError(detail=f'Page {schema.page} dont have any data.')

            extracted_filepath = list(set(extract_path(filtered_image)))

            # Process filtered image
            converted_image = processor.resize(extracted_filepath[:QUERY_PER_PAGE])

            # CLIP encoding
            query_image = query_model.encode(decoded, batch_size=1)
            encoded_image = query_model.encode(converted_image, batch_size=4)

            # Query similar images
            rangked_image = query_model.query(query_image, encoded_image, IMAGE_PER_PAGE)
            similar_image = format_clip_pred(rangked_image, extracted_filepath, BASE_URL)

            # Pagination response
            page.prediction = schema.prediction
            page.total_image = len(query_all)
            page.total_page = math.ceil(len(query_all) / QUERY_PER_PAGE)
            page.similar_image = similar_image

            # Default response
            response.data = page.model_dump()

    except DiVA:
        raise

    except Exception as e:
        logging.error(f'Error in search_by_image_endpoint: {e}')
        raise ServiceError(detail='Internal Server Error.', name='DiVA')
    return response


router.add_api_route(
    methods=['POST'],
    path='',
    endpoint=query,
    summary='Query similar image.',
    status_code=status.HTTP_200_OK,
)
