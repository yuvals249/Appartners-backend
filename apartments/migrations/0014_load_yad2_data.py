from django.db import migrations
from django.core.management import call_command
import os
from pathlib import Path


def load_yad2_data(apps, schema_editor):
    """
    Load Yad2 data from fixture files
    """
    # Get the path to the fixture files
    fixture_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fixtures')
    
    # Load fixtures in the correct order
    fixtures = [
        'yad2_cities.json',
        'yad2_users.json',
        'yad2_user_details.json',
        'yad2_user_responses.json',
        'yad2_apartments.json',
        'yad2_apartment_photos.json',
        'yad2_apartment_features.json',
    ]
    
    for fixture in fixtures:
        fixture_path = os.path.join(fixture_dir, fixture)
        if os.path.exists(fixture_path):
            print(f"Loading fixture: {fixture}")
            if fixture == 'yad2_users.json':
                call_command('loaddata', fixture_path, app_label='auth')
            elif fixture in ['yad2_user_details.json', 'yad2_user_responses.json']:
                call_command('loaddata', fixture_path, app_label='users')
            else:
                call_command('loaddata', fixture_path, app_label='apartments')
        else:
            print(f"Warning: Fixture file {fixture_path} not found, skipping...")


def remove_yad2_data(apps, schema_editor):
    """
    Remove Yad2 data from the database
    """
    # Get models
    User = apps.get_model('auth', 'User')
    UserDetails = apps.get_model('users', 'UserDetails')
    UserResponse = apps.get_model('users', 'UserResponse')
    Apartment = apps.get_model('apartments', 'Apartment')
    ApartmentFeature = apps.get_model('apartments', 'ApartmentFeature')
    ApartmentPhoto = apps.get_model('apartments', 'ApartmentPhoto')
    
    # Remove Yad2 data
    print("Removing Yad2 data...")
    
    # Remove apartment features and photos for Yad2 apartments
    yad2_apartments = Apartment.objects.filter(is_yad2=True)
    ApartmentFeature.objects.filter(apartment__in=yad2_apartments).delete()
    ApartmentPhoto.objects.filter(apartment__in=yad2_apartments).delete()
    
    # Remove Yad2 apartments
    yad2_apartments.delete()
    
    # Remove user responses for Yad2 users
    yad2_user_details = UserDetails.objects.filter(is_yad2=True)
    yad2_user_ids = [ud.user_id for ud in yad2_user_details]
    UserResponse.objects.filter(user_id__in=yad2_user_ids).delete()
    
    # Remove Yad2 user details
    yad2_user_details.delete()
    
    # Remove Yad2 users
    User.objects.filter(id__in=yad2_user_ids).delete()
    
    print("Yad2 data removed successfully!")


class Migration(migrations.Migration):

    dependencies = [
        ('apartments', '0013_remove_apartment_house_number_apartment_is_yad2'),
        ('users', '0016_userdetails_is_yad2'),
    ]

    operations = [
        migrations.RunPython(load_yad2_data, remove_yad2_data),
    ]
