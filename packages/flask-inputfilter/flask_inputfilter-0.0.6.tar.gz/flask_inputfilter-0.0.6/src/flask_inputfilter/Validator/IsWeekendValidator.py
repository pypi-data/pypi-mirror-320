from datetime import datetime
from typing import Any

from ..Exception import ValidationError


class IsWeekendValidator:
    """
    Validator that checks if a date is on a weekend (Saturday or Sunday).
    Supports datetime and ISO 8601 formatted strings.
    """

    def __init__(
        self, error_message: str = "Date '{}' is not on a weekend."
    ) -> None:
        self.error_message = error_message

    def validate(self, value: Any) -> None:
        value_datetime = self._parse_date(value)

        if value_datetime.weekday() not in (5, 6):
            if "{}" in self.error_message:
                raise ValidationError(self.error_message.format(value))

            raise ValidationError(self.error_message)

    def _parse_date(self, value: Any) -> datetime:
        if isinstance(value, datetime):
            return value

        elif isinstance(value, str):
            try:
                return datetime.fromisoformat(value)

            except ValueError:
                raise ValidationError(f"Invalid ISO 8601 format: {value}")

        else:
            raise ValidationError(
                f"Unsupported type for weekend validation: {type(value)}"
            )
