from rest_framework import serializers
from django.contrib.auth.models import User
from users.models.user_details import UserDetails
from users.models.questionnaire import UserResponse
from users.serializers.questionnaire import QuestionSerializer
from apartments.models import City
import logging

logger = logging.getLogger(__name__)

class UserBasicSerializer(serializers.ModelSerializer):
    """
    Serializer for basic user information, combining data from User and UserDetails models.
    
    This serializer is used across the application to provide consistent user information
    in API responses, particularly in:
    - Chat messages (showing sender details)
    - Chat room participants
    - User listings
    - Basic profile information
    
    The serializer combines data from Django's User model and our custom UserDetails model,
    providing a unified view of user information without exposing sensitive data.
    """
    user_id = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()
    preferred_city = serializers.SerializerMethodField()
    questionnaire_responses = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()

    class Meta:
        model = UserDetails
        fields = ['id', 'user_id', 'email', 'first_name', 'last_name', 'phone_number', 'photo_url', 
        'preferred_city', 'questionnaire_responses', 'bio']
        
    def get_user_id(self, obj):
        """
        Get user ID from either User or UserDetails object
        """
        if isinstance(obj, User):
            return obj.id
        return obj.user.id
        
    def get_email(self, obj):
        """
        Get email from either User or UserDetails object
        """
        if isinstance(obj, User):
            return obj.email
        return obj.user.email

    def get_first_name(self, obj):
        """
        Get first_name from either User or UserDetails object
        """
        if isinstance(obj, User):
            user_details = UserDetails.objects.filter(user=obj).first()
            return user_details.first_name if user_details else ""
        return obj.first_name

    def get_last_name(self, obj):
        """
        Get last_name from either User or UserDetails object
        """
        if isinstance(obj, User):
            user_details = UserDetails.objects.filter(user=obj).first()
            return user_details.last_name if user_details else ""
        return obj.last_name

    def get_phone_number(self, obj):
        """
        Get phone_number from either User or UserDetails object
        """
        if isinstance(obj, User):
            user_details = UserDetails.objects.filter(user=obj).first()
            return user_details.phone_number if user_details else ""
        return obj.phone_number

    def get_photo_url(self, obj):
        """
        Get photo URL from either User or UserDetails object.
        Returns the URL of the user's photo if it exists, None otherwise.
        """
        try:
            if isinstance(obj, User):
                user_details = UserDetails.objects.filter(user=obj).first()
                if user_details and user_details.photo:
                    return user_details.photo.url
                return None
            if obj.photo:
                return obj.photo.url
            return None
        except Exception as e:
            logger.error(f"Error getting photo URL: {str(e)}")
            return None

    def get_preferred_city(self, obj):
        """
        Return preferred city as an object with ID and name
        """
        try:
            # Determine if we're dealing with User or UserDetails
            if isinstance(obj, User):
                user_details = UserDetails.objects.filter(user=obj).first()
                if user_details and user_details.preferred_city:
                    preferred_city = user_details.preferred_city
                else:
                    return None
            else:  # UserDetails
                if not obj.preferred_city:
                    return None
                preferred_city = obj.preferred_city
                
            # Try to get the city object by name (exact match)
            city = City.objects.filter(name=preferred_city).first()
            
            # If not found by exact name, try case-insensitive match
            if not city:
                city = City.objects.filter(name__iexact=preferred_city).first()
            
            if city:
                return {
                    "id": city.id,
                    "name": city.name
                }
            else:
                # If city not found in database, still return structured data
                return {
                    "name": preferred_city
                }
        except Exception as e:
            # Log the error but continue
            logger.error(f"Error finding city: {str(e)}")
            
            # Return None on error
            return None

    def get_questionnaire_responses(self, obj):
        """
        Return user's questionnaire responses in a structured format
        """
        try:
            # Determine the user object based on whether we received a User or UserDetails
            if isinstance(obj, User):
                user = obj
            else:
                user = obj.user
                
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
            
            return response_data
        except Exception as e:
            logger.error(f"Error fetching questionnaire responses: {str(e)}")
            return []

    def get_bio(self, obj):
        """
        Get the user's bio/about_me field
        """
        try:
            if isinstance(obj, User):
                user_details = UserDetails.objects.filter(user=obj).first()
                return user_details.about_me if user_details else ""
            return obj.about_me if hasattr(obj, 'about_me') else ""
        except Exception as e:
            logger.error(f"Error getting about_me: {str(e)}")
            return ""