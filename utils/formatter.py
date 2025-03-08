import urllib.parse
from utils.logger import logging
from collections import OrderedDict
from typing import Literal, Union


class CustomFormatter:
    def format_cls_label(
        self, data: Union[dict, list], target_type: Literal["dict", "list"]
    ) -> Union[list, dict]:
        logging.info("Formatting cls prediction.")
        if isinstance(data, dict):
            if target_type == "dict":
                return {label: True for label, score in data.items()}
            else:
                return list(data.values())
        else:
            if target_type == "dict":
                return {entry: True for entry in data}
            else:
                raise ValueError("Feature not implemented!")

    def format_prefix_path(self, filtered_image: list, prefix_path: str) -> list:
        logging.info("Formatting prefix path.")
        return [prefix_path + entry["filepath"] for entry in filtered_image]

    def format_cls_model_architecture(self, state_dict: dict) -> dict:
        logging.info("Formating model architecture.")
        formatted_state = OrderedDict()
        for key, value in state_dict.items():
            new_key = key.replace("module.", "")
            formatted_state[new_key] = value
        return formatted_state

    def format_trained_cls_label(self, label: dict) -> dict:
        logging.info("Formatting trained label.")
        return {int(key): value for key, value in label.items()}

    def format_clip_output(
        self, actual_path: list, clip_result: list, base_url: str
    ) -> list:
        formatted_results = []

        for entry in clip_result:
            image_path = actual_path[entry["corpus_id"]]
            encoded_path = urllib.parse.quote(image_path, safe="")
            formatted_results.append(
                {
                    "filepath": image_path,
                    "accuracy": round(entry["score"], 2),
                    "stream_image": f"{base_url}/query/stream-image?image_path={encoded_path}",
                }
            )

        return formatted_results
