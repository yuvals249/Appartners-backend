from rest_framework import serializers

from users.models.user_details import UserDetails


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = ('first_name', 'last_name', 'gender', 'occupation', 'birth_date', 'phone_number', 'preferred_city', 'about_me', 'photo')
