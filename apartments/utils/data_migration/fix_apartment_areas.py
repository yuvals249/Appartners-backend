#!/usr/bin/env python
"""
Script to fix the area field for Yad2 apartments.
This script will:
1. Read the area values from the original JSON file
2. Update the area field for all Yad2 apartments
"""

import os
import sys
import json
import django

# Set up Django environment
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appartners.settings')
django.setup()

# Import Django models
from apartments.models import Apartment


def fix_apartment_areas():
    """
    Fix the area field for Yad2 apartments
    """
    # Get all Yad2 apartments
    yad2_apartments = Apartment.objects.filter(is_yad2=True)
    
    print(f"Fixing area field for {yad2_apartments.count()} Yad2 apartments...")
    
    # Get the path to the apartments.json file
    apartments_file = os.path.join(BASE_DIR, 'data', 'db_import', 'apartments.json')
    
    print(f"Looking for apartment data at: {apartments_file}")
    
    # Load the original apartment data
    area_map = {}
    if os.path.exists(apartments_file):
        try:
            with open(apartments_file, 'r', encoding='utf-8') as f:
                apartments_data = json.load(f)
                
            # Create a mapping of apartment ID to area
            for apt_data in apartments_data:
                apt_id = apt_data.get("id")
                if apt_id:
                    area_map[str(apt_id)] = apt_data.get("area")
                    
            print(f"Loaded {len(area_map)} apartment areas from JSON file")
        except Exception as e:
            print(f"Error loading apartment data: {e}")
    else:
        print(f"Warning: Apartment data file not found at {apartments_file}")
    
    # Update each apartment with its area
    updated_count = 0
    for apartment in yad2_apartments:
        # Get the area from the map
        apt_id_str = str(apartment.id)
        if apt_id_str in area_map and area_map[apt_id_str]:
            # Update the apartment with the correct area
            apartment.area = area_map[apt_id_str]
            apartment.save(update_fields=['area'])
            updated_count += 1
    
    print(f"Updated area field for {updated_count} Yad2 apartments")


if __name__ == "__main__":
    fix_apartment_areas()
