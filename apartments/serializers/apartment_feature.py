from rest_framework import serializers

from apartments.models import ApartmentFeature
from apartments.serializers.feature import FeatureSerializer


class ApartmentFeatureSerializer(serializers.ModelSerializer):
    """
    Serializer for the ApartmentFeature model (relationship table).
    """
    feature = FeatureSerializer(read_only=True)  # Include the Feature details

    class Meta:
        model = ApartmentFeature
        fields = ['id', 'apartment', 'feature']
