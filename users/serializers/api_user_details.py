from rest_framework import serializers
import logging
from users.models.user_details import UserDetails
from users.models.questionnaire import UserResponse
from users.serializers.questionnaire import QuestionSerializer
from apartments.models import City

# Get logger
logger = logging.getLogger(__name__)

class ApiUserDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer for user details that matches the API specification.
    Returns all fields defined in the UserDetails schema in the API spec.
    """
    id = serializers.IntegerField(source='user.id')
    email = serializers.EmailField(source='user.email')
    photo_url = serializers.SerializerMethodField()
    preferred_city = serializers.SerializerMethodField()
    questionnaire_responses = serializers.SerializerMethodField()
    
    class Meta:
        model = UserDetails
        fields = [
            'id', 'email', 'first_name', 'last_name', 'gender',
            'occupation', 'birth_date', 'phone_number', 
            'preferred_city', 'about_me', 'photo_url', 'questionnaire_responses'
        ]
    
    def get_photo_url(self, obj):
        try:
            if obj.photo:
                return obj.photo.url
            return None
        except Exception as e:
            logger.error(f"Error getting photo URL: {str(e)}")
            return None
    
    def get_preferred_city(self, obj):
        try:
            if obj.preferred_city:
                try:
                    # Try to get the city object by name
                    city = City.objects.filter(name=obj.preferred_city).first()
                    if city:
                        return {
                            "id": str(city.id),
                            "name": city.name
                        }
                except Exception as e:
                    logger.error(f"Error getting city object: {str(e)}")
                
                # If we couldn't get a city object, return the string value
                return obj.preferred_city
            return None
        except Exception as e:
            logger.error(f"Error getting preferred city: {str(e)}")
            return None
            
    def get_questionnaire_responses(self, obj):
        """
        Return user's questionnaire responses in a structured format
        """
        try:
            # Get all responses for the user, ordered by question order
            user_responses = UserResponse.objects.filter(user=obj.user).select_related('question').order_by('question__order')
            
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
    
    def to_representation(self, instance):
        try:
            return super().to_representation(instance)
        except Exception as e:
            logger.error(f"Error in to_representation for user {getattr(instance, 'id', 'unknown')}: {str(e)}")
            # Return a minimal representation to avoid breaking the API
            return {
                'id': getattr(instance.user, 'id', None),
                'email': getattr(instance.user, 'email', ''),
                'first_name': getattr(instance, 'first_name', ''),
                'last_name': getattr(instance, 'last_name', '')
            }
