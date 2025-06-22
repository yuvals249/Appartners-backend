import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from faker import Faker
from appartners.utils import generate_jwt

from apartments.models import City, Feature, Apartment
from chat.models import ChatRoom, Message
from users.models import UserDetails, UserUserLike, DeviceToken, UserResponse, Question, QuestionnaireTemplate

fake = Faker()

# Common fixtures
@pytest.fixture
def api_client():
    """Fixture for creating an APIClient"""
    return APIClient()

@pytest.fixture
def test_user():
    """Fixture for creating a test user"""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )

@pytest.fixture
def test_user1():
    """Fixture for creating the first test user"""
    user = User.objects.create_user(
        username="user1@example.com",
        email="user1@example.com",
        password="testpass123"
    )
    UserDetails.objects.create(
        user=user,
        first_name="User",
        last_name="One",
        birth_date="1990-01-01",
        gender="M",
        phone_number="0501234567",
        occupation="Student",
        preferred_city="Tel Aviv"
    )
    return user

@pytest.fixture
def test_user2():
    """Fixture for creating the second test user"""
    user = User.objects.create_user(
        username="user2@example.com",
        email="user2@example.com",
        password="testpass123"
    )
    UserDetails.objects.create(
        user=user,
        first_name="User",
        last_name="Two",
        birth_date="1990-01-01",
        gender="F",
        phone_number="0507654321",
        occupation="Student",
        preferred_city="Tel Aviv"
    )
    return user

@pytest.fixture
def test_token(test_user1):
    """Fixture for creating a JWT token for tests"""
    return generate_jwt(test_user1, 'access')

# Apartment fixtures
@pytest.fixture
def test_city():
    """Fixture for creating a test city"""
    return City.objects.create(
        name="Beer Sheva",
        hebrew_name="באר שבע",
    )

@pytest.fixture
def test_feature():
    """Fixture for creating a test feature"""
    return Feature.objects.create(
        name="Parking",
        description="Provides parking space for vehicles",
    )

@pytest.fixture
def test_apartment(test_user, test_city):
    """Fixture for creating a test apartment"""
    return Apartment.objects.create(
        user=test_user,
        city=test_city,
        street='Test Street',
        type='Apartment',
        floor=1,
        number_of_rooms=2,
        number_of_available_rooms=1,
        total_price=1000,
        available_entry_date=date.today() + timedelta(days=30),
        about='Test Description'
    )

@pytest.fixture
def valid_apartment_data(test_user, test_city):
    """Fixture for valid apartment data"""
    return {
        "user": test_user,
        "city": test_city,
        "street": "Rager",
        "type": "Apartment",
        "floor": 3,
        "number_of_rooms": 3,
        "number_of_available_rooms": 2,
        "total_price": Decimal('2500.00'),
        "available_entry_date": date.today() + timedelta(days=30),
        "about": "A nice apartment in Beer Sheva",
        "latitude": Decimal('31.2518000'),
        "longitude": Decimal('34.7913000'),
        "area": "Old City",
    }

@pytest.fixture
def valid_city_data():
    """Fixture for valid city data"""
    return {
        'name': 'Tel Aviv',
        'hebrew_name': 'תל אביב',
        'active': True
    }

@pytest.fixture
def valid_feature_data():
    """Fixture for valid feature data"""
    return {
        'name': 'Parking',
        'description': 'Private parking spot',
        'active': True
    }

# Chat fixtures
@pytest.fixture
def test_chat_room(test_user1, test_user2):
    """Fixture for creating a test chat room"""
    chat_room = ChatRoom.objects.create(name="Test Chat Room")
    chat_room.participants.add(test_user1, test_user2)
    return chat_room

@pytest.fixture
def test_message(test_chat_room, test_user1):
    """Fixture for creating a test message"""
    return Message.objects.create(
        room=test_chat_room,
        sender=test_user1,
        content="Test message",
        firebase_id="test_firebase_id"
    )

# User fixtures
@pytest.fixture
def test_user_like_data(test_user1, test_user2):
    """Fixture for user like data"""
    return {
        'user': test_user1,
        'target_user': test_user2,
        'like': True
    }

@pytest.fixture
def test_device_token_data(test_user1):
    """Fixture for device token data"""
    return {
        'user': test_user1,
        'token': 'test-device-token-123',
        'device_type': 'ios'
    }

@pytest.fixture
def test_questionnaire():
    """Fixture for creating a test questionnaire"""
    return QuestionnaireTemplate.objects.create(
        title='Test Questionnaire',
        description='A test questionnaire'
    )

@pytest.fixture
def test_question(test_questionnaire):
    """Fixture for creating a test question"""
    return Question.objects.create(
        questionnaire=test_questionnaire,
        title='What is your favorite color?',
        question_type='text',
        placeholder='Enter your favorite color'
    )

@pytest.fixture
def test_user_response_data(test_user1, test_question):
    """Fixture for user response data"""
    return {
        'user': test_user1,
        'question': test_question,
        'text_response': 'Blue',
        'numeric_response': None
    } 