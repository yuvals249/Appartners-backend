from rest_framework import serializers

from apartments.models import City


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'created_at', 'updated_at', 'name', 'hebrew_name']
