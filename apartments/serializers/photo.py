from rest_framework import serializers

from apartments.models import ApartmentPhoto


class ApartmentPhotoSerializer(serializers.ModelSerializer):
    """
    Serializer for the ApartmentPhoto model.
    """

    class Meta:
        model = ApartmentPhoto
        fields = ['id', 'apartment', 'photo']
