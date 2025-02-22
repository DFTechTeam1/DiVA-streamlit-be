import io
import base64
from PIL import Image
from utils.logger import logging
from utils.query import QueryDatabase
from fastapi import APIRouter, status, Depends
from utils.custom_model.siglip import CustomSigLipModel
from src.schema.request_format import SearchByImage
from sqlalchemy.ext.asyncio import AsyncSession
from services.postgres.connection import get_db
from src.schema.response import ResponseDefault, Pagination
from services.postgres.models import ClientPreview
from utils.helper import CustomHelper
from utils.error.custom_error import DiVA, ServiceError, DataNotFoundError

router = APIRouter(tags=["Query"], prefix="/query")
predictor = CustomSigLipModel(model_path="models/SIGLIP_custom_model.pth")
helper = CustomHelper()


async def search_by_image_endpoint(
    schema: SearchByImage, db: AsyncSession = Depends(get_db)
) -> ResponseDefault:
    logging.info("Endpoint Search By Image.")
    response = ResponseDefault()
    pagination = Pagination()
    query = QueryDatabase(session=db)
    helper.find_image(directory="mount/192.168.100.105/Dfactory/client_preview")

    try:
        logging.info(
            f"Received base64 image string length: {len(schema.encoded_image)}"
        )
        image_data = base64.b64decode(schema.encoded_image)

        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        predictions = predictor.predict_image(image, threshold=schema.threshold)

        if not predictions:
            raise DataNotFoundError(
                detail="Prediction failed, please lower the threshold and try again."
            )

        filters = {label: True for label, score in predictions.items()}
        matching_data = await query.find(
            table=ClientPreview, fetch="all", filter="and", **filters
        )

        similar_image_filepath = [
            entry["filepath"] for entry in matching_data[: schema.image_per_page]
        ]

        pagination.prediction_label = predictions
        pagination.similar_image = similar_image_filepath
        pagination.total_image = len(matching_data)
        pagination.total_page = (
            schema.image_per_page + len(matching_data) - 1
        ) // schema.image_per_page

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
