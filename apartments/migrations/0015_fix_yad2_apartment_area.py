from django.db import migrations
import json
import os
import uuid


def fix_yad2_apartment_area(apps, schema_editor):
    """
    Fix the missing area field for Yad2 apartments
    """
    # Get models
    Apartment = apps.get_model('apartments', 'Apartment')
    
    # Get all Yad2 apartments
    yad2_apartments = Apartment.objects.filter(is_yad2=True)
    
    print(f"Fixing area field for {yad2_apartments.count()} Yad2 apartments...")
    
    # Try multiple possible paths for the apartments.json file
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'data', 'db_import', 'apartments.json'),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'db_import', 'apartments.json'),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'db_import', 'apartments.json'),
    ]
    
    apartments_file = None
    for path in possible_paths:
        if os.path.exists(path):
            apartments_file = path
            break
    
    if apartments_file:
        print(f"Found apartment data at: {apartments_file}")
    else:
        print("Could not find apartments.json file")
        return
    
    # Load the original apartment data
    area_map = {}
    if apartments_file and os.path.exists(apartments_file):
        try:
            with open(apartments_file, 'r', encoding='utf-8') as f:
                apartments_data = json.load(f)
                
            # Create a mapping of apartment ID to area
            for apt_data in apartments_data:
                apt_id = apt_data.get("id")
                if apt_id:
                    # Convert UUID to string if needed
                    if isinstance(apt_id, uuid.UUID):
                        apt_id = str(apt_id)
                    area_map[apt_id] = apt_data.get("area")
                    
            print(f"Loaded {len(area_map)} apartment areas from JSON file")
        except Exception as e:
            print(f"Error loading apartment data: {e}")
            return
    
    # Update each apartment with its area
    updated_count = 0
    for apartment in yad2_apartments:
        # Get the area from the map
        apt_id_str = str(apartment.id)
        if apt_id_str in area_map and area_map[apt_id_str]:
            # Update the apartment with the correct area from the file
            apartment.area = area_map[apt_id_str]
            apartment.save(update_fields=['area'])
            updated_count += 1
    
    print(f"Updated area field for {updated_count} Yad2 apartments")


def reverse_fix_yad2_apartment_area(apps, schema_editor):
    """
    Reverse the fix by clearing the area field for Yad2 apartments
    """
    # Get models
    Apartment = apps.get_model('apartments', 'Apartment')
    
    # Get all Yad2 apartments
    yad2_apartments = Apartment.objects.filter(is_yad2=True)
    
    print(f"Clearing area field for {yad2_apartments.count()} Yad2 apartments...")
    
    # Clear the area field
    yad2_apartments.update(area=None)
    
    print(f"Cleared area field for {yad2_apartments.count()} Yad2 apartments")


class Migration(migrations.Migration):

    dependencies = [
        ('apartments', '0014_load_yad2_data'),
    ]

    operations = [
        migrations.RunPython(fix_yad2_apartment_area, reverse_fix_yad2_apartment_area),
    ]
