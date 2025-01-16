from rest_framework import serializers
from apartments.models import Feature, City
from apartments.serializers import FeatureSerializer, CitySerializer


class ApartmentPostPayloadSerializer(serializers.Serializer):
    features = serializers.SerializerMethodField()
    cities = serializers.SerializerMethodField()

    def get_features(self, obj):
        """
        Serialize active features
        """
        features = Feature.objects.filter(active=True)
        return FeatureSerializer(features, many=True).data

    def get_cities(self, obj):
        """
        Serialize active cities
        """
        cities = City.objects.filter(active=True)
        return CitySerializer(cities, many=True).data
