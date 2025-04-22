from rest_framework import serializers
from .models import User

class UserBasicSerializer(serializers.ModelSerializer):
    """
    Serializer for basic user information to be returned in API responses.
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone_number']
