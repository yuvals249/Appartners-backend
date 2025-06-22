import pytest
from django.contrib.auth.models import User
from users.models import UserDetails
from datetime import date


def assert_timestamps_equal(created_at, updated_at, tolerance_seconds=1):
    """Helper function to compare timestamps with tolerance"""
    assert abs((created_at - updated_at).total_seconds()) < tolerance_seconds

@pytest.mark.django_db
def test_user_details_required_fields(test_user):
    # Try to create UserDetails without required fields
    with pytest.raises(Exception):  # Should raise ValidationError
        UserDetails.objects.create(
            user=test_user,
            # Missing required fields
        )

@pytest.mark.django_db
def test_user_details_phone_number_unique(test_user, valid_user_details_data):
    # Create first user details
    UserDetails.objects.create(**valid_user_details_data)
    
    # Create another user
    another_user = User.objects.create_user(
        username='anotheruser',
        email='another@example.com',
        password='testpass123'
    )
    
    # Try to create another UserDetails with the same phone number
    with pytest.raises(Exception):  # Should raise IntegrityError
        UserDetails.objects.create(
            user=another_user,
            first_name='Jane',
            last_name='Doe',
            gender='Female',
            occupation='Designer',
            birth_date=date(1992, 1, 1),
            preferred_city='Jerusalem',
            phone_number=valid_user_details_data['phone_number'],  # Same phone number
            is_yad2=False
        )

@pytest.mark.django_db
def test_user_details_cascade_delete(test_user, valid_user_details_data):
    # Create user details
    user_details = UserDetails.objects.create(**valid_user_details_data)
    
    # Delete the user
    test_user.delete()
    
    # User details should be deleted
    assert not UserDetails.objects.filter(id=user_details.id).exists()

@pytest.mark.django_db
def test_user_details_auto_timestamps(test_user, valid_user_details_data):
    user_details = UserDetails.objects.create(**valid_user_details_data)
    assert user_details.created_at is not None
    assert user_details.updated_at is not None
    assert_timestamps_equal(user_details.created_at, user_details.updated_at)

@pytest.mark.django_db
def test_user_details_update_timestamp(test_user, valid_user_details_data):
    # Create user details
    user_details = UserDetails.objects.create(**valid_user_details_data)
    initial_updated_at = user_details.updated_at
    
    # Wait a bit
    import time
    time.sleep(1)
    
    # Update the user details
    user_details.about_me = 'Updated bio'
    user_details.save()
    
    # Check that updated_at was updated
    user_details.refresh_from_db()
    assert user_details.updated_at > initial_updated_at 