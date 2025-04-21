from rest_framework import serializers
import logging
from users.models.user_details import UserDetails

# Get logger
logger = logging.getLogger(__name__)

class ApiUserDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer for user details that matches the API specification.
    Returns all fields defined in the UserDetails schema in the API spec.
    """
    id = serializers.IntegerField(source='user.id')
    email = serializers.EmailField(source='user.email')
    photo = serializers.SerializerMethodField()
    preferred_city = serializers.SerializerMethodField()
    
    class Meta:
        model = UserDetails
        fields = [
            'id', 'email', 'first_name', 'last_name', 'gender',
            'occupation', 'birth_date', 'phone_number', 
            'preferred_city', 'about_me', 'photo'
        ]
    
    def get_photo(self, obj):
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
                return str(obj.preferred_city.id)
            return None
        except Exception as e:
            logger.error(f"Error getting preferred city: {str(e)}")
            return None
            
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
