"""
Authentication-related views for the users app.
Handles user registration, login, and validation of unique fields.
"""
import logging
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import DatabaseError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils import timezone

from appartners.utils import generate_jwt
from users.models import UserDetails
from users.serializers import UserDetailsSerializer, UserRegistrationSerializer
from users.utils.validators import validate_and_normalize_email, validate_and_normalize_phone


class ValidateUniqueView(APIView):
    """
    API endpoint for validating email and phone number uniqueness.
    Used during registration to check if email/phone are already taken.
    
    Endpoint: POST /api/v1/users/validate-unique/
    Request body:
        - email: User's email to validate
        - phone: User's phone number to validate
    
    Returns:
        - 200: Both email and phone are valid and unique
        - 400: Validation errors (email exists/invalid, phone exists/invalid)
        - 500: Server error
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
    API endpoint for user authentication.
    Handles user login and returns user details with JWT token.
    
    Endpoint: POST /api/v1/users/login/
    Request body:
        - email: User's email
        - password: User's password
    
    Returns:
        - 200: Login successful (user details + JWT token)
        - 401: Invalid credentials
        - 404: User details not found
    """
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        logger = logging.getLogger(__name__)
        logger.info(f"Login attempt with email: {email}")

        # Authenticate using Django's auth system
        user = authenticate(request, username=email, password=password)
        if not user:
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Update last login timestamp
        user.last_login = timezone.now()
        user.save()

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
    API endpoint for user registration.
    Handles new user creation with profile photo upload.
    
    Endpoint: POST /api/v1/users/register/
    Request body (multipart/form-data):
        - email: User's email
        - password: User's password
        - first_name: User's first name
        - last_name: User's last name
        - gender: User's gender
        - occupation: User's occupation
        - birth_date: User's birth date
        - preferred_city: User's preferred city
        - phone_number: User's phone number
        - about_me: User's bio (optional)
        - photo: Profile photo file
    
    Returns:
        - 201: Registration successful (user details + JWT token)
        - 400: Validation errors or missing photo
        - 500: Database error
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
