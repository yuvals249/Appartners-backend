import pytest
from users.models import UserPresence
from django.utils import timezone
import time

@pytest.mark.django_db
def test_user_presence_str_representation(test_user):
    presence = UserPresence.objects.create(user=test_user)
    expected_str = f"{test_user.username} last seen at {presence.last_seen_at}"
    assert str(presence) == expected_str

@pytest.mark.django_db
def test_user_presence_one_to_one_constraint(test_user):
    # Create first presence record
    UserPresence.objects.create(user=test_user)
    
    # Try to create another presence record for the same user
    with pytest.raises(Exception):  # Should raise IntegrityError
        UserPresence.objects.create(user=test_user)

@pytest.mark.django_db
def test_user_presence_cascade_delete_user(test_user):
    # Create a presence record
    presence = UserPresence.objects.create(user=test_user)
    
    # Delete the user
    test_user.delete()
    
    # The presence record should be deleted
    assert not UserPresence.objects.filter(id=presence.id).exists()

@pytest.mark.django_db
def test_user_presence_default_timestamp(test_user):
    # Create a presence record
    presence = UserPresence.objects.create(user=test_user)
    
    # Check that last_seen_at is set to current time
    assert presence.last_seen_at is not None
    assert (timezone.now() - presence.last_seen_at).total_seconds() < 1

@pytest.mark.django_db
def test_user_presence_update_presence(test_user):
    # Create a presence record
    presence = UserPresence.objects.create(user=test_user)
    initial_last_seen = presence.last_seen_at
    time.sleep(1)
    presence.update_presence()
    presence.refresh_from_db()
    assert presence.last_seen_at > initial_last_seen 