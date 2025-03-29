from rest_framework import serializers

from ..models import UserPreferences


class UserPreferencesGetSerializer(serializers.ModelSerializer):
    city = serializers.CharField(source="city.name", read_only=True)  # Return the city name
    preferred_move_in_date = serializers.DateField(source="move_in_date")  # Use move_in_date directly
    # features = serializers.CharField(source="features.name", read_only=True)  # Return the city name
    price_range = serializers.SerializerMethodField()

    class Meta:
        model = UserPreferences
        fields = [
            'city',
            'preferred_move_in_date',
            # 'features',
            'number_of_roommates',
            'price_range',
        ]

    def get_price_range(self, obj):
        return {
            "min": obj.min_price,
            "max": obj.max_price
        }
