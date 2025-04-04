"""
Questionnaire-related views for the users app.
"""
from jwt import ExpiredSignatureError, InvalidTokenError
from django.contrib.auth.models import User
from django.db import DatabaseError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from appartners.utils import decode_jwt
from users.models.questionnaire import QuestionnaireTemplate, UserResponse
from users.serializers import (
    QuestionnaireTemplateSerializer,
    UserResponseBulkSerializer,
    QuestionSerializer
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
                response_data,
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
