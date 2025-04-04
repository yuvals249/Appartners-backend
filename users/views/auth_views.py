"""
Authentication-related views for the users app.
"""
import logging
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import DatabaseError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from appartners.utils import generate_jwt
from users.models import UserDetails
from users.serializers import UserDetailsSerializer, UserRegistrationSerializer
from users.utils.validators import validate_and_normalize_email, validate_and_normalize_phone


class ValidateUniqueView(APIView):
    """
    Validates the user phone number and email to check validity and uniqueness.
    """
    def post(self, request):
        email = request.data.get('email')
        phone = request.data.get('phone')

        # Initialize response data
        response_data = {}
        is_valid = True
        
        # Validate and normalize email
        email_valid, normalized_email, email_error = validate_and_normalize_email(email)
        if not email_valid:
            response_data['email'] = email_error
            is_valid = False
            
        # Validate and normalize phone
        phone_valid, normalized_phone, phone_error = validate_and_normalize_phone(phone)
        if not phone_valid:
            response_data['phone'] = phone_error
            is_valid = False
        
        # If either field is invalid, return early with error
        if not is_valid:
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate email uniqueness
        try:
            # Check if email already exists in User model
            if User.objects.filter(email=normalized_email).exists():
                response_data['email'] = 'Email already exists'
                is_valid = False
                
            # Check if phone already exists in UserDetails model
            if UserDetails.objects.filter(phone_number=normalized_phone).exists():
                response_data['phone'] = 'Phone number already exists'
                is_valid = False
                
            if not is_valid:
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
                
            # If we get here, both email and phone are valid and unique
            return Response(
                {'message': 'Email and phone number are valid and unique'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error in ValidateUniqueView: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoginView(APIView):
    """
    Login endpoint to authenticate users using email and password.
    Returns user details from UserDetails model and sets a secure cookie.
    """

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        logger = logging.getLogger(__name__)
        logger.info(f"Login attempt with email: {email}")

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


class RegisterView(APIView):
    """
    Registration endpoint to create a new user with UserDetails.
    Handles image upload from React Native.
    """
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request):
        # Create a mutable copy of the request data
        data = request.data.copy()
        
        # Handle photo upload from React Native
        photo = request.FILES.get('photo')
        if not photo:
            return Response(
                {"error": "Photo is required for registration"},
                status=status.HTTP_400_BAD_REQUEST
            )
        data['photo'] = photo
            
        # Create serializer with data
        serializer = UserRegistrationSerializer(data=data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Create user and user details
            result = serializer.save()
            user = result['user']
            user_details = result['user_details']
            
            # Generate JWT token
            token = generate_jwt(user)
            
            # Serialize user details for response
            user_details_serializer = UserDetailsSerializer(user_details)
            
            return Response(
                {
                    "message": "User registered successfully",
                    "user": user_details_serializer.data,
                    "UserAuth": token
                },
                status=status.HTTP_201_CREATED
            )
        except DatabaseError:
            return Response(
                {"error": "A database error occurred. Please try again later"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
