from rest_framework import serializers
from .models import Apartment, ApartmentPhoto, Feature, ApartmentFeature


class FeatureSerializer(serializers.ModelSerializer):
    """
    Serializer for the Feature model (lookup table).
    """
    class Meta:
        model = Feature
        fields = ['id', 'name', 'active']


class ApartmentPhotoSerializer(serializers.ModelSerializer):
    """
    Serializer for the ApartmentPhoto model.
    """
    class Meta:
        model = ApartmentPhoto
        fields = ['id', 'apartment', 'photo']


class ApartmentFeatureSerializer(serializers.ModelSerializer):
    """
    Serializer for the ApartmentFeature model (relationship table).
    """
    feature = FeatureSerializer(read_only=True)  # Include the Feature details

    class Meta:
        model = ApartmentFeature
        fields = ['id', 'apartment', 'feature']


class ApartmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Apartment model with nested relationships.
    """
    photos = ApartmentPhotoSerializer(many=True, read_only=True)  # Nested photos
    apartment_features = ApartmentFeatureSerializer(many=True, read_only=True)  # Nested features relationship

    class Meta:
        model = Apartment
        fields = [
            'id', 'city', 'street', 'type', 'house_number', 'floor',
            'number_of_rooms', 'number_of_available_rooms', 'total_price',
            'available_entry_date', 'about', 'photos', 'apartment_features'
        ]
