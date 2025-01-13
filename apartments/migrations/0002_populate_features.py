from django.db import migrations
import uuid


def populate_features(apps, schema_editor):
    feature_model = apps.get_model('apartments', 'Feature')

    # Define the features to insert
    features = [
        {"id": uuid.uuid4(), "name": "Parking", "active": True, "description": "Provides parking space for vehicles"},
        {"id": uuid.uuid4(), "name": "Safe Room", "active": True, "description": "A secure room for emergencies"},
        {"id": uuid.uuid4(), "name": "Elevator", "active": True, "description": "Building includes an elevator"},
        {"id": uuid.uuid4(), "name": "Balcony", "active": True, "description": "Has a private balcony"},
        {"id": uuid.uuid4(), "name": "Storage", "active": True, "description": "Includes extra storage space"},
        {"id": uuid.uuid4(), "name": "New", "active": True, "description": "Newly built or renovated property"},
        {"id": uuid.uuid4(), "name": "Garden", "active": True, "description": "Has a garden or green space"},
        {"id": uuid.uuid4(), "name": "Air Conditioning", "active": True,
         "description": "Equipped with air conditioning"},
        {"id": uuid.uuid4(), "name": "Window Bars", "active": True,
         "description": "Includes bars on windows for security"},
        {"id": uuid.uuid4(), "name": "Wheelchair Accessible", "active": True,
         "description": "Accessible for wheelchair users"},
        {"id": uuid.uuid4(), "name": "Renovated", "active": True, "description": "Recently renovated property"},
        {"id": uuid.uuid4(), "name": "Furnished", "active": True, "description": "Fully furnished property"},
        {"id": uuid.uuid4(), "name": "Gym", "active": True, "description": "Building has a gym or fitness center"},
        {"id": uuid.uuid4(), "name": "Roommates", "active": True, "description": "Suitable for sharing with roommates"},
        {"id": uuid.uuid4(), "name": "Well-maintained", "active": True, "description": "Property is well-maintained"},
        {"id": uuid.uuid4(), "name": "Pet-friendly", "active": True, "description": "Allows pets in the property"},
        {"id": uuid.uuid4(), "name": "Family-friendly", "active": True, "description": "Ideal for families"},
        {"id": uuid.uuid4(), "name": "Semi-furnished", "active": True, "description": "Partially furnished property"},
        {"id": uuid.uuid4(), "name": "Unfurnished", "active": True, "description": "Unfurnished property"},
        {"id": uuid.uuid4(), "name": "Laundry Machine", "active": True, "description": "Includes a laundry machine"},
        {"id": uuid.uuid4(), "name": "Master Bedroom", "active": True, "description": "Has a master bedroom"},
        {"id": uuid.uuid4(), "name": "Study Room", "active": True, "description": "Includes a study room"},
        {"id": uuid.uuid4(), "name": "Shared Bathroom", "active": True, "description": "Shared bathroom facilities"},
        {"id": uuid.uuid4(), "name": "Private Bathroom", "active": True, "description": "Includes a private bathroom"},
        {"id": uuid.uuid4(), "name": "Close To University", "active": True, "description": "Located near a university"},
        {"id": uuid.uuid4(), "name": "Storage Room", "active": True, "description": "Has a dedicated storage room"},
        {"id": uuid.uuid4(), "name": "Trash Chute", "active": True, "description": "Equipped with a trash chute"},
    ]

    # Bulk create the features
    feature_model.objects.bulk_create([feature_model(**feature) for feature in features])


class Migration(migrations.Migration):
    dependencies = [
        ('apartments', '0001_initial'),  # Replace <app_name> with your app name
    ]

    operations = [
        migrations.RunPython(populate_features),
    ]
