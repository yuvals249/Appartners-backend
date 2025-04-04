"""
Core apartment-related views for the apartments app.
"""
from django.core.exceptions import ValidationError
from django.db import DatabaseError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from apartments.serializers import ApartmentPostPayloadSerializer
from apartments.serializers.apartment import ApartmentSerializer
from apartments.models import Apartment, City
from apartments.models.photo import ApartmentPhoto
from appartners.utils import get_user_from_token
from apartments.utils.location import add_random_offset, get_area_from_coordinates, truncate_coordinates


class ApartmentCreateView(APIView):
    """API View to create a new apartment."""
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        # Extract user and validate photos
        success, result = get_user_from_token(request)
        if not success:
            return result
        
        photos = request.FILES.getlist('photos')
        if not photos:
            return Response({"error": "At least one photo is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Prepare request data
        request_data = self._prepare_request_data(request, result)
        
        # Validate data
        serializer = ApartmentSerializer(data=request_data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Process location and save apartment
        try:
            # Process location data
            request_data = self._process_location_data(request_data)
            
            # Update serializer with processed location data
            serializer = ApartmentSerializer(data=request_data, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Save apartment
            apartment = serializer.save()
            
            # Handle photos
            for photo in photos:
                ApartmentPhoto.objects.create(apartment=apartment, photo=photo)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _prepare_request_data(self, request, user_id):
        """Prepare request data with user_id and features."""
        request_data = {k: v for k, v in request.data.items() if k != 'photos'}
        request_data['user_id'] = user_id
        
        features_list = request.data.getlist('features')
        if features_list:
            request_data['features'] = features_list
            
        return request_data
    
    def _process_location_data(self, request_data):
        lat, lon = request_data['latitude'], request_data['longitude']

        # Get area from coordinates
        area = get_area_from_coordinates(lat, lon)
        if area:
            request_data['area'] = area
        
        # Add random offset and truncate
        offset_lat, offset_lon = add_random_offset(lat, lon)
        truncated_lat, truncated_lon = truncate_coordinates(offset_lat, offset_lon)
        
        # Update request data with processed coordinates
        request_data['latitude'] = truncated_lat
        request_data['longitude'] = truncated_lon
        
        return request_data


class ApartmentPostPayloadView(APIView):
    """
    Get dropdown data for apartment post.
    """
    
    def get(self, request, *args, **kwargs):
        serializer = ApartmentPostPayloadSerializer()
        return Response(serializer.data)
