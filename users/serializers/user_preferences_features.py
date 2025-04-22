from rest_framework import serializers

from users.models.user_preferences_features import UserPreferencesFeatures


class UserPreferencesFeaturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferencesFeatures
        # fields = ('city', 'min_price', 'max_price', 'move_in_date', 'number_of_roommates')
