import pytest
from users.models import UserResponse


def assert_timestamps_equal(created_at, updated_at, tolerance_seconds=1):
    """Helper function to compare timestamps with tolerance"""
    assert abs((created_at - updated_at).total_seconds()) < tolerance_seconds

@pytest.mark.django_db
def test_user_response_str_representation(test_user, test_question):
    response = UserResponse.objects.create(
        user=test_user,
        question=test_question,
        text_response='Test response'
    )
    assert str(response) == f"{test_user.email} - {test_question.title}"

@pytest.mark.django_db
def test_user_response_unique_constraint(test_user, test_question):
    # Create first response
    UserResponse.objects.create(
        user=test_user,
        question=test_question,
        text_response='First response'
    )
    
    # Try to create another response for the same user and question
    with pytest.raises(Exception):  # Should raise IntegrityError
        UserResponse.objects.create(
            user=test_user,
            question=test_question,
            text_response='Second response'
        )

@pytest.mark.django_db
def test_user_response_cascade_delete_user(test_user, test_question):
    # Create a response
    response = UserResponse.objects.create(
        user=test_user,
        question=test_question,
        text_response='Test response'
    )
    
    # Delete the user
    test_user.delete()
    
    # The response should be deleted
    assert not UserResponse.objects.filter(id=response.id).exists()

@pytest.mark.django_db
def test_user_response_cascade_delete_question(test_user, test_question):
    # Create a response
    response = UserResponse.objects.create(
        user=test_user,
        question=test_question,
        text_response='Test response'
    )
    
    # Delete the question
    test_question.delete()
    
    # The response should be deleted
    assert not UserResponse.objects.filter(id=response.id).exists()

@pytest.mark.django_db
def test_user_response_auto_timestamps(test_user, test_question):
    response = UserResponse.objects.create(
        user=test_user,
        question=test_question,
        text_response='Test response'
    )
    assert response.created_at is not None
    assert response.updated_at is not None
    assert_timestamps_equal(response.created_at, response.updated_at)

@pytest.mark.django_db
def test_user_response_update_timestamp(test_user, test_question):
    # Create a response
    response = UserResponse.objects.create(
        user=test_user,
        question=test_question,
        text_response='Test response'
    )
    initial_updated_at = response.updated_at
    
    # Wait a bit
    import time
    time.sleep(1)
    
    # Update the response
    response.text_response = 'Updated response'
    response.save()
    
    # Check that updated_at was updated
    response.refresh_from_db()
    assert response.updated_at > initial_updated_at

@pytest.mark.django_db
def test_user_response_numeric_response(test_user, test_question):
    # Create a response with numeric value
    response = UserResponse.objects.create(
        user=test_user,
        question=test_question,
        numeric_response=42
    )
    
    # Check that the response was created correctly
    assert response.numeric_response == 42
    assert response.text_response is None

@pytest.mark.django_db
def test_user_response_text_response(test_user, test_question):
    # Create a response with text value
    response = UserResponse.objects.create(
        user=test_user,
        question=test_question,
        text_response='Test response'
    )
    
    # Check that the response was created correctly
    assert response.text_response == 'Test response'
    assert response.numeric_response is None 