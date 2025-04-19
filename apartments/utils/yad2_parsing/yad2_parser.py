import json
import os
from datetime import datetime, timedelta
import random

def extract_apartments_from_file(file_path, start_index=0, max_apartments=50):
    """
    Extract apartment data from the Yad2 file which is in JSON format.
    
    Args:
        file_path: Path to the Yad2 data file
        start_index: Starting index for processing apartments
        max_apartments: Maximum number of apartments to extract
        
    Returns:
        list: List of dictionaries with simplified apartment data
        int: Total number of apartments in the file
    """
    apartments = []
    
    print(f"Processing apartments from index {start_index} to {start_index + max_apartments}")
    
    try:
        # Read the JSON data
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        total_apartments = len(data)
        print(f"Total apartments in file: {total_apartments}")
        
        # Process each apartment in the array
        for i in range(start_index, min(start_index + max_apartments, total_apartments)):
            try:
                apt = data[i]
                # Extract the required fields
                apartment = {
                    'street': apt.get('address', {}).get('street', {}).get('text', ''),
                    'longitude': apt.get('address', {}).get('coords', {}).get('lon', 0),
                    'latitude': apt.get('address', {}).get('coords', {}).get('lat', 0),
                    'floor': apt.get('address', {}).get('house', {}).get('floor', 0),
                    'number_of_rooms': apt.get('additionalDetails', {}).get('roomsCount', 0),
                    'type': apt.get('additionalDetails', {}).get('property', {}).get('text', 'Apartment'),
                    'price': apt.get('price', 0),
                    'token': apt.get('token', ''),
                    'agency_name': apt.get('customer', {}).get('agencyName', ''),
                    'square_meter': apt.get('additionalDetails', {}).get('squareMeter', 0),
                    'agency_logo': apt.get('customer', {}).get('agencyLogo', ''),
                    'images': apt.get('metaData', {}).get('images', [])[:3],  # Limit to 3 images
                    'area': apt.get('address', {}).get('neighborhood', {}).get('text', '')
                }
                
                # Only add if we have valid coordinates and street
                if apartment['longitude'] and apartment['latitude'] and apartment['street']:
                    apartments.append(apartment)
                    print(f"Found apartment: {apartment['street']} - {apartment['price']} - {len(apartment['images'])} images")
            
            except Exception as e:
                print(f"Error processing apartment {i}: {e}")
        
        print(f"Found {len(apartments)} apartments in this batch")
        return apartments, total_apartments
        
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return [], 0
    except Exception as e:
        print(f"Error processing file: {e}")
        return [], 0

def create_apartment_objects(apartments_data):
    """
    Convert the simplified apartment data to a format suitable for database insertion.
    
    Args:
        apartments_data: List of dictionaries with simplified apartment data
        
    Returns:
        list: List of dictionaries ready for database insertion
    """
    db_apartments = []
    
    for apt in apartments_data:
        # Calculate available rooms randomly (1 to number_of_rooms)
        if apt['number_of_rooms'] > 0:
            available_rooms = random.randint(1, int(apt['number_of_rooms']))
        else:
            available_rooms = 0
        
        # Generate a random future date for available_entry_date
        current_date = datetime.now()
        days_to_add = random.randint(30, 365)  # Between 1 month and 1 year
        entry_date = current_date.replace(day=1) + timedelta(days=days_to_add)
        entry_date_str = entry_date.strftime("%Y-%m-%d")
        
        # Create the apartment object
        apartment = {
            'street': apt['street'],
            'longitude': apt['longitude'],
            'latitude': apt['latitude'],
            'floor': apt['floor'],
            'number_of_rooms': apt['number_of_rooms'],
            'number_of_available_rooms': available_rooms,
            'type': apt['type'],
            'total_price': apt['price'],
            'available_entry_date': entry_date_str,
            'about': f"Apartment listed by {apt['agency_name']}" if apt['agency_name'] else None,
            'photos': apt['images'],  # This will need to be processed further to save the images
            'square_meter': apt['square_meter'],
            'area': apt.get('area', '')
        }
        
        db_apartments.append(apartment)
    
    return db_apartments

