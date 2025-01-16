from rest_framework import serializers

from users.models.user_preferences import UserPreferences


class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        fields = ('city', 'min_price', 'max_price', 'move_in_date', 'number_of_roommates')
