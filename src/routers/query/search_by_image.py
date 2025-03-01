from utils.logger import logging
from utils.query import QueryDatabase
from utils.model import SigLIP, CLIP
from utils.helper import CustomHelper
from utils.validator import RequestValidator
from utils.preprocessing import ImageProcessing
from utils.formatter import CustomFormatter
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
    formatter = CustomFormatter()
    validator = RequestValidator()

    # Model
    cls_model = SigLIP()
    query_model = CLIP(model_name=schema.base_model)

    # Database
    query = QueryDatabase(session=db)

    # Classification label
    trained_label = formatter.format_cls_label(
        data=cls_model.trained_label, target_type="list"
    )
    next_page, validated_label = validator.validate_label(
        actual_label=trained_label, predicted_label=schema.prediction_label
    )

    # Utilities
    start_time = helper.local_time()

    try:
        if not next_page:
            logging.info("Performing query images.")
            decoded_image = processor.decode_image(encoded_image=schema.encoded_image)

            cls_predicted = cls_model.predict(
                decoded_image=decoded_image, threshold=schema.threshold
            )
            if not cls_predicted:
                raise DataNotFoundError(
                    detail="Prediction failed, please lower the threshold and try again."
                )

            filters = formatter.format_cls_label(data=cls_predicted, target_type="dict")
            filtered_image = await query.find(
                table=ClientPreview,
                fetch="all",
                filter="or",
                limit=150,
                **filters,
            )

            query_all = await query.find(
                table=ClientPreview,
                fetch="all",
                filter="or",
                **filters,
            )

            formatted_path = formatter.format_prefix_path(
                filtered_image=filtered_image, prefix_path="mount/"
            )
            processed_image = processor.process_image(image_paths=formatted_path)

            custom_encoding = query_model.encode(image=processed_image)
            query_image = query_model.search(
                query=decoded_image,
                encoded_image=custom_encoding,
                k=schema.image_per_page,
            )
            formatted_result = formatter.format_clip_output(
                actual_path=formatted_path, clip_result=query_image
            )
            total_page = (
                schema.image_per_page + len(formatted_result) - 1
            ) // schema.image_per_page

            total_image = len(query_all)

            pagination.prediction_label = cls_predicted
            pagination.similar_image = formatted_result
            pagination.total_image = total_image
            pagination.total_page = total_page
            pagination.total_chungked_image = schema.image_per_page

            response.message = "Prediction successful."
            response.data = pagination.model_dump()
        else:
            filters = formatter.format_cls_label(
                data=validated_label, target_type="dict"
            )

            filtered_image = await query.find(
                table=ClientPreview,
                fetch="all",
                filter="or",
                limit=150,
                offset=(schema.page * schema.image_per_page) - schema.image_per_page,
                **filters,
            )
            if filtered_image:
                formatted_path = formatter.format_prefix_path(
                    filtered_image=filtered_image, prefix_path="mount/"
                )
                processed_image = processor.process_image(image_paths=formatted_path)

                custom_encoding = query_model.encode(image=processed_image)

                decoded_image = processor.decode_image(
                    encoded_image=schema.encoded_image
                )
                query_image = query_model.search(
                    query=decoded_image,
                    encoded_image=custom_encoding,
                    k=schema.image_per_page,
                )
                formatted_result = formatter.format_clip_output(
                    actual_path=formatted_path, clip_result=query_image
                )

                total_chungked_image = (
                    len(formatted_result) if formatted_result else None
                )

                pagination.prediction_label = filters
                pagination.similar_image = formatted_result
                pagination.total_page = None
                pagination.total_image = None
                pagination.total_chungked_image = total_chungked_image
                response.message = f"Query page {schema.page} successful."
                response.data = pagination.model_dump()
            else:
                response.message = f"Page {schema.page} dont have any data."

        end_time = helper.local_time()
        elapsed_time = end_time - start_time
        logging.info(f"Elapsed time: {elapsed_time}")

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
