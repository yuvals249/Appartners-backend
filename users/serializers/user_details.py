from rest_framework import serializers

from users.models.user_details import UserDetails


class UserDetailsSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()
    
    def get_email(self, obj):
        return obj.user.email
        
    def get_photo_url(self, obj):
        if obj.photo:
            return obj.photo.url
        return None
        
    class Meta:
        model = UserDetails
        fields = ('email', 'first_name', 'last_name', 'gender', 'occupation', 'birth_date', 'phone_number', 'preferred_city', 'about_me', 'photo', 'photo_url')
