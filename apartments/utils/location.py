"""
Location-related utility functions for apartments.
"""
import random
import requests
import logging

logger = logging.getLogger(__name__)

def get_area_from_coordinates(lat, lon):
    """
    Get area information from coordinates using reverse geocoding.
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        str: Area name or empty string if not found
    """
    try:

        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        headers = {
            "User-Agent": "appartners/1.0 (tomsh610@gmail.com)"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200 and response.json():
            data = response.json()
            address = data.get("address", {})
            area = address.get("suburb") or address.get("residential") or address.get("neighbourhood") or ""
            return area

        return ""

    except Exception as e:
        logger.error(f"Error fetching area from coordinates: {str(e)}")
        return ""


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
    
    return float(lat) + lat_offset, float(lon) + lon_offset


def truncate_coordinates(lat, lon):
    """
    Truncate coordinates to fit within model constraints (max_digits=10, decimal_places=7).
    
    Args:
        lat: Latitude as float
        lon: Longitude as float
        
    Returns:
        tuple: (truncated_lat, truncated_lon)
    """
    # Format to 7 decimal places
    truncated_lat = float(f"{lat:.7f}")
    truncated_lon = float(f"{lon:.7f}")
    
    return truncated_lat, truncated_lon
