import base64
import io
import asyncio


from utils.logger import logging
from io import BytesIO
from PIL import Image
from services.postgres.connection import database_connection
from utils.query import QueryDatabase
from utils.helper import CustomHelper
from utils.custom_model.clip_vit import CustomCLIPModel
from utils.custom_model.siglip import CustomSigLipModel
from utils.custom_model.processor import ImageProcessor
from services.postgres.models import ClientPreview


helper = CustomHelper()

start_time = helper.local_time()

custom_clip = CustomCLIPModel()
custom_siglip = CustomSigLipModel(model_path="models/SIGLIP_custom_model.pth")
processor = ImageProcessor()
image_list = helper.find_image(
    directory="mount/192.168.100.105/Dfactory/client_preview"
)


def encode_image(image_path: str) -> str:
    with Image.open(image_path) as image:
        buffered = BytesIO()
        image_ext = image_path.split(".")[-1].upper()
        if image_ext == "JPG":
            image_ext = "JPEG"
        image.save(buffered, format=image_ext)
        return base64.b64encode(buffered.getvalue()).decode("utf-8")


def decoder_image(encoded_image: str) -> type[Image]:
    image_data = base64.b64decode(encoded_image)
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    image = image.resize((255, 255))
    return image


# target_image = image_list[0]
# encoded = encode_image(image_path=target_image)
# decoded = decoder_image(encoded_image=encoded)
# predicted_image = custom_siglip.predict_image(decoded)
# if not predicted_image:
#     raise DataNotFoundError("Prediction not found!")
# filters = {label: True for label, score in predicted_image.items()}


async def main(filters: dict, total_entry: int) -> list:
    engine = database_connection()
    async with engine.begin() as conn:
        query = QueryDatabase(session=conn)

        find_query = await query.find(
            table=ClientPreview,
            fetch="all",
            limit=total_entry,
            # filter="or",
            **filters,
        )
        return find_query


def format_path(filtered_image: list) -> list:
    return ["mount" + "/" + entry["filepath"] for entry in filtered_image]


def filter_output(actual_path: list, clip_result: list) -> None:
    for entry in clip_result:
        accuracy = entry["score"]
        filepath = actual_path[entry["corpus_id"]]
        print(filepath, accuracy)


def text_filter(filter_list: list) -> dict:
    categories = [
        "nature",
        "artifacts",
        "living_beings",
        "conceptual",
        "art_deco",
        "architectural",
        "artistic",
        "sci_fi",
        "fantasy",
        "afternoon",
        "sunset_sunrise",
        "night",
        "warm",
        "cool",
        "neutral",
        "gold",
    ]

    invalid_filters = [entry for entry in filter_list if entry not in categories]

    if invalid_filters:
        raise ValueError(
            f"Filter(s) {', '.join(invalid_filters)} not available. Please use one of: {', '.join(categories)}"
        )

    return {entry: True for entry in filter_list}


def query_image(image_path: str, total_extracted_image: int, total_entry: int) -> list:
    start_time = helper.local_time()
    encoded = encode_image(image_path=image_path)
    decoded = decoder_image(encoded_image=encoded)
    print(type(decoded))
    print(decoded.resize((255, 255)))

    predicted_image = custom_siglip.predict_image(decoded)
    filters = {label: True for label, score in predicted_image.items()}

    similar_image = asyncio.run(main(filters, total_entry))
    formatted_path = format_path(filtered_image=similar_image)

    processed_image = processor.process_image(image_paths=formatted_path)
    encoded_data = custom_clip.run_encoder(image=processed_image)
    print(type(encoded_data))

    similar_image = custom_clip.search(
        query=decoded, encoded_image=encoded_data, k=total_extracted_image
    )
    end_time = helper.local_time()
    print(f"{image_path}")
    logging.info(f"Elapsed time: {end_time - start_time}")
    return similar_image


test = query_image(image_path=image_list[25], total_extracted_image=50, total_entry=10)
filter_output(image_list, test)
