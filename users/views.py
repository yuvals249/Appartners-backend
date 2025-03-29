import jwt
from django.contrib.auth import authenticate
from jwt import ExpiredSignatureError, InvalidTokenError
from rest_framework import status
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from appartners.utils import generate_jwt

from .serializers import UserDetailsSerializer, UserPreferencesGetSerializer

from .models import UserPreferences, UserDetails

from rest_framework.views import APIView
from appartners.validators import UUIDValidator
from django.db import DatabaseError


class UserDetailsList(APIView):
    def get(self, request):
        user_details = UserDetails.objects.all()

        # Serialize the users data
        serializer = UserDetailsSerializer(user_details, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class UserPreferencesView(APIView):
    def get(self, request, user_preferences_id):
        try:
            # validator = UUIDValidator()
            # if not validator(user_preferences_id):
            #     return Response(
            #         {"error": "Invalid user preferences_id ID format."},
            #         status=status.HTTP_400_BAD_REQUEST
            #     )
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


class LoginView(APIView):
    """
    Login endpoint to authenticate users using email and password.
    Returns user details from UserDetails model and sets a secure cookie.
    """

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # Authenticate the user
        user = authenticate(request, username=email, password=password)
        if not user:
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        # Fetch the user's details from the UserDetails model
        try:
            user_details = UserDetails.objects.get(user=user)
        except UserDetails.DoesNotExist:
            return Response(
                {"error": "User details not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Serialize the user details
        serializer = UserDetailsSerializer(user_details)

        token = generate_jwt(user)

        # Include the token in the response
        return Response(
            {
                "user": serializer.data,
                "UserAuth": token
            },
            status=status.HTTP_200_OK)
