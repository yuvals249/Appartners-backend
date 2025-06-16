import pytest
from users.models import DeviceToken
from django.core.exceptions import ValidationError
import time


def assert_timestamps_equal(created_at, updated_at, tolerance_seconds=1):
    """Helper function to compare timestamps with tolerance"""
    assert abs((created_at - updated_at).total_seconds()) < tolerance_seconds

@pytest.mark.django_db
def test_device_token_str_representation(test_user, valid_device_token_data):
    device_token = DeviceToken.objects.create(**valid_device_token_data)
    expected_str = f"{test_user.email} - {valid_device_token_data['device_type']} - {valid_device_token_data['token'][:10]}..."
    assert str(device_token) == expected_str

@pytest.mark.django_db
def test_device_token_unique_constraint(test_user, valid_device_token_data):
    DeviceToken.objects.create(**valid_device_token_data)
    with pytest.raises(Exception):
        DeviceToken.objects.create(
            user=test_user,
            token=valid_device_token_data['token'],
            device_type='ios',
            is_active=True
        )

@pytest.mark.django_db
def test_device_token_cascade_delete_user(test_user, valid_device_token_data):
    device_token = DeviceToken.objects.create(**valid_device_token_data)
    test_user.delete()
    assert not DeviceToken.objects.filter(id=device_token.id).exists()

@pytest.mark.django_db
def test_device_token_device_type_choices(test_user):
    with pytest.raises(ValidationError):
        token = DeviceToken(
            user=test_user,
            token='test_token',
            device_type='invalid_type'
        )
        token.full_clean()
        token.save()

@pytest.mark.django_db
def test_device_token_auto_timestamps(test_user, valid_device_token_data):
    device_token = DeviceToken.objects.create(**valid_device_token_data)
    assert device_token.created_at is not None
    assert device_token.updated_at is not None
    assert_timestamps_equal(device_token.created_at, device_token.updated_at)

@pytest.mark.django_db
def test_device_token_update_timestamp(test_user, valid_device_token_data):
    device_token = DeviceToken.objects.create(**valid_device_token_data)
    initial_updated_at = device_token.updated_at
    time.sleep(1)
    device_token.is_active = False
    device_token.save()
    device_token.refresh_from_db()
    assert device_token.updated_at > initial_updated_at 