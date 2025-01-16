import uuid
from rest_framework.exceptions import ValidationError


class UUIDValidator:
    """
    A simple validator to check if a string is a valid UUID.
    """

    def __call__(self, value):
        try:
            uuid.UUID(str(value))
        except ValueError:
            raise ValidationError("Invalid UUID format")
        return value
