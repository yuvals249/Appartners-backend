from rest_framework import serializers

from ..models import UserPreferences
from apartments.models import Feature, Apartment


class UserPreferencesGetSerializer(serializers.ModelSerializer):
    city = serializers.CharField(source="city.name", read_only=True)  # Return the city name
    preferred_move_in_date = serializers.DateField(source="move_in_date")  # Use move_in_date directly
    features = serializers.SerializerMethodField()  # Get features using a method
    price_range = serializers.SerializerMethodField()
    available_areas = serializers.SerializerMethodField()  # Get available areas for the selected city

    class Meta:
        model = UserPreferences
        fields = [
            'city',
            'preferred_move_in_date',
            'features',
            'number_of_roommates',
            'price_range',
            'max_floor',
            'area',
            'available_areas',
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
    
    def get_available_areas(self, obj):
        """
        Get all available areas/neighborhoods for the selected city
        """
        if obj.city:
            # Get distinct areas from apartments in the same city
            areas = Apartment.objects.filter(
                city=obj.city, 
                area__isnull=False
            ).exclude(
                area=''
            ).values_list('area', flat=True).distinct().order_by('area')
            
            return list(areas)
        return []
