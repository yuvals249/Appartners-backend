import pytest
from users.models import UserUserLike


def assert_timestamps_equal(created_at, updated_at, tolerance_seconds=1):
    """Helper function to compare timestamps with tolerance"""
    assert abs((created_at - updated_at).total_seconds()) < tolerance_seconds

@pytest.mark.django_db
def test_user_user_like_str_representation(test_user, test_user2):
    # Create a like
    like = UserUserLike.objects.create(
        user=test_user,
        target_user=test_user2,
        like=True
    )
    
    assert str(like) == f"{test_user.email} likes {test_user2.email}"

@pytest.mark.django_db
def test_user_user_like_unique_constraint(test_user, test_user2):
    # Create first like
    UserUserLike.objects.create(
        user=test_user,
        target_user=test_user2,
        like=True
    )
    
    # Try to create another like for the same users
    with pytest.raises(Exception):  # Should raise IntegrityError
        UserUserLike.objects.create(
            user=test_user,
            target_user=test_user2,
            like=False  # Different like value, but still should fail
        )

@pytest.mark.django_db
def test_user_user_like_cascade_delete_user(test_user, test_user2):
    # Create a like
    like = UserUserLike.objects.create(
        user=test_user,
        target_user=test_user2,
        like=True
    )
    
    # Delete the user who created the like
    test_user.delete()
    
    # The like should be deleted
    assert not UserUserLike.objects.filter(id=like.id).exists()

@pytest.mark.django_db
def test_user_user_like_cascade_delete_target_user(test_user, test_user2):
    # Create a like
    like = UserUserLike.objects.create(
        user=test_user,
        target_user=test_user2,
        like=True
    )
    
    # Delete the target user
    test_user2.delete()
    
    # The like should be deleted
    assert not UserUserLike.objects.filter(id=like.id).exists()

@pytest.mark.django_db
def test_user_user_like_auto_timestamps(test_user, test_user2):
    like = UserUserLike.objects.create(
        user=test_user,
        target_user=test_user2,
        like=True
    )
    assert like.created_at is not None
    assert like.updated_at is not None
    assert_timestamps_equal(like.created_at, like.updated_at)

@pytest.mark.django_db
def test_user_user_like_update_timestamp(test_user, test_user2):
    # Create a like
    like = UserUserLike.objects.create(
        user=test_user,
        target_user=test_user2,
        like=True
    )
    initial_updated_at = like.updated_at
    
    # Wait a bit
    import time
    time.sleep(1)
    
    # Update the like
    like.like = False
    like.save()
    
    # Check that updated_at was updated
    like.refresh_from_db()
    assert like.updated_at > initial_updated_at 