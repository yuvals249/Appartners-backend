#!/usr/bin/env python
"""
Script to import Yad2 apartment data into the database.
This script will:
1. Use the already processed apartment data
2. Generate users and user details
3. Create apartments with features
4. Import all data into the database
"""

import os
import sys
import json
import django
from datetime import datetime

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appartners.settings')
django.setup()

# Import Django models
from django.contrib.auth.models import User
from django.db import transaction
from apartments.models import Apartment, Feature, ApartmentFeature, City
from users.models import UserDetails, UserResponse
from questionnaire.models import Question

# Import data processing functions
from apartments.utils.db_import.main import prepare_data_for_db_import


def import_yad2_data(processed_file_path, user_count=300):
    """
    Import Yad2 data into the database
    
    Args:
        processed_file_path: Path to the processed apartments JSON file
        user_count: Number of users to generate
    """
    print(f"Starting Yad2 data import process from {processed_file_path}")
    
    # Check if the processed file exists
    if not os.path.exists(processed_file_path):
        print(f"Error: Processed file {processed_file_path} does not exist!")
        return
    
    # Step 1: Prepare data for database import
    print(f"Preparing data for database import with {user_count} users...")
    prepare_data_for_db_import(processed_file_path, user_count)
    
    # Step 2: Import prepared data into the database
    import_prepared_data()
    
    print("Yad2 data import completed successfully!")


def import_prepared_data():
    """
    Import prepared data into the database
    """
    print("Importing prepared data into the database...")
    
    # Get paths to the prepared data files
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                           'data', 'db_import')
    
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
    
    # Import data into the database
    with transaction.atomic():
        # Import users
        print(f"Importing {len(users_data)} users...")
        for user_data in users_data:
            user = User.objects.create_user(
                username=user_data['email'],
                email=user_data['email'],
                password='yad2user123',  # Default password
                first_name=user_data['name'].split()[0],
                last_name=' '.join(user_data['name'].split()[1:]) if len(user_data['name'].split()) > 1 else '',
                date_joined=datetime.fromisoformat(user_data['created_at']),
                is_active=True
            )
            user.save()
        
        # Import user details
        print(f"Importing {len(user_details_data)} user details...")
        for detail_data in user_details_data:
            user = User.objects.get(email=next(u['email'] for u in users_data if u['id'] == detail_data['user_id']))
            
            user_detail = UserDetails(
                user=user,
                first_name=user.first_name,
                last_name=user.last_name,
                gender='Male' if 'gender' not in detail_data else detail_data['gender'],
                occupation='Student' if 'occupation' not in detail_data else detail_data['occupation'],
                birth_date='1990-01-01' if 'birth_date' not in detail_data else detail_data['birth_date'],
                preferred_city='Beer Sheva' if 'preferred_city' not in detail_data else detail_data['preferred_city'],
                phone_number=detail_data['phone'],
                about_me='Yad2 imported user' if 'about_me' not in detail_data else detail_data['about_me'],
                is_yad2=True
            )
            user_detail.save()
        
        # Import user responses
        print(f"Importing {len(user_responses_data)} user responses...")
        for response_data in user_responses_data:
            user = User.objects.get(email=next(u['email'] for u in users_data if u['id'] == response_data['user_id']))
            question = Question.objects.get(id=int(response_data['question_id']))
            
            user_response = UserResponse(
                user=user,
                question=question,
                response=response_data['response'],
                created_at=datetime.fromisoformat(response_data['created_at']),
                updated_at=datetime.fromisoformat(response_data['updated_at'])
            )
            user_response.save()
        
        # Import apartments
        print(f"Importing {len(apartments_data)} apartments...")
        for apt_data in apartments_data:
            # Get the user
            user = User.objects.get(email=next(u['email'] for u in users_data if u['id'] == apt_data['user_id']))
            
            # Get or create the city
            city, _ = City.objects.get_or_create(name=apt_data['city'])
            
            # Create the apartment
            apartment = Apartment(
                id=apt_data['id'],
                user=user,
                city=city,
                street=apt_data['street'],
                type=apt_data['type'],
                floor=apt_data['floor'],
                number_of_rooms=apt_data['number_of_rooms'],
                number_of_available_rooms=apt_data['number_of_available_rooms'],
                total_price=apt_data['total_price'],
                available_entry_date=apt_data['available_entry_date'],
                about=apt_data['about'],
                latitude=apt_data['latitude'],
                longitude=apt_data['longitude'],
                area=apt_data['area'],
                created_at=datetime.fromisoformat(apt_data['created_at']),
                updated_at=datetime.fromisoformat(apt_data['updated_at']),
                is_yad2=True
            )
            apartment.save()
        
        # Import apartment features
        print(f"Importing {len(apartment_features_data)} apartment features...")
        for feature_data in apartment_features_data:
            apartment = Apartment.objects.get(id=feature_data['apartment_id'])
            feature, _ = Feature.objects.get_or_create(name=feature_data['feature'])
            
            apartment_feature = ApartmentFeature(
                id=feature_data['id'],
                apartment=apartment,
                feature=feature,
                created_at=datetime.fromisoformat(feature_data['created_at']),
                updated_at=datetime.fromisoformat(feature_data['updated_at'])
            )
            apartment_feature.save()
    
    print("Data import completed successfully!")


if __name__ == "__main__":
    # Check if the processed file path is provided as an argument
    if len(sys.argv) > 1:
        processed_file_path = sys.argv[1]
    else:
        # Use default path
        processed_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                         'data', 'processed_apartments.json')
    
    # Check if user count is provided as an argument
    user_count = 300
    if len(sys.argv) > 2:
        try:
            user_count = int(sys.argv[2])
        except ValueError:
            print(f"Invalid user count: {sys.argv[2]}. Using default: 300")
    
    import_yad2_data(processed_file_path, user_count)
