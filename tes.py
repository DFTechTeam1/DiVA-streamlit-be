# import time
# import math
# import logging
# import torch
# import asyncio
# from typing import Optional
# from pathlib import Path
# from services.custom_model.siglip import CustomModel
# from services.postgre.connection import get_db
# from services.postgre.models import ClientPreview
# from utils.query import QueryDatabase
# from utils.helper import extract_path
# from utils.processor import ImageProcessor
# from utils.clip import query_model
# # from sentence_transformers import SentenceTransformer, util


# async def main() -> Optional[list]:
#     QUERY_PER_PAGE = 200
#     processor = ImageProcessor()
#     BASE_DIR = Path(__file__).resolve().parents[0]
#     MODEL_PATH = BASE_DIR / 'models' / 'SIGLIP_custom_model.pth'
#     TRAINED_LABEL = BASE_DIR / 'json' / 'trained_label.json'
#     IMAGE_PATH = '/home/dfactory/Project/DiVA-streamlit-be/mount/192.168.100.102/Queue_Job_4/2023/03_MARET/05_MARET_DANNY_NOVIA/PREVIEW/2023_03_05_Danny Novia_Opening.png'
#     model = CustomModel(model_path=MODEL_PATH, label_path=TRAINED_LABEL)

#     encoded = processor.encode(IMAGE_PATH)
#     decoded = processor.decode(encoded)
#     resized = processor.resize(decoded)
#     results = model.predict(images=resized, threshold=0.9, batch_size=10)
#     formatted_result = model.to_dict(results[0])

#     fullpaths = []
#     async for session in get_db():
#         db = QueryDatabase(session=session)
#         try:
#             query_images = await db.find(
#                 table=ClientPreview,
#                 fetch='all',
#                 filter='or',
#                 limit=QUERY_PER_PAGE,
#                 **formatted_result,
#             )
#             all_data = await db.find(
#                 table=ClientPreview, fetch='all', filter='or', **formatted_result
#             )
#             if query_images:
#                 fullpaths = extract_path(query_images)

#         except Exception as e:
#             logging.error(f'Failed to insert record: {e}')

#     if not fullpaths:
#         logging.warning('No matching images found.')
#         return None

#     start_time = time.time()
#     response = {}
#     total_image = len(all_data)
#     total_page = math.ceil(total_image / QUERY_PER_PAGE)
#     response['total_image'] = total_image
#     response['total_page'] = total_page

#     'cuda' if torch.cuda.is_available() else 'cpu'
#     # load_clip =  SentenceTransformer(model_name_or_path='clip-ViT-B-16', device=device)
#     logging.info('Initiating encoding process.')
#     converted_image = processor.resize(fullpaths)
#     query_model.encode(converted_image, batch_size=2)
#     query_model.encode(resized, batch_size=2)
#     results = query_model.query(query, encoded, k=50)
#     ranked_results = [
#         {'path': fullpaths[item['corpus_id']], 'score': item['score']} for item in results
#     ]
#     response['ranked_results'] = ranked_results
#     print(response)
#     print(f'elapsed time: {time.time() - start_time}')


# if __name__ == '__main__':
#     tes = asyncio.run(main())


from utils.processor import ImageProcessor

processor = ImageProcessor()

IMAGE_PATH = '/home/dfactory/Project/DiVA-streamlit-be/mount/192.168.100.102/Queue_Job_5/2023/08_AGUSTUS/04_AGUSTUS_PAMERAN_DOUBLE_TREE/PREVIEW/2023_08_4_Pameran_Double_Tree_SB.png'
encoded_image = processor.encode(image_path=IMAGE_PATH)
print(encoded_image[:10])
with open('encoded.txt', 'w') as file:
    file.write(encoded_image)
