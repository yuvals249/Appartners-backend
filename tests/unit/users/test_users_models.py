import pytest
from django.contrib.auth.models import User
from users.models import UserDetails, UserUserLike, DeviceToken, UserPresence, QuestionnaireTemplate, Question, UserResponse, UserPreferences, UserPreferencesFeatures
from datetime import date, datetime, timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone
from apartments.models import City, Feature
from decimal import Decimal

@pytest.fixture
def test_user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def test_user2():
    return User.objects.create_user(
        username='testuser2',
        email='test2@example.com',
        password='testpass123'
    )

@pytest.fixture
def test_city():
    return City.objects.create(
        name='Test City',
        active=True
    )

@pytest.fixture
def test_feature():
    return Feature.objects.create(
        name='Test Feature',
        active=True
    )

@pytest.fixture
def valid_user_details_data(test_user):
    return {
        'user': test_user,
        'first_name': 'John',
        'last_name': 'Doe',
        'gender': 'Male',
        'occupation': 'Software Engineer',
        'birth_date': date(1990, 1, 1),
        'preferred_city': 'Tel Aviv',
        'phone_number': '0501234567',
        'about_me': 'I love coding!',
        'is_yad2': False
    }

@pytest.fixture
def valid_device_token_data(test_user):
    return {
        'user': test_user,
        'token': 'test_device_token_123',
        'device_type': 'android',
        'is_active': True
    }

@pytest.fixture
def test_questionnaire_template():
    return QuestionnaireTemplate.objects.create(
        title='Test Questionnaire',
        description='A test questionnaire',
        order=1
    )

@pytest.fixture
def test_question(test_questionnaire_template):
    return Question.objects.create(
        questionnaire=test_questionnaire_template,
        title='Test Question',
        placeholder='Enter your answer',
        question_type='text',
        order=1
    )

@pytest.fixture
def valid_user_preferences_data(test_user, test_city):
    return {
        'user': test_user,
        'city': test_city,
        'move_in_date': date.today() + timedelta(days=30),
        'number_of_roommates': [1, 2],
        'min_price': 1000,
        'max_price': 2000,
        'max_floor': 5,
        'area': 'Test Area'
    }

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

@pytest.mark.django_db
def test_device_token_str_representation(test_user, valid_device_token_data):
    device_token = DeviceToken.objects.create(**valid_device_token_data)
    expected_str = f"{test_user.email} - {valid_device_token_data['device_type']} - {valid_device_token_data['token'][:10]}..."
    assert str(device_token) == expected_str

@pytest.mark.django_db
def test_device_token_unique_constraint(test_user, valid_device_token_data):
    # Create first device token
    DeviceToken.objects.create(**valid_device_token_data)
    
    # Try to create another token for the same user and token value
    with pytest.raises(Exception):  # Should raise IntegrityError
        DeviceToken.objects.create(
            user=test_user,
            token=valid_device_token_data['token'],  # Same token
            device_type='ios',  # Different device type, but still should fail
            is_active=True
        )

@pytest.mark.django_db
def test_device_token_cascade_delete_user(test_user, valid_device_token_data):
    # Create a device token
    device_token = DeviceToken.objects.create(**valid_device_token_data)
    
    # Delete the user
    test_user.delete()
    
    # The device token should be deleted
    assert not DeviceToken.objects.filter(id=device_token.id).exists()

@pytest.mark.django_db
def test_device_token_device_type_choices(test_user):
    with pytest.raises(ValidationError):
        token = DeviceToken(
            user=test_user,
            token='test_token',
            device_type='invalid_type'  # Invalid device type
        )
        token.full_clean()  # This will trigger validation
        token.save()

@pytest.mark.django_db
def test_device_token_auto_timestamps(test_user, valid_device_token_data):
    device_token = DeviceToken.objects.create(**valid_device_token_data)
    assert device_token.created_at is not None
    assert device_token.updated_at is not None
    assert_timestamps_equal(device_token.created_at, device_token.updated_at)

@pytest.mark.django_db
def test_device_token_update_timestamp(test_user, valid_device_token_data):
    # Create a device token
    device_token = DeviceToken.objects.create(**valid_device_token_data)
    initial_updated_at = device_token.updated_at
    
    # Wait a bit
    import time
    time.sleep(1)
    
    # Update the device token
    device_token.is_active = False
    device_token.save()
    
    # Check that updated_at was updated
    device_token.refresh_from_db()
    assert device_token.updated_at > initial_updated_at 

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
    assert (timezone.now() - presence.last_seen_at).total_seconds() < 1  # Should be within 1 second

@pytest.mark.django_db
def test_user_presence_update_presence(test_user):
    # Create a presence record
    presence = UserPresence.objects.create(user=test_user)
    initial_last_seen = presence.last_seen_at
    
    # Wait a bit
    import time
    time.sleep(1)
    
    # Update presence
    presence.update_presence()
    
    # Check that last_seen_at was updated
    presence.refresh_from_db()
    assert presence.last_seen_at > initial_last_seen 

@pytest.mark.django_db
def test_questionnaire_template_str_representation(test_questionnaire_template):
    assert str(test_questionnaire_template) == 'Test Questionnaire'

