from rest_framework import serializers

from apartments.models import Feature


class FeatureSerializer(serializers.ModelSerializer):
    """
    Serializer for the Feature model (lookup table).
    """

    class Meta:
        model = Feature
        fields = ['id', 'name']
