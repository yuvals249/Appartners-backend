#!/usr/bin/env python
"""
Script to prepare fixture files for the Yad2 data migration.
This script will:
1. Process the prepared Yad2 data
2. Convert it to Django fixture format
3. Save the fixtures in the apartments/fixtures directory
"""

import os
import sys
import json
import django
import uuid
from datetime import datetime
from pathlib import Path
from django.contrib.auth.hashers import make_password

# Set up Django environment
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appartners.settings')
django.setup()

# Import Django models
from django.contrib.auth.models import User
from django.db import transaction
from apartments.models import Apartment, Feature, ApartmentFeature, City, ApartmentPhoto
from users.models import UserDetails, UserResponse

# Import data processing functions
from apartments.utils.db_import.main import prepare_data_for_db_import


# Custom JSON encoder to handle UUIDs
class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            # Return the UUID as a string
            return str(obj)
        return super().default(obj)


def prepare_fixtures(processed_file_path, user_count=300):
    """
    Prepare fixture files for the Yad2 data migration
    
    Args:
        processed_file_path: Path to the processed apartments JSON file
        user_count: Number of users to generate
    """
    print(f"Preparing fixture files from {processed_file_path}")
    
    # Check if the processed file exists
    if not os.path.exists(processed_file_path):
        print(f"Error: Processed file {processed_file_path} does not exist!")
        return
    
    try:
        # Step 1: Prepare data for database import
        print(f"Preparing data with {user_count} users...")
        prepare_data_for_db_import(processed_file_path, user_count)
        
        # Step 2: Convert prepared data to Django fixture format
        print("Converting data to Django fixture format...")
        convert_to_fixtures()
        
        print("Fixture preparation completed successfully!")
    except Exception as e:
        print(f"Error during fixture preparation: {e}")
        import traceback
        traceback.print_exc()


def get_hashed_password():
    """
    Get hashed password from environment variable or use default
    
    Returns:
        str: Hashed password
    """
    # Get password from environment variable or use default
    password = os.environ.get('YAD2_USER_PASSWORD', '111111')
    
    # Hash the password using Django's make_password function
    return make_password(password)


