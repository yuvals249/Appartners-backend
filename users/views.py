from django.contrib.auth import authenticate
from jwt import ExpiredSignatureError, InvalidTokenError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView

from appartners.utils import generate_jwt, decode_jwt
from users.utils.validators import validate_and_normalize_email, validate_and_normalize_phone

from .serializers import (
    UserDetailsSerializer, 
    UserPreferencesGetSerializer, 
    UserRegistrationSerializer,
    QuestionnaireTemplateSerializer,
    UserResponseBulkSerializer,
    QuestionSerializer
)
from apartments.serializers.city import CitySerializer

from .models import UserPreferences, UserDetails
from apartments.models.city import City
from users.models.questionnaire import QuestionnaireTemplate, Question, UserResponse

from django.db import DatabaseError
from django.contrib.auth.models import User
import logging

class UserDetailsList(APIView):
    def get(self, request):
        user_details = UserDetails.objects.all()

        # Serialize the users data
        serializer = UserDetailsSerializer(user_details, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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


class CityPayloadView(APIView):
    """
    Returns a payload with a list of all active cities.
    """
    def get(self, request):
        try:
            # Get all active cities from the City model
            cities = City.objects.filter(active=True)
            
            # Use the CitySerializer to serialize the cities
            serializer = CitySerializer(cities, many=True)
            
            return Response({"cities": serializer.data}, status=status.HTTP_200_OK)
        except DatabaseError:
            return Response(
                {"error": "A database error occurred. Please try again later"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserPreferencesView(APIView):
    def get(self, request, user_preferences_id):
        try:
            validator = UUIDValidator()
            if not validator(user_preferences_id):
                return Response(
                    {"error": "Invalid user preferences_id ID format."},
                    status=status.HTTP_400_BAD_REQUEST
                )
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
        if photo:
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


class QuestionnaireView(APIView):
    """
    Get questionnaire structure
    """
    def get(self, request):
        try:
            # Get all questionnaire templates ordered by their order field
            questionnaires = QuestionnaireTemplate.objects.all()
            
            if not questionnaires.exists():
                return Response(
                    {"error": "No questionnaire templates found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # If a specific template ID is requested
            template_id = request.query_params.get('id')
            if template_id:
                try:
                    questionnaire = questionnaires.get(id=template_id)
                    serializer = QuestionnaireTemplateSerializer(questionnaire)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except QuestionnaireTemplate.DoesNotExist:
                    return Response(
                        {"error": f"Questionnaire template with ID {template_id} not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Otherwise return all templates
            serializer = QuestionnaireTemplateSerializer(questionnaires, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except DatabaseError:
            return Response(
                {"error": "A database error occurred. Please try again later"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserResponseView(APIView):
    """
    Submit, retrieve, and update user responses to questionnaire
    """
    def post(self, request):
        try:
            # Get the user from the token
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return Response(
                    {"error": "Authorization token required"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
            token = auth_header.split(' ')[1]
            user_id, _ = decode_jwt(token)
            user = User.objects.get(id=user_id)
            
            # Process the responses
            serializer = UserResponseBulkSerializer(
                data=request.data, 
                context={'user': user}
            )
            
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "Responses saved successfully"},
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except (ExpiredSignatureError, InvalidTokenError):
            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except DatabaseError:
            return Response(
                {"error": "A database error occurred. Please try again later"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        try:
            # Get the user from the token
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return Response(
                    {"error": "Authorization token required"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
            token = auth_header.split(' ')[1]
            user_id, _ = decode_jwt(token)
            user = User.objects.get(id=user_id)
            
            # Get all responses for the user, ordered by question order
            user_responses = UserResponse.objects.filter(user=user).select_related('question').order_by('question__order')
            
            if not user_responses.exists():
                return Response(
                    {"error": "No responses found for this user"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Create a detailed response with question details
            response_data = []
            for response in user_responses:
                question_serializer = QuestionSerializer(response.question)
                response_data.append({
                    'question': question_serializer.data,
                    'text_response': response.text_response,
                    'numeric_response': response.numeric_response,
                    'created_at': response.created_at
                })
            
            return Response(
                {"responses": response_data},
                status=status.HTTP_200_OK
            )
        except (ExpiredSignatureError, InvalidTokenError):
            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except DatabaseError:
            return Response(
                {"error": "A database error occurred. Please try again later"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request):
        try:
            # Get the user from the token
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return Response(
                    {"error": "Authorization token required"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
            token = auth_header.split(' ')[1]
            user_id, _ = decode_jwt(token)
            user = User.objects.get(id=user_id)
            
            # Process the responses (same as POST but with different status code)
            serializer = UserResponseBulkSerializer(
                data=request.data, 
                context={'user': user}
            )
            
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "Responses updated successfully"},
                    status=status.HTTP_200_OK
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except (ExpiredSignatureError, InvalidTokenError):
            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except DatabaseError:
            return Response(
                {"error": "A database error occurred. Please try again later"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
