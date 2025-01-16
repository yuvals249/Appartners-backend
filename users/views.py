import jwt
from django.contrib.auth import authenticate
from jwt import ExpiredSignatureError, InvalidTokenError
from rest_framework import status
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from appartners.utils import generate_jwt
from users.serializers.user_details import UserDetailsSerializer
from users.serializers.user_preferences import UserPreferencesSerializer

from users.models.user_details import UserDetails
from users.models.user_preferences import UserPreferences
from rest_framework.views import APIView


class UserDetailsList(ListAPIView):
    queryset = UserDetails.objects.all()
    serializer_class = UserDetailsSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_fields = ('id',)
    search_fields = ('first_name', 'last_name', 'phone_number',)


class UserPreferencesList(ListAPIView):
    queryset = UserPreferences.objects.all()
    serializer_class = UserPreferencesSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_fields = ('id', 'area', 'max_price', 'move_in_date', 'number_of_roommates')


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
