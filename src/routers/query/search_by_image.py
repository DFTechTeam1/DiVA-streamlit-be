from utils.logger import logging
from utils.query import QueryDatabase
from utils.model import SigLIP, CLIP
from utils.helper import CustomHelper
from urllib.parse import quote
from utils.preprocessing import ImageProcessing
from utils.error.custom_error import DiVA, ServiceError, DataNotFoundError
from src.schema.response import ResponseDefault, Pagination
from src.schema.request_format import SearchByImage
from services.postgres.models import ClientPreview
from services.postgres.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, status, Depends

router = APIRouter(tags=["Query"], prefix="/query")


async def search_by_image_endpoint(
    schema: SearchByImage, db: AsyncSession = Depends(get_db)
) -> ResponseDefault:
    logging.info("Endpoint Search By Image.")

    # API response model
    response = ResponseDefault()
    pagination = Pagination()

    # API Helper
    helper = CustomHelper()
    processor = ImageProcessing()

    # Model
    cls_model = SigLIP()
    query_model = CLIP(model_name=schema.base_model)

    # Database
    query = QueryDatabase(session=db)

    helper.find_image(directory="mount/192.168.100.105/Dfactory/client_preview")

    BASE_URL = "http://localhost:8000/api/v1/query/stream-image?image_path="

    def format_filepaths(similar_images):
        return [
            {
                "filepath": f"{BASE_URL}{quote(image['filepath'], safe='')}",
                "accuracy": image["accuracy"],
            }
            for image in similar_images
        ]

    try:
        decoded_image = processor.decode_image(encoded_image=schema.encoded_image)

        cls_predicted = cls_model.predict(
            decoded_image=decoded_image, threshold=schema.threshold
        )
        if not cls_predicted:
            raise DataNotFoundError(
                detail="Prediction failed, please lower the threshold and try again."
            )

        filters = cls_model.format_predicted_data(predicted_label=cls_predicted)
        filtered_image = await query.find(
            table=ClientPreview,
            fetch="all",
            filter=schema.filter_type,
            limit=schema.image_per_page,
            **filters,
        )

        formatted_path = helper.format_path(
            filtered_image=filtered_image, prefix_path="mount/"
        )
        processed_image = processor.process_image(image_paths=formatted_path)

        custom_encoding = query_model.encode(image=processed_image)
        query_image = query_model.search(
            query=decoded_image, encoded_image=custom_encoding, k=schema.image_per_page
        )
        formatted_result = query_model.filter_output(
            actual_path=formatted_path, clip_result=query_image
        )
        print(len(formatted_result))

        total_similar_image = len(formatted_result)
        total_page = (
            schema.image_per_page + len(formatted_result) - 1
        ) // schema.image_per_page

        [
            {
                "filepath": entry["filepath"],
                "stream_url": f"http://localhost:8000/query/stream-image?image_path={entry['filepath']}",
            }
            for entry in formatted_result[: schema.image_per_page]
        ]

        pagination.prediction_label = cls_predicted
        pagination.similar_image = format_filepaths(formatted_result)
        pagination.total_image = total_similar_image
        pagination.total_page = total_page

        response.message = "Prediction successful"
        response.data = pagination.model_dump()
    except DiVA:
        raise

    except Exception as e:
        logging.error(f"Error in search_by_image_endpoint: {e}")
        raise ServiceError(detail="Internal Server Error.", name="DiVA")

    return response


router.add_api_route(
    methods=["POST"],
    path="/image",
    response_model=ResponseDefault,
    endpoint=search_by_image_endpoint,
    status_code=status.HTTP_200_OK,
)
