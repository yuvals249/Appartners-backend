from rest_framework import serializers
from users.models.user_details import UserDetails
from apartments.models import City

class UserDetailsSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    preferred_city = serializers.SerializerMethodField()

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

    class Meta:
        model = UserDetails
        fields = ('id', 'email', 'first_name', 'last_name', 'gender', 'occupation', 'birth_date', 'phone_number', 'preferred_city', 'about_me', 'photo', 'photo_url')
