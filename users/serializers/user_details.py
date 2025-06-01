from rest_framework import serializers
from users.models.user_details import UserDetails
from users.models.questionnaire import UserResponse
from users.serializers.questionnaire import QuestionSerializer
from apartments.models import City

class UserDetailsSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    preferred_city = serializers.SerializerMethodField()
    questionnaire_responses = serializers.SerializerMethodField()

    def get_email(self, obj):
        return obj.user.email

    def get_photo_url(self, obj):
        if obj.photo:
            return obj.photo.url
        return None

    def get_id(self, obj):
        return obj.user.id
        
    def get_preferred_city(self, obj):
        """
        Return preferred city as an object with ID and name
        """
        if obj.preferred_city:
            try:
                # Try to get the city object by name (exact match)
                city = City.objects.filter(name=obj.preferred_city).first()
                
                # If not found by exact name, try case-insensitive match
                if not city:
                    city = City.objects.filter(name__iexact=obj.preferred_city).first()
                
                if city:
                    return {
                        "id": city.id,
                        "name": city.name
                    }
                else:
                    # If city not found in database, still return structured data
                    return {
                        "name": obj.preferred_city
                    }
            except Exception as e:
                # Log the error but continue
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error finding city: {str(e)}")
                
                # Return structured data with just the name
                return {
                    "name": obj.preferred_city
                }
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
            # Log the error but return empty list
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error fetching questionnaire responses: {str(e)}")
            return []

    class Meta:
        model = UserDetails
        fields = ('id', 'email', 'first_name', 'last_name', 'gender', 'occupation', 'birth_date', 'phone_number', 'preferred_city', 'about_me', 'photo', 'photo_url', 'questionnaire_responses')
