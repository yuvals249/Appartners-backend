from rest_framework import serializers
from users.models.user_details import UserDetails

class UserBasicSerializer(serializers.ModelSerializer):
    """
    Serializer for basic user details information to be returned in API responses.
    """
    user_id = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    
    class Meta:
        model = UserDetails
        fields = ['id', 'user_id', 'email', 'first_name', 'last_name', 'phone_number']
        
    def get_user_id(self, obj):
        return obj.user.id
        
    def get_email(self, obj):
        return obj.user.email
