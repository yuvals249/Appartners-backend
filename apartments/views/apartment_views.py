"""
Core apartment-related views for the apartments app.
"""
from django.core.exceptions import ValidationError
from django.db import DatabaseError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apartments.serializers import ApartmentPostPayloadSerializer
from apartments.serializers.apartment import ApartmentSerializer
from apartments.models import Apartment, City
from appartners.utils import get_user_from_token
from apartments.utils.location import get_location_data, add_random_offset


class ApartmentCreateView(APIView):
    """
    API View to create a new apartment.
    """

    def post(self, request, *args, **kwargs):
        # Extract user from token using centralized function
        success, result = get_user_from_token(request)
        if not success:
            return result  # Return the error response
            
        user_id = result
        
        # Add user to request data
        request_data = request.data.copy()
        request_data['user_id'] = user_id
        
        # Handle photos
        photos = request.FILES.getlist('photos')
        if not photos:
            return Response(
                {"error": "At least one photo is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        request_data.setlist('photos', photos)
        
        # Validate the data first
        serializer = ApartmentSerializer(data=request_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        # Get location data from OpenStreetMap
        try:
            street = request_data.get('street')
            house_number = request_data.get('house_number')
            city_id = request_data.get('city')
            
            # Get city name
            city_name = City.objects.get(id=city_id).name if city_id else None
            
            if street and house_number and city_name:
                lat, lon, area = get_location_data(street, house_number, city_name)
                
                if lat and lon:
                    # Add random offset to coordinates
                    offset_lat, offset_lon = add_random_offset(lat, lon)
                    
                    # Add to request data
                    request_data['latitude'] = offset_lat
                    request_data['longitude'] = offset_lon
                    request_data['area'] = area
                    
                    # Update serializer with new data
                    serializer = ApartmentSerializer(data=request_data)
                    if not serializer.is_valid():
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log the error but continue with apartment creation
            print(f"Error processing location data: {str(e)}")
        
        # Save the apartment
        try:
            apartment = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            # Handle model-level validation errors
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except DatabaseError:
            return Response(
                {"error": "A database error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            # Handle other exceptions
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ApartmentPostPayloadView(APIView):
    """
    Get dropdown data for apartment post.
    """
    
    def get(self, request, *args, **kwargs):
        serializer = ApartmentPostPayloadSerializer()
        return Response(serializer.data)
