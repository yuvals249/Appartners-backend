from rest_framework import serializers

from ..models import UserPreferences
from apartments.models import Feature, Apartment


class UserPreferencesGetSerializer(serializers.ModelSerializer):
    city = serializers.SerializerMethodField()  # Return city ID and name
    features = serializers.SerializerMethodField()  # Get features using a method
    price_range = serializers.SerializerMethodField()

    class Meta:
        model = UserPreferences
        fields = [
            'city',
            'move_in_date',
            'features',
            'number_of_roommates',
            'price_range',
            'max_floor',
            'area',
        ]

    def get_price_range(self, obj):
        return {
            "min": obj.min_price,
            "max": obj.max_price
        }
    
    def get_city(self, obj):
        if obj.city:
            return {
                "id": obj.city.id,
                "name": obj.city.name
            }
        return None
    
    def get_features(self, obj):
        # Get all features associated with this user preference
        feature_ids = obj.user_preference_features.values_list('feature_id', flat=True)
        features = Feature.objects.filter(id__in=feature_ids)
        return [{"id": feature.id, "name": feature.name} for feature in features]
