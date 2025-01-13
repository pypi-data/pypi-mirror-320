from typing import Any

from ..Exception import ValidationError
from .BaseValidator import BaseValidator


class IsBooleanValidator(BaseValidator):
    """
    Validator that checks if a value is a bool.
    """

    def __init__(
        self, error_message: str = "Value '{}' is not a bool."
    ) -> None:

        self.error_message = error_message

    def validate(self, value: Any) -> None:

        if not isinstance(value, bool):
            if "{}" in self.error_message:
                raise ValidationError(self.error_message.format(value))

            raise ValidationError(self.error_message)
