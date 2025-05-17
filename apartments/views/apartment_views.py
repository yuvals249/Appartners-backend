"""
Core apartment-related views for the apartments app.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from apartments.serializers.apartment import ApartmentSerializer
from apartments.models.photo import ApartmentPhoto
from apartments.utils.location import add_random_offset, get_area_from_coordinates, truncate_coordinates
from apartments.models import Feature, City
from apartments.serializers.feature import FeatureSerializer
from apartments.serializers.city import CitySerializer

class ApartmentCreateView(APIView):
    """API View to create a new apartment."""
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        if request.token_error:
            return request.token_error
            
        user_id = request.user_from_token
        
        photos = request.FILES.getlist('photos')
        if not photos:
            return Response({"error": "At least one photo is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Prepare request data
        request_data = self._prepare_request_data(request, user_id)
        
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
    Get dropdown data for apartment creation form.
    Returns active features and cities for use in the apartment creation UI.
    """
    
    def get(self, request):
        """
        Retrieve active features and cities for apartment creation.
        """
        try:
            # Direct implementation that works
            # Get active data
            features = Feature.objects.filter(active=True)
            cities = City.objects.filter(active=True)
            
            # Serialize the data
            feature_data = FeatureSerializer(features, many=True).data
            city_data = CitySerializer(cities, many=True).data
            
            # Return the response
            return Response({
                'features': feature_data,
                'cities': city_data
            })
        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve apartment form data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
