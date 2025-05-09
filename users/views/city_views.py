"""
City-related views for the users app.
"""
from django.db import DatabaseError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apartments.models.city import City
from apartments.models.apartment import Apartment
from apartments.serializers.city import CitySerializer


class CityPayloadView(APIView):
    authentication_classes = []  # No authentication required
    permission_classes = []  # No permissions required
    """
    Returns a payload with a list of all active cities and their areas.
    """
    def get(self, request):
        try:
            # Get all active cities from the City model
            cities = City.objects.filter(active=True)
            
            # Use the CitySerializer to serialize the cities
            serializer = CitySerializer(cities, many=True)
            
            return Response({
                "cities": serializer.data
            }, status=status.HTTP_200_OK)
        except DatabaseError:
            return Response(
                {"error": "A database error occurred. Please try again later"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