def save_to_json(apartments, output_file, append=False):
    """
    Save the processed apartment data to a JSON file.
    
    Args:
        apartments: List of apartment dictionaries
        output_file: Path to the output JSON file
        append: Whether to append to existing file or overwrite
    """
    if append and os.path.exists(output_file):
        # Read existing data
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            
            # Append new data
            combined_data = existing_data + apartments
            
            # Write combined data
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(combined_data, f, ensure_ascii=False, indent=2)
                
            print(f"Appended {len(apartments)} apartments to existing file. Total: {len(combined_data)}")
        except Exception as e:
            print(f"Error appending to file: {e}")
            # Fallback to overwrite
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(apartments, f, ensure_ascii=False, indent=2)
    else:
        # Write new file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(apartments, f, ensure_ascii=False, indent=2)
            print(f"Saved {len(apartments)} apartments to new file")

def process_all_apartments(input_file, output_file, batch_size=50):
    """
    Process all apartments in the file in batches.
    
    Args:
        input_file: Path to the input JSON file
        output_file: Path to the output JSON file
        batch_size: Number of apartments to process in each batch
    """
    start_index = 0
    total_processed = 0
    
    # Process first batch and get total count
    apartments, total_apartments = extract_apartments_from_file(input_file, start_index, batch_size)
    
    if not apartments:
        print("No apartments found in the first batch")
        return
    
    # Convert and save first batch
    db_apartments = create_apartment_objects(apartments)
    save_to_json(db_apartments, output_file, append=False)
    
    total_processed += len(db_apartments)
    start_index += batch_size
    
    # Process remaining batches
    while start_index < total_apartments:
        print(f"\nProcessing batch starting at index {start_index}")
        apartments, _ = extract_apartments_from_file(input_file, start_index, batch_size)
        
        if apartments:
            db_apartments = create_apartment_objects(apartments)
            save_to_json(db_apartments, output_file, append=True)
            
            total_processed += len(db_apartments)
        
        start_index += batch_size
    
    print(f"\nFinished processing all apartments. Total processed: {total_processed}")

def remove_duplicate_apartments(apartments_file):
    """
    Remove duplicate apartments from the processed data.
    Two apartments are considered duplicates if they have the same:
    - street
    - number_of_rooms
    - floor
    - total_price
    - type
    - square_meter
    - area
    
    Args:
        apartments_file: Path to the processed apartments JSON file
        
    Returns:
        int: Number of duplicates removed
    """
    print(f"Removing duplicate apartments from {apartments_file}")
    
    try:
        # Read the processed apartments
        with open(apartments_file, 'r', encoding='utf-8') as f:
            apartments = json.load(f)
        
        print(f"Read {len(apartments)} apartments from file")
        
        # Create a dictionary to track unique apartments
        unique_apartments = {}
        duplicates = []
        
        # Define a function to create a unique key for each apartment
        def get_apartment_key(apt):
            return (
                apt['street'],
                apt['number_of_rooms'],
                apt['floor'],
                apt['total_price'],
                apt['type'],
                apt.get('square_meter', 0),
                apt.get('area', '')
            )
        
        # Find duplicates
        for i, apt in enumerate(apartments):
            key = get_apartment_key(apt)
            
            if key in unique_apartments:
                duplicates.append(i)
            else:
                unique_apartments[key] = i
        
        print(f"Found {len(duplicates)} duplicate apartments")
        
        if duplicates:
            # Create a new list without duplicates
            unique_apt_list = [apartments[i] for i in range(len(apartments)) if i not in duplicates]
            
            # Save the deduplicated list
            with open(apartments_file, 'w', encoding='utf-8') as f:
                json.dump(unique_apt_list, f, ensure_ascii=False, indent=2)
            
            print(f"Removed {len(duplicates)} duplicates. Saved {len(unique_apt_list)} unique apartments.")
            return len(duplicates)
        else:
            print("No duplicates found.")
            return 0
    
    except Exception as e:
        print(f"Error removing duplicates: {e}")
        return 0

def main():
    # Path to the Yad2 data file
    yad2_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'yad2.json')
    
    # Output file path
    output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed_apartments.json')
    
    # Choose the operation to perform
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'deduplicate':
        # Only run deduplication
        remove_duplicate_apartments(output_file)
    else:
        # Process all apartments in batches
        process_all_apartments(yad2_file, output_file, batch_size=50)

if __name__ == "__main__":
    main()
