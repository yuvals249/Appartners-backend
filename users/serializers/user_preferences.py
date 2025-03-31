from rest_framework import serializers

from ..models import UserPreferences
from apartments.models import Feature


class UserPreferencesGetSerializer(serializers.ModelSerializer):
    city = serializers.CharField(source="city.name", read_only=True)  # Return the city name
    preferred_move_in_date = serializers.DateField(source="move_in_date")  # Use move_in_date directly
    features = serializers.SerializerMethodField()  # Get features using a method
    price_range = serializers.SerializerMethodField()

    class Meta:
        model = UserPreferences
        fields = [
            'city',
            'preferred_move_in_date',
            'features',
            'number_of_roommates',
            'price_range',
        ]

    def get_price_range(self, obj):
        return {
            "min": obj.min_price,
            "max": obj.max_price
        }
    
    def get_features(self, obj):
        # Get all features associated with this user preference
        feature_ids = obj.user_preference_features.values_list('feature_id', flat=True)
        features = Feature.objects.filter(id__in=feature_ids)
        return [feature.name for feature in features]
