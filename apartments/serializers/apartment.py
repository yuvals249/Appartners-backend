from rest_framework import serializers
from apartments.models import City, ApartmentFeature, Feature, ApartmentPhoto
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
    photos = serializers.ListField(
        child=serializers.ImageField(), required=True, min_length=1  # Ensure at least one valid photo
    )
    photo_urls = serializers.SerializerMethodField()

    class Meta:
        model = Apartment
        fields = [
            'id', 'city', 'street', 'type', 'house_number', 'floor', 'number_of_rooms',
            'number_of_available_rooms', 'total_price', 'available_entry_date',
            'about', 'features', 'feature_details', 'user_id', 'created_at', 'photos', 'photo_urls',
            'latitude', 'longitude', 'area'
        ]

    def get_feature_details(self, obj):
        """
        Get features through the intermediate model
        """
        features = [af.feature for af in obj.apartment_features.all()]
        return FeatureSerializer(features, many=True).data

    def get_photo_urls(self, obj):
        """
        Get the URLs of the apartment photos
        """
        return [photo.photo.url for photo in obj.photos.all()]

    def create(self, validated_data):
        features = validated_data.pop('features', [])
        user = validated_data.pop('user_id', None)
        photos = validated_data.pop('photos', [])
        
        # Create the apartment
        apartment = Apartment.objects.create(user=user, **validated_data)

        # Create ApartmentFeature instances for each feature
        for feature in features:
            ApartmentFeature.objects.create(
                apartment=apartment,
                feature=feature
            )
            
        # Create ApartmentPhoto instances for each photo
        for photo in photos:
            ApartmentPhoto.objects.create(
                apartment=apartment,
                photo=photo
            )

        return apartment