def convert_to_fixtures():
    """
    Convert prepared data to Django fixture format
    """
    # Get paths to the prepared data files
    data_dir = os.path.join(BASE_DIR, 'data', 'db_import')
    
    users_file = os.path.join(data_dir, 'users.json')
    user_details_file = os.path.join(data_dir, 'user_details.json')
    user_responses_file = os.path.join(data_dir, 'user_responses.json')
    apartments_file = os.path.join(data_dir, 'apartments.json')
    apartment_features_file = os.path.join(data_dir, 'apartment_features.json')
    
    # Check if all files exist
    for file_path in [users_file, user_details_file, user_responses_file, 
                     apartments_file, apartment_features_file]:
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} does not exist!")
            return
    
    # Load data from files
    with open(users_file, 'r', encoding='utf-8') as f:
        users_data = json.load(f)
    
    with open(user_details_file, 'r', encoding='utf-8') as f:
        user_details_data = json.load(f)
    
    with open(user_responses_file, 'r', encoding='utf-8') as f:
        user_responses_data = json.load(f)
    
    with open(apartments_file, 'r', encoding='utf-8') as f:
        apartments_data = json.load(f)
    
    with open(apartment_features_file, 'r', encoding='utf-8') as f:
        apartment_features_data = json.load(f)
    
    # Create fixture directory
    fixture_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                              'fixtures')
    os.makedirs(fixture_dir, exist_ok=True)
    
    # Get hashed password
    hashed_password = get_hashed_password()
    
    # Create a mapping from UUID to integer ID for users
    uuid_to_int_map = {}
    for i, user_data in enumerate(users_data, start=1000):  # Start from 1000 to avoid conflicts
        # Convert UUID to string if it's a UUID object
        user_id = user_data["id"]
        if isinstance(user_id, uuid.UUID):
            user_id = str(user_id)
        uuid_to_int_map[user_id] = i
    
    # Create a mapping for UserDetails IDs
    userdetails_uuid_to_int_map = {}
    for i, detail_data in enumerate(user_details_data, start=1000):  # Start from 1000 to avoid conflicts
        # Convert UUID to string if it's a UUID object
        detail_id = detail_data["id"]
        if isinstance(detail_id, uuid.UUID):
            detail_id = str(detail_id)
        userdetails_uuid_to_int_map[detail_id] = i
    
    # Convert users to fixture format
    users_fixture = []
    for user_data in users_data:
        first_name = user_data["name"].split()[0]
        last_name = " ".join(user_data["name"].split()[1:]) if len(user_data["name"].split()) > 1 else ""
        
        # Convert UUID to string if it's a UUID object
        user_id = user_data["id"]
        if isinstance(user_id, uuid.UUID):
            user_id = str(user_id)
        
        users_fixture.append({
            "model": "auth.user",
            "pk": uuid_to_int_map[user_id],  # Use integer ID
            "fields": {
                "password": hashed_password,
                "last_login": user_data["created_at"],
                "is_superuser": False,
                "username": user_data["email"],
                "first_name": first_name,
                "last_name": last_name,
                "email": user_data["email"],
                "is_staff": False,
                "is_active": True,
                "date_joined": user_data["created_at"],
                "groups": [],
                "user_permissions": []
            }
        })
    
    # Convert user details to fixture format
    user_details_fixture = []
    for detail_data in user_details_data:
        # Convert UUID to string if it's a UUID object
        user_id = detail_data["user_id"]
        if isinstance(user_id, uuid.UUID):
            user_id = str(user_id)
        
        # Convert UUID to string if it's a UUID object
        detail_id = detail_data["id"]
        if isinstance(detail_id, uuid.UUID):
            detail_id = str(detail_id)
        
        user_details_fixture.append({
            "model": "users.userdetails",
            "pk": userdetails_uuid_to_int_map[detail_id],  # Use integer ID
            "fields": {
                "user_id": uuid_to_int_map[user_id],  # Use integer ID
                "first_name": next((u["fields"]["first_name"] for u in users_fixture if u["pk"] == uuid_to_int_map[user_id]), ""),
                "last_name": next((u["fields"]["last_name"] for u in users_fixture if u["pk"] == uuid_to_int_map[user_id]), ""),
                "gender": "Male",
                "occupation": "Student",
                "birth_date": "1990-01-01",
                "preferred_city": "Beer Sheva",
                "phone_number": detail_data["phone"],
                "about_me": "Yad2 imported user",
                "is_yad2": True,
                "created_at": detail_data["created_at"],
                "updated_at": detail_data["updated_at"]
            }
        })
    
    # Create a mapping for UserResponse IDs
    userresponse_uuid_to_int_map = {}
    for i, response_data in enumerate(user_responses_data, start=1000):  # Start from 1000 to avoid conflicts
        # Convert UUID to string if it's a UUID object
        response_id = response_data["id"]
        if isinstance(response_id, uuid.UUID):
            response_id = str(response_id)
        userresponse_uuid_to_int_map[response_id] = i
    
    # Convert user responses to fixture format
    user_responses_fixture = []
    for response_data in user_responses_data:
        # Convert UUID to string if it's a UUID object
        user_id = response_data["user_id"]
        if isinstance(user_id, uuid.UUID):
            user_id = str(user_id)
        
        # Convert UUID to string if it's a UUID object
        response_id = response_data["id"]
        if isinstance(response_id, uuid.UUID):
            response_id = str(response_id)
        
        user_responses_fixture.append({
            "model": "users.userresponse",
            "pk": userresponse_uuid_to_int_map[response_id],  # Use integer ID
            "fields": {
                "user_id": uuid_to_int_map[user_id],  # Use integer ID
                "question_id": response_data["question_id"],
                "numeric_response": response_data["response"],
                "text_response": None,
                "created_at": response_data["created_at"],
                "updated_at": response_data["updated_at"]
            }
        })
    
    # Get city ID for Beer Sheva
    beer_sheva_id = None
    try:
        # Try to get the city from the database
        beer_sheva = City.objects.filter(name__icontains="Beer Sheva").first()
        if beer_sheva:
            beer_sheva_id = beer_sheva.id
        else:
            # If Beer Sheva doesn't exist, try to get any city
            any_city = City.objects.first()
            if any_city:
                beer_sheva_id = any_city.id
            else:
                # If no cities exist, create a fixture for Beer Sheva
                beer_sheva_id = str(uuid.uuid4())
                city_fixture = [{
                    "model": "apartments.city",
                    "pk": beer_sheva_id,
                    "fields": {
                        "name": "Beer Sheva",
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    }
                }]
                # Save city fixture
                with open(os.path.join(fixture_dir, 'yad2_cities.json'), 'w', encoding='utf-8') as f:
                    json.dump(city_fixture, f, cls=UUIDEncoder, ensure_ascii=False, indent=2)
                print(f"Created city fixture for Beer Sheva with ID: {beer_sheva_id}")
    except Exception as e:
        print(f"Error getting city ID: {e}")
        # Create a default city ID
        beer_sheva_id = str(uuid.uuid4())
        city_fixture = [{
            "model": "apartments.city",
            "pk": beer_sheva_id,
            "fields": {
                "name": "Beer Sheva",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        }]
        # Save city fixture
        with open(os.path.join(fixture_dir, 'yad2_cities.json'), 'w', encoding='utf-8') as f:
            json.dump(city_fixture, f, cls=UUIDEncoder, ensure_ascii=False, indent=2)
        print(f"Created city fixture for Beer Sheva with ID: {beer_sheva_id}")
    
    # Convert apartments to fixture format
    apartments_fixture = []
    apartment_photos_fixture = []
    
    for apt_data in apartments_data:
        # Convert UUID to string if it's a UUID object
        user_id = apt_data["user_id"]
        if isinstance(user_id, uuid.UUID):
            user_id = str(user_id)
        
        # Ensure total_price is within the model's constraints (max_digits=6, decimal_places=2)
        # This means the maximum value is 9999.99
        total_price = apt_data["total_price"]
        if total_price > 9999.99:
            total_price = 9999.99
        
        # Get apartment ID
        apartment_id = apt_data["id"]
        if isinstance(apartment_id, uuid.UUID):
            apartment_id = str(apartment_id)
        
        apartments_fixture.append({
            "model": "apartments.apartment",
            "pk": apartment_id,  # Keep the original UUID for apartments
            "fields": {
                "user_id": uuid_to_int_map[user_id],  # Use integer ID for user
                "city_id": beer_sheva_id,  # Use the Beer Sheva city ID
                "street": apt_data["street"],
                "type": apt_data["type"],
                "floor": apt_data["floor"],
                "number_of_rooms": apt_data["number_of_rooms"],
                "number_of_available_rooms": apt_data["number_of_available_rooms"],
                "total_price": total_price,
                "available_entry_date": apt_data["available_entry_date"],
                "about": apt_data["about"],
                "latitude": apt_data["latitude"],
                "longitude": apt_data["longitude"],
                "area": apt_data["area"],
                "is_yad2": True,
                "created_at": apt_data["created_at"],
                "updated_at": apt_data["updated_at"]
            }
        })
    
    # Get existing features
    existing_features = {}
    try:
        # Get all features from the database
        for feature in Feature.objects.all():
            existing_features[feature.name] = feature.id
    except:
        # If we can't access the database, use some common features
        common_features = ["Laundry Machine", "Elevator", "Parking", "Air Conditioner", "Balcony"]
        for i, name in enumerate(common_features, start=1):
            existing_features[name] = i
    
    # Convert apartment features to fixture format
    apartment_features_fixture = []
    for i, feature_data in enumerate(apartment_features_data, start=1000):  # Start from 1000 to avoid conflicts
        feature_name = feature_data.get("feature", "")
        if not feature_name:
            continue
        
        # Convert UUID to string if it's a UUID object
        apartment_id = feature_data["apartment_id"]
        if isinstance(apartment_id, uuid.UUID):
            apartment_id = str(apartment_id)
            
        # Use existing feature ID if available, otherwise use a default
        feature_id = existing_features.get(feature_name, 1)
            
        apartment_features_fixture.append({
            "model": "apartments.apartmentfeature",
            "pk": str(uuid.uuid4()),  # Generate a new UUID for apartment features
            "fields": {
                "apartment_id": apartment_id,  # Keep the original apartment UUID
                "feature_id": feature_id,
                "created_at": feature_data.get("created_at", datetime.now().isoformat()),
                "updated_at": feature_data.get("updated_at", datetime.now().isoformat())
            }
        })
    
    # Save fixtures to files
    with open(os.path.join(fixture_dir, 'yad2_users.json'), 'w', encoding='utf-8') as f:
        json.dump(users_fixture, f, cls=UUIDEncoder, ensure_ascii=False, indent=2)
    
    with open(os.path.join(fixture_dir, 'yad2_user_details.json'), 'w', encoding='utf-8') as f:
        json.dump(user_details_fixture, f, cls=UUIDEncoder, ensure_ascii=False, indent=2)
    
    with open(os.path.join(fixture_dir, 'yad2_user_responses.json'), 'w', encoding='utf-8') as f:
        json.dump(user_responses_fixture, f, cls=UUIDEncoder, ensure_ascii=False, indent=2)
    
    with open(os.path.join(fixture_dir, 'yad2_apartments.json'), 'w', encoding='utf-8') as f:
        json.dump(apartments_fixture, f, cls=UUIDEncoder, ensure_ascii=False, indent=2)
    
    with open(os.path.join(fixture_dir, 'yad2_apartment_photos.json'), 'w', encoding='utf-8') as f:
        json.dump(apartment_photos_fixture, f, cls=UUIDEncoder, ensure_ascii=False, indent=2)
    
    with open(os.path.join(fixture_dir, 'yad2_apartment_features.json'), 'w', encoding='utf-8') as f:
        json.dump(apartment_features_fixture, f, cls=UUIDEncoder, ensure_ascii=False, indent=2)
    
    print(f"Fixtures saved to {fixture_dir}:")
    print(f"- {len(users_fixture)} users")
    print(f"- {len(user_details_fixture)} user details")
    print(f"- {len(user_responses_fixture)} user responses")
    print(f"- {len(apartments_fixture)} apartments")
    print(f"- {len(apartment_photos_fixture)} apartment photos")
    print(f"- {len(apartment_features_fixture)} apartment features")


if __name__ == "__main__":
    # Check if the processed file path is provided as an argument
    if len(sys.argv) > 1:
        processed_file_path = sys.argv[1]
    else:
        # Use default path
        processed_file_path = os.path.join(BASE_DIR, 'apartments', 'data', 'processed_apartments.json')
    
    # Check if user count is provided as an argument
    if len(sys.argv) > 2:
        user_count = int(sys.argv[2])
    else:
        # Use default user count
        user_count = 300
    
    # Prepare fixtures
    prepare_fixtures(processed_file_path, user_count)
