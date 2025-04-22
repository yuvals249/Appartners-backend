import json
import os
import time
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.location import get_area_from_coordinates

def fill_missing_areas(file_path):
    """
    Fill in missing area values using the get_area_from_coordinates function.
    
    Args:
        file_path: Path to the processed apartments JSON file
    """
    print(f"Filling missing area values in {file_path}")
    
    try:
        # Read the processed apartments
        with open(file_path, 'r', encoding='utf-8') as f:
            apartments = json.load(f)
        
        total_apartments = len(apartments)
        print(f"Total apartments: {total_apartments}")
        
        if total_apartments == 0:
            print("No apartments found in the file.")
            return
        
        # Count apartments with missing area
        missing_area_count = sum(1 for apt in apartments if not apt.get('area'))
        print(f"Found {missing_area_count} apartments with missing area")
        
        # Fill in missing areas
        updated_count = 0
        for i, apt in enumerate(apartments):
            if not apt.get('area') and apt.get('latitude') and apt.get('longitude'):
                print(f"Processing apartment {i+1}/{total_apartments}: {apt['street']}")
                
                try:
                    # Get area from coordinates
                    lat = apt['latitude']
                    lon = apt['longitude']
                    area = get_area_from_coordinates(lat, lon)
                    
                    if area:
                        apt['area'] = area
                        updated_count += 1
                        print(f"  Updated area to: {area}")
                    else:
                        print(f"  Could not determine area")
                    
                    # Add a delay to avoid rate limiting (1 second)
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"  Error getting area: {e}")
        
        print(f"\nUpdated {updated_count} apartments with area information")
        
        # Save the updated data
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(apartments, f, ensure_ascii=False, indent=2)
        
        print(f"Saved updated data to {file_path}")
        
    except Exception as e:
        print(f"Error filling missing areas: {e}")

if __name__ == "__main__":
    # Path to the processed apartments file
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed_apartments.json')
    
    # Fill missing areas
    fill_missing_areas(file_path)
