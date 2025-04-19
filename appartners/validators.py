import uuid
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status


class UUIDValidator:
    """
    UUID validation utility with methods for both serializers and views.
    """
    
    @staticmethod
    def validate(value):
        """
        Validate a UUID string and return a tuple (is_valid, error_response).
        
        Returns:
            tuple: (is_valid, error_response)
        """
        try:
            uuid.UUID(str(value))
            return True, None
        except ValueError:
            return False, Response(
                {"error": "Invalid UUID format"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def __call__(self, value):
        """For serializer field validation"""
        try:
            uuid.UUID(str(value))
            return value
        except ValueError:
            raise ValidationError("Invalid UUID format")
