from rest_framework import serializers
from apartments.models import Apartment, City, Feature, ApartmentFeature


class ApartmentSerializer(serializers.ModelSerializer):
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())  # City ID validation
    features = serializers.PrimaryKeyRelatedField(
        queryset=Feature.objects.all(), many=True, required=False  # Feature IDs validation
    )
    photos = serializers.ListField(
        child=serializers.ImageField(), required=False  # Ensure at least one valid photo
    )

    class Meta:
        model = Apartment
        fields = [
            'city', 'street', 'type', 'house_number', 'floor', 'number_of_rooms',
            'number_of_available_rooms', 'total_price', 'available_entry_date',
            'about', 'features', 'photos'
        ]

    def validate(self, data):
        """
        Cross-field validation.
        """
        # Ensure available rooms do not exceed total rooms
        if data['number_of_available_rooms'] > data['number_of_rooms']:
            raise serializers.ValidationError(
                {"number_of_available_rooms": "Cannot exceed the total number of rooms."}
            )
        return data

    def create(self, validated_data):
        """
        Override create method to handle features and photos.
        """
        features = validated_data.pop('features', [])  # Extract features from the validated data
        # photos = validated_data.pop('photos', [])  # Extract photos from the validated data

        # Create the apartment instance
        apartment = Apartment.objects.create(**validated_data)

        # Add features to the apartment
        for feature in features:
            ApartmentFeature.objects.create(apartment=apartment, feature=feature)

        # Handle photos

        return apartment


