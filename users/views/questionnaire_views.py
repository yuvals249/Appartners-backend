"""
Questionnaire-related views for the users app.
"""
from jwt import ExpiredSignatureError, InvalidTokenError
from django.contrib.auth.models import User
from django.db import DatabaseError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models.questionnaire import QuestionnaireTemplate, UserResponse
from users.serializers import (
    QuestionnaireTemplateSerializer,
    UserResponseBulkSerializer,
    QuestionSerializer
)


class QuestionnaireView(APIView):
    authentication_classes = []  # No authentication required
    permission_classes = []  # No permissions required
    """
    Get questionnaire structure
    """
    def get(self, request):
        try:
            # Get all questionnaire templates ordered by their order field
            questionnaires = QuestionnaireTemplate.objects.all()
            
            if not questionnaires.exists():
                return Response(
                    {"errors": "No questionnaire templates found"},
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
                        {"errors": f"Questionnaire template with ID {template_id} not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Otherwise return all templates
            serializer = QuestionnaireTemplateSerializer(questionnaires, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except DatabaseError:
            return Response(
                {"errors": "A database error occurred. Please try again later"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserResponseView(APIView):
    """
    Submit, retrieve, and update user responses to questionnaire
    """
    def post(self, request):
        try:
            # Return error if authentication failed
            if request.token_error:
                return request.token_error
                
            # Get user_id from the request (set by middleware)
            user_id = request.user_from_token
            user = User.objects.get(id=user_id)
            
            # Delete existing responses for this user
            UserResponse.objects.filter(user=user).delete()
            
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
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response(
                {"errors": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except DatabaseError:
            return Response(
                {"errors": "A database error occurred. Please try again later"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        try:
            # Return error if authentication failed
            if request.token_error:
                return request.token_error
                
            # Get user_id from the request (set by middleware)
            user_id = request.user_from_token
            user = User.objects.get(id=user_id)
            
            # Get all responses for the user, ordered by question order
            user_responses = UserResponse.objects.filter(user=user).select_related('question').order_by('question__order')
            
            # Create a detailed response with question details (empty list if no responses)
            response_data = []
            for response in user_responses:
                question_serializer = QuestionSerializer(response.question)
                response_data.append({
                    'question': question_serializer.data,
                    'text_response': response.text_response,
                    'numeric_response': response.numeric_response,
                    'created_at': response.created_at
                })
            
            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"errors": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except DatabaseError:
            return Response(
                {"errors": "A database error occurred. Please try again later"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
