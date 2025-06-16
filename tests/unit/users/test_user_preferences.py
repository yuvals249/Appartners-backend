import pytest
from users.models import UserPreferences, UserPreferencesFeatures
from apartments.models import Feature
from datetime import timedelta, date

def assert_timestamps_equal(created_at, updated_at, tolerance_seconds=1):
    """Helper function to compare timestamps with tolerance"""
    assert abs((created_at - updated_at).total_seconds()) < tolerance_seconds

@pytest.mark.django_db
def test_user_preferences_cascade_delete_user(test_user, valid_user_preferences_data):
    # Create preferences
    preferences = UserPreferences.objects.create(**valid_user_preferences_data)
    
    # Delete the user
    test_user.delete()
    
    # The preferences should be deleted
    assert not UserPreferences.objects.filter(id=preferences.id).exists()

@pytest.mark.django_db
def test_user_preferences_cascade_delete_city(test_user, valid_user_preferences_data):
    # Create preferences
    preferences = UserPreferences.objects.create(**valid_user_preferences_data)
    
    # Delete the city
    valid_user_preferences_data['city'].delete()
    
    # The preferences should be deleted
    assert not UserPreferences.objects.filter(id=preferences.id).exists()

@pytest.mark.django_db
def test_user_preferences_features_str_representation(test_user, test_city, test_feature):
    # Create preferences
    preferences = UserPreferences.objects.create(
        user=test_user,
        city=test_city,
        move_in_date=date.today() + timedelta(days=30)
    )
    
    # Create preferences features
    pref_feature = UserPreferencesFeatures.objects.create(
        user_preferences=preferences,
        feature=test_feature
    )
    
    assert str(pref_feature) == f"{preferences.id} - {test_feature.name}"

@pytest.mark.django_db
def test_user_preferences_features_cascade_delete_preferences(test_user, test_city, test_feature):
    # Create preferences
    preferences = UserPreferences.objects.create(
        user=test_user,
        city=test_city,
        move_in_date=date.today() + timedelta(days=30)
    )
    
    # Create preferences features
    pref_feature = UserPreferencesFeatures.objects.create(
        user_preferences=preferences,
        feature=test_feature
    )
    
    # Delete the preferences
    preferences.delete()
    
    # The preferences features should be deleted
    assert not UserPreferencesFeatures.objects.filter(id=pref_feature.id).exists()
    assert Feature.objects.filter(id=test_feature.id).exists()

@pytest.mark.django_db
def test_user_preferences_features_cascade_delete_feature(test_user, test_city, test_feature):
    # Create preferences
    preferences = UserPreferences.objects.create(
        user=test_user,
        city=test_city,
        move_in_date=date.today() + timedelta(days=30)
    )
    
    # Create preferences features
    pref_feature = UserPreferencesFeatures.objects.create(
        user_preferences=preferences,
        feature=test_feature
    )
    
    # Delete the feature
    test_feature.delete()
    
    # The preferences features should be deleted
    assert not UserPreferencesFeatures.objects.filter(id=pref_feature.id).exists()
    assert UserPreferences.objects.filter(id=preferences.id).exists()

@pytest.mark.django_db
def test_user_preferences_features_auto_timestamps(test_user, test_city, test_feature):
    # Create preferences
    preferences = UserPreferences.objects.create(
        user=test_user,
        city=test_city,
        move_in_date=date.today() + timedelta(days=30)
    )
    
    # Create preferences features
    pref_feature = UserPreferencesFeatures.objects.create(
        user_preferences=preferences,
        feature=test_feature
    )
    
    assert pref_feature.created_at is not None
    assert pref_feature.updated_at is not None
    assert_timestamps_equal(pref_feature.created_at, pref_feature.updated_at) 