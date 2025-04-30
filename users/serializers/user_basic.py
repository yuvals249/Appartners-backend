from rest_framework import serializers
from django.contrib.auth.models import User
from users.models.user_details import UserDetails

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

    class Meta:
        model = UserDetails
        fields = ['id', 'user_id', 'email', 'first_name', 'last_name', 'phone_number']
        
    def get_user_id(self, obj):
        """
        Retrieves the associated User's ID.
        
        Args:
            obj: UserDetails instance
            
        Returns:
            int: User's ID
        """
        return obj.user.id
        
    def get_email(self, obj):
        """
        Retrieves the associated User's email.
        
        Args:
            obj: UserDetails instance
            
        Returns:
            str: User's email
        """
        return obj.user.email
