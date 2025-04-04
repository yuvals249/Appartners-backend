"""
Core apartment-related views for the apartments app.
"""
import random
import requests
from django.core.exceptions import ValidationError
from django.db import DatabaseError

from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apartments.serializers import ApartmentPostPayloadSerializer
from apartments.serializers.apartment import ApartmentSerializer
from apartments.models import Apartment
from appartners.utils import get_user_from_token
from appartners.validators import UUIDValidator


def get_location_data(street, house_number, city_name):
    """
    Get location data from OpenStreetMap Nominatim API.
    
    Args:
        street: Street name
        house_number: House number
        city_name: City name
        
    Returns:
        tuple: (latitude, longitude, area) or (None, None, None) if not found
    """
    try:
        # Construct the search query
        query = f"{street} {house_number}, {city_name}"
        
        # Make the request to Nominatim
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": query,
                "format": "json",
                "limit": 1,
                "addressdetails": 1
            },
            headers={"User-Agent": "AppartnerApp/1.0"}
        )
        
        # Check if we got a valid response
        if response.status_code == 200 and response.json():
            data = response.json()[0]
            lat = float(data.get("lat"))
            lon = float(data.get("lon"))
            
            # Get area from address details
            address = data.get("address", {})
            area = address.get("suburb") or address.get("residential") or address.get("neighbourhood") or ""
            
            return lat, lon, area
            
        return None, None, None
        
    except Exception as e:
        print(f"Error fetching location data: {str(e)}")
        return None, None, None


def add_random_offset(lat, lon):
    """
    Add a small random offset to coordinates for privacy.
    
    Args:
        lat: Original latitude
        lon: Original longitude
        
    Returns:
        tuple: (offset_lat, offset_lon)
    """
    # Add random offset between -0.0005 and 0.0005 (approximately 50 meters)
    lat_offset = random.uniform(-0.0005, 0.0005)
    lon_offset = random.uniform(-0.0005, 0.0005)
    
    return lat + lat_offset, lon + lon_offset


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
            from apartments.models import City
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
        try:
            # Fetch payload using the serializer
            payload = ApartmentPostPayloadSerializer({}).data
            return Response(payload)
        except DatabaseError:
            # Handle database errors
            return Response(
                {"error": "An error occurred while fetching dropdown data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except APIException as e:
            # Handle serialization-related errors
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ApartmentView(APIView):
    """
    Retrieve or delete an apartment by ID.
    """

    def get(self, request, apartment_id):
        try:
            validator = UUIDValidator()
            if not validator(apartment_id):
                return Response(
                    {"error": "Invalid UUID format"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            apartment = Apartment.objects.get(id=apartment_id)
        except Apartment.DoesNotExist:
            return Response(
                {"error": "Apartment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ApartmentSerializer(apartment)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def delete(self, request, apartment_id):
        # Extract user from token using centralized function
        success, result = get_user_from_token(request)
        if not success:
            return result  # Return the error response
            
        user_id = result
        
        try:
            validator = UUIDValidator()
            if not validator(apartment_id):
                return Response(
                    {"error": "Invalid UUID format"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Get the apartment
            apartment = Apartment.objects.get(id=apartment_id)
            
            # Check if the user is the owner of the apartment
            if apartment.user_id != user_id:
                return Response(
                    {"error": "You don't have permission to delete this apartment"},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            # Delete the apartment (this will cascade to related entities)
            apartment.delete()
            
            return Response(
                {"message": "Apartment and all related data deleted successfully"},
                status=status.HTTP_200_OK
            )
            
        except Apartment.DoesNotExist:
            return Response(
                {"error": "Apartment not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except DatabaseError:
            return Response(
                {"error": "An error occurred while deleting the apartment"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
