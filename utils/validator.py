from typing import Optional


class RequestValidator:
    def validate_label(
        self, actual_label: list, predicted_label: list
    ) -> tuple[bool, Optional[list]]:
        non_existing_label = [
            entry for entry in predicted_label if entry not in actual_label
        ]
        if non_existing_label:
            return (False, None)

        return (True, predicted_label)
