import pytest
from django.core.exceptions import ValidationError
from apartments.models import City, Feature

@pytest.mark.django_db
def test_city_name_unique(valid_city_data):
    # Create first city
    City.objects.create(**valid_city_data)
    
    # Try to create another city with the same name
    with pytest.raises(ValidationError):
        city = City(**valid_city_data)
        city.full_clean()
        city.save()

@pytest.mark.django_db
def test_city_update_timestamp(valid_city_data):
    city = City.objects.create(**valid_city_data)
    initial_updated_at = city.updated_at
    
    # Update the city
    city.name = 'New Name'
    city.save()
    
    # Refresh from db
    city.refresh_from_db()
    assert city.updated_at > initial_updated_at

@pytest.mark.django_db
def test_feature_name_unique(valid_feature_data):
    # Create first feature
    Feature.objects.create(**valid_feature_data)
    
    # Try to create another feature with the same name
    with pytest.raises(ValidationError):
        feature = Feature(**valid_feature_data)
        feature.full_clean()
        feature.save()

@pytest.mark.django_db
def test_feature_update_timestamp(valid_feature_data):
    feature = Feature.objects.create(**valid_feature_data)
    initial_updated_at = feature.updated_at
    
    # Update the feature
    feature.name = 'New Feature'
    feature.save()
    
    # Refresh from db
    feature.refresh_from_db()
    assert feature.updated_at > initial_updated_at 