"""
User-related views for the users app.
"""
from django.db import DatabaseError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import UserDetails, UserPreferences
from users.serializers import UserDetailsSerializer, UserPreferencesGetSerializer


class UserDetailsList(APIView):
    """
    View to list all user details.
    """
    def get(self, request):
        user_details = UserDetails.objects.all()

        # Serialize the users data
        serializer = UserDetailsSerializer(user_details, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserPreferencesView(APIView):
    """
    View to retrieve user preferences by ID.
    """
    def get(self, request, user_preferences_id):
        try:
            # Check if the ID is a valid UUID
            try:
                from django.core.validators import UUIDValidator
                validator = UUIDValidator()
                if not validator(user_preferences_id):
                    return Response(
                        {"error": "Invalid user preferences_id ID format."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ImportError:
                # If UUIDValidator is not available, continue without validation
                pass
                
            user_preferences = UserPreferences.objects.get(user_id=user_preferences_id)
        except UserPreferences.DoesNotExist:
            return Response({"error": "user preferences not found."}, status=status.HTTP_404_NOT_FOUND)
        except DatabaseError:
            return Response(
                {"error": "A database error occurred. Please try again later"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        # Serialize the apartment data
        serializer = UserPreferencesGetSerializer(user_preferences)
        return Response(serializer.data, status=status.HTTP_200_OK)
