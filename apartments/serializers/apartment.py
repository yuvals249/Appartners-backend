from rest_framework import serializers
from apartments.models import City, ApartmentFeature, Feature
from apartments.serializers import FeatureSerializer
from apartments.models.apartment import Apartment
from django.contrib.auth.models import User


class ApartmentSerializer(serializers.ModelSerializer):
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())  # City ID validation
    features = serializers.PrimaryKeyRelatedField(
        queryset=Feature.objects.all(), many=True, write_only=True, required=False  # For input
    )
    feature_details = serializers.SerializerMethodField()
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, required=False)
    # photos = serializers.ListField(
    #     child=serializers.ImageField(), required=False  # Ensure at least one valid photo
    # )

    class Meta:
        model = Apartment
        fields = [
            'id', 'city', 'street', 'type', 'house_number', 'floor', 'number_of_rooms',
            'number_of_available_rooms', 'total_price', 'available_entry_date',
            'about', 'features', 'feature_details', 'user_id', 'created_at'
        ]

    def get_feature_details(self, obj):
        """
        Get features through the intermediate model
        """
        features = [af.feature for af in obj.apartment_features.all()]
        return FeatureSerializer(features, many=True).data


    def create(self, validated_data):
        features = validated_data.pop('features', [])
        user = validated_data.pop('user_id', None)
        
        # Create the apartment
        apartment = Apartment.objects.create(user=user, **validated_data)

        # Create ApartmentFeature instances for each feature
        for feature in features:
            ApartmentFeature.objects.create(
                apartment=apartment,
                feature=feature
            )

        return apartment
