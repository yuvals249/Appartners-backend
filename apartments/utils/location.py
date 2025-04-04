"""
Location-related utility functions for apartments.
"""
import random
import requests
import logging

logger = logging.getLogger(__name__)


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
        logger.error(f"Error fetching location data: {str(e)}")
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