@pytest.mark.django_db
def test_questionnaire_template_ordering():
    # Create templates with different order values
    template1 = QuestionnaireTemplate.objects.create(
        title='First Template',
        description='First template',
        order=2
    )
    template2 = QuestionnaireTemplate.objects.create(
        title='Second Template',
        description='Second template',
        order=1
    )
    
    # Get templates ordered by order field
    templates = QuestionnaireTemplate.objects.all()
    assert templates[0] == template2  # Lower order first
    assert templates[1] == template1

@pytest.mark.django_db
def test_questionnaire_template_auto_timestamps(test_questionnaire_template):
    assert test_questionnaire_template.created_at is not None
    assert test_questionnaire_template.updated_at is not None
    assert_timestamps_equal(test_questionnaire_template.created_at, test_questionnaire_template.updated_at)

@pytest.mark.django_db
def test_questionnaire_template_update_timestamp(test_questionnaire_template):
    initial_updated_at = test_questionnaire_template.updated_at
    
    # Wait a bit
    import time
    time.sleep(1)
    
    # Update the template
    test_questionnaire_template.title = 'Updated Template'
    test_questionnaire_template.save()
    
    # Check that updated_at was updated
    test_questionnaire_template.refresh_from_db()
    assert test_questionnaire_template.updated_at > initial_updated_at

@pytest.mark.django_db
def test_question_str_representation(test_question):
    assert str(test_question) == 'Test Question'

@pytest.mark.django_db
def test_question_ordering(test_questionnaire_template):
    # Create questions with different order values
    question1 = Question.objects.create(
        questionnaire=test_questionnaire_template,
        title='First Question',
        placeholder='First question',
        question_type='text',
        order=2
    )
    question2 = Question.objects.create(
        questionnaire=test_questionnaire_template,
        title='Second Question',
        placeholder='Second question',
        question_type='text',
        order=1
    )
    
    # Get questions ordered by order field
    questions = Question.objects.all()
    assert questions[0] == question2  # Should be first due to order=1
    assert questions[1] == question1  # Should be second due to order=2

@pytest.mark.django_db
def test_question_cascade_delete_template(test_questionnaire_template):
    question = Question.objects.create(
        questionnaire=test_questionnaire_template,
        title='Test Question',
        placeholder='Test question',
        question_type='text',
        order=1
    )
    
    # Delete the template
    test_questionnaire_template.delete()
    
    # The question should be deleted
    assert not Question.objects.filter(id=question.id).exists()

@pytest.mark.django_db
def test_question_question_type_choices(test_questionnaire_template):
    with pytest.raises(ValidationError):
        question = Question(
            questionnaire=test_questionnaire_template,
            title='Test Question',
            placeholder='Test question',
            question_type='invalid_type',  # Invalid question type
            order=1
        )
        question.full_clean()  # This will trigger validation
        question.save()

@pytest.mark.django_db
def test_user_response_str_representation(test_user, test_question):
    response = UserResponse.objects.create(
        user=test_user,
        question=test_question,
        text_response='Test response'
    )
    expected_str = f"{test_user.email} - {test_question.title[:30]}"
    assert str(response) == expected_str

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
        numeric_response=5
    )
    
    # Check that numeric response is saved correctly
    response.refresh_from_db()
    assert response.numeric_response == 5
    assert response.text_response is None

@pytest.mark.django_db
def test_user_response_text_response(test_user, test_question):
    # Create a response with text value
    response = UserResponse.objects.create(
        user=test_user,
        question=test_question,
        text_response='Test response'
    )
    
    # Check that text response is saved correctly
    response.refresh_from_db()
    assert response.text_response == 'Test response'
    assert response.numeric_response is None

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
        city=test_city
    )
    
    # Create preferences-feature relationship
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
        city=test_city
    )
    
    # Create preferences-feature relationship
    pref_feature = UserPreferencesFeatures.objects.create(
        user_preferences=preferences,
        feature=test_feature
    )
    
    # Delete the preferences
    preferences.delete()
    
    # The relationship should be deleted
    assert not UserPreferencesFeatures.objects.filter(id=pref_feature.id).exists()
    # But the feature should still exist
    assert Feature.objects.filter(id=test_feature.id).exists()

@pytest.mark.django_db
def test_user_preferences_features_cascade_delete_feature(test_user, test_city, test_feature):
    # Create preferences
    preferences = UserPreferences.objects.create(
        user=test_user,
        city=test_city
    )
    
    # Create preferences-feature relationship
    pref_feature = UserPreferencesFeatures.objects.create(
        user_preferences=preferences,
        feature=test_feature
    )
    
    # Delete the feature
    test_feature.delete()
    
    # The relationship should be deleted
    assert not UserPreferencesFeatures.objects.filter(id=pref_feature.id).exists()
    # But the preferences should still exist
    assert UserPreferences.objects.filter(id=preferences.id).exists()

@pytest.mark.django_db
def test_user_preferences_features_auto_timestamps(test_user, test_city, test_feature):
    preferences = UserPreferences.objects.create(
        user=test_user,
        city=test_city,
        move_in_date=date.today() + timedelta(days=30)  # תאריך עתידי
    )
    
    pref_feature = UserPreferencesFeatures.objects.create(
        user_preferences=preferences,
        feature=test_feature
    )
    
    assert pref_feature.created_at is not None
    assert pref_feature.updated_at is not None
    assert_timestamps_equal(pref_feature.created_at, pref_feature.updated_at)