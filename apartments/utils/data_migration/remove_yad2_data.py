#!/usr/bin/env python
"""
Script to remove all Yad2 imported data from the database.
This script will:
1. Remove all apartments marked with is_yad2=True
2. Remove all users and user details associated with Yad2 data
3. Remove all user responses from Yad2 users
"""

import os
import sys
import django
from datetime import datetime

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appartners.settings')
django.setup()

# Import Django models
from django.contrib.auth.models import User
from django.db import transaction
from apartments.models import Apartment, ApartmentFeature, ApartmentPhoto
from users.models import UserDetails, UserResponse


def remove_yad2_data(dry_run=False):
    """
    Remove all Yad2 data from the database
    
    Args:
        dry_run: If True, only print what would be deleted without actually deleting
    """
    action = "Would delete" if dry_run else "Deleting"
    
    print("Starting Yad2 data removal process")
    print(f"Mode: {'DRY RUN - no data will be deleted' if dry_run else 'LIVE - data will be deleted'}")
    
    with transaction.atomic():
        # Get all Yad2 apartments
        yad2_apartments = Apartment.objects.filter(is_yad2=True)
        apartment_count = yad2_apartments.count()
        print(f"{action} {apartment_count} Yad2 apartments")
        
        if not dry_run:
            # Delete apartment features first (foreign key constraint)
            apartment_ids = list(yad2_apartments.values_list('id', flat=True))
            apartment_features = ApartmentFeature.objects.filter(apartment_id__in=apartment_ids)
            feature_count = apartment_features.count()
            print(f"Deleting {feature_count} apartment features")
            apartment_features.delete()
            
            # Delete apartment photos
            apartment_photos = ApartmentPhoto.objects.filter(apartment_id__in=apartment_ids)
            photo_count = apartment_photos.count()
            print(f"Deleting {photo_count} apartment photos")
            apartment_photos.delete()
            
            # Delete apartments
            yad2_apartments.delete()
        
        # Get all Yad2 user details
        yad2_user_details = UserDetails.objects.filter(is_yad2=True)
        user_detail_count = yad2_user_details.count()
        print(f"{action} {user_detail_count} Yad2 user details")
        
        # Get users associated with Yad2 user details
        user_ids = list(yad2_user_details.values_list('user_id', flat=True))
        
        # Get user responses from Yad2 users
        user_responses = UserResponse.objects.filter(user_id__in=user_ids)
        response_count = user_responses.count()
        print(f"{action} {response_count} user responses")
        
        if not dry_run:
            # Delete user responses
            user_responses.delete()
            
            # Delete user details
            yad2_user_details.delete()
            
            # Delete users
            users = User.objects.filter(id__in=user_ids)
            user_count = users.count()
            print(f"Deleting {user_count} users")
            users.delete()
    
    print("Yad2 data removal completed successfully!")


if __name__ == "__main__":
    # Check if dry run is specified
    dry_run = False
    if len(sys.argv) > 1 and sys.argv[1].lower() in ['--dry-run', '-d']:
        dry_run = True
    
    remove_yad2_data(dry_run)
