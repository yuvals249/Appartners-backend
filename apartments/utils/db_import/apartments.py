import random
from datetime import datetime
from .utils import generate_uuid

def prepare_apartments(apartments_data, users):
    """
    Prepare apartments for database import
    
    Args:
        apartments_data: List of processed apartment data
        users: List of user objects
        
    Returns:
        list: Prepared apartment objects
    """
    db_apartments = []
    
    # Get current timestamp
    now = datetime.now().isoformat()
    
    # Assign users to apartments
    for i, apt_data in enumerate(apartments_data):
        # Generate a UUID for the apartment
        apt_id = generate_uuid()
        
        # Assign a random user as the owner
        user_index = i % len(users)  # Distribute apartments among users
        user_id = users[user_index]["id"]
        
        # Create the apartment object
        apartment = {
            "id": apt_id,
            "city": "Beer Sheva",  # Use city name instead of ID
            "user_id": user_id,
            "street": apt_data["street"],
            "type": apt_data["type"],
            "floor": apt_data["floor"],
            "number_of_rooms": apt_data["number_of_rooms"],
            "number_of_available_rooms": apt_data["number_of_available_rooms"],
            "total_price": apt_data["total_price"],
            "available_entry_date": apt_data["available_entry_date"],
            "about": apt_data["about"],
            "latitude": str(apt_data["latitude"]),
            "longitude": str(apt_data["longitude"]),
            "area": apt_data["area"],
            "created_at": now,
            "updated_at": now,
            "is_yad2": True,
            "photo_urls": apt_data["photos"]
        }
        
        db_apartments.append(apartment)
    
    return db_apartments

def get_feature_data():
    """
    Get feature data with probabilities
    
    Returns:
        list: Feature data with probabilities
    """
    return [
        {"name": "Laundry Machine", "probability": 0.95},
        {"name": "Furnished", "probability": 0.92},
        {"name": "Pet-friendly", "probability": 0.90},
        {"name": "Parking", "probability": 0.88},
        {"name": "Elevator", "probability": 0.87},
        {"name": "Air Conditioning", "probability": 0.85},
        {"name": "Semi-furnished", "probability": 0.83},
        {"name": "Balcony", "probability": 0.82},
        {"name": "Private Bathroom", "probability": 0.80},
        {"name": "Master Bedroom", "probability": 0.78},
        {"name": "Close To University", "probability": 0.76},
        {"name": "New", "probability": 0.75},
        {"name": "Renovated", "probability": 0.73},
        {"name": "Family-friendly", "probability": 0.71},
        {"name": "Gym", "probability": 0.70},
        {"name": "Storage Room", "probability": 0.68},
        {"name": "Storage", "probability": 0.66},
        {"name": "Garden", "probability": 0.65},
        {"name": "Window Bars", "probability": 0.60},
        {"name": "Study Room", "probability": 0.58},
        {"name": "Unfurnished", "probability": 0.55},
        {"name": "Roommates", "probability": 0.52},
        {"name": "Well-maintained", "probability": 0.50},
        {"name": "Safe Room", "probability": 0.45},
        {"name": "Trash Chute", "probability": 0.40},
        {"name": "Shared Bathroom", "probability": 0.30},
        {"name": "Wheelchair Accessible", "probability": 0.25}
    ]

def assign_features_to_apartments(apartments):
    """
    Assign features to apartments based on probabilities
    
    Args:
        apartments: List of apartment objects
        
    Returns:
        list: Apartment feature associations
    """
    apartment_features = []
    feature_data = get_feature_data()
    now = datetime.now().isoformat()
    
    for apt in apartments:
        # Decide how many features to assign to this apartment (2-6)
        num_features = random.randint(2, 6)
        
        # Select features based on their probability
        selected_features = []
        for feature in feature_data:
            # Check if we should add this feature based on its probability
            if random.random() < feature["probability"] and len(selected_features) < num_features:
                selected_features.append(feature)
        
        # If we didn't get enough features, randomly select more
        if len(selected_features) < num_features:
            remaining_features = [f for f in feature_data if f not in selected_features]
            additional_features = random.sample(remaining_features, min(num_features - len(selected_features), len(remaining_features)))
            selected_features.extend(additional_features)
        
        # Create apartment_feature entries
        for feature in selected_features:
            apartment_feature = {
                "id": generate_uuid(),
                "apartment_id": apt["id"],
                "feature": feature["name"],  # Use feature name instead of ID
                "created_at": now,
                "updated_at": now
            }
            
            apartment_features.append(apartment_feature)
    
    return apartment_features
