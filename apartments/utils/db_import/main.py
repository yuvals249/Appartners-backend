import json
import os
import sys

from .users import generate_users, generate_user_responses
from .apartments import prepare_apartments, assign_features_to_apartments

def prepare_data_for_db_import(file_path, user_count=300):
    """
    Prepare apartment data for database import.
    
    Args:
        file_path: Path to the processed apartments JSON file
        user_count: Number of users to generate
    """
    print(f"Preparing apartment data from {file_path} for database import")
    
    try:
        # Read the processed apartments
        with open(file_path, 'r', encoding='utf-8') as f:
            apartments_data = json.load(f)
        
        total_apartments = len(apartments_data)
        print(f"Total apartments: {total_apartments}")
        
        if total_apartments == 0:
            print("No apartments found in the file.")
            return
        
        # Generate users and user details
        print(f"Generating {user_count} random users...")
        users, user_details = generate_users(user_count)
        
        # Generate user responses
        print("Generating random user responses...")
        user_responses = generate_user_responses(users)
        
        # Prepare apartments for database
        print("Preparing apartments for database...")
        db_apartments = prepare_apartments(apartments_data, users)
        
        # Assign features to apartments
        print("Assigning features to apartments...")
        apartment_features = assign_features_to_apartments(db_apartments)
        
        # Save the prepared data
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(file_path))), 'data', 'db_import')
        os.makedirs(output_dir, exist_ok=True)
        
        with open(os.path.join(output_dir, 'users.json'), 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        
        with open(os.path.join(output_dir, 'user_details.json'), 'w', encoding='utf-8') as f:
            json.dump(user_details, f, ensure_ascii=False, indent=2)
        
        with open(os.path.join(output_dir, 'user_responses.json'), 'w', encoding='utf-8') as f:
            json.dump(user_responses, f, ensure_ascii=False, indent=2)
        
        with open(os.path.join(output_dir, 'apartments.json'), 'w', encoding='utf-8') as f:
            json.dump(db_apartments, f, ensure_ascii=False, indent=2)
        
        with open(os.path.join(output_dir, 'apartment_features.json'), 'w', encoding='utf-8') as f:
            json.dump(apartment_features, f, ensure_ascii=False, indent=2)
        
        print(f"\nPrepared data saved to {output_dir}:")
        print(f"- {len(users)} users")
        print(f"- {len(user_details)} user details")
        print(f"- {len(user_responses)} user responses")
        print(f"- {len(db_apartments)} apartments")
        print(f"- {len(apartment_features)} apartment features")
        
    except Exception as e:
        print(f"Error preparing data: {e}")

def main():
    # Path to the processed apartments file
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'processed_apartments.json')
    
    # Prepare apartments for database import
    prepare_data_for_db_import(file_path, user_count=300)

if __name__ == "__main__":
    main()
