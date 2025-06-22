import pytest
from unittest.mock import Mock
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from users.models import QuestionnaireTemplate, Question
from apartments.models import City, Feature, Apartment
from datetime import date, timedelta
from django.test import RequestFactory
from appartners.utils import generate_jwt
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal


@pytest.fixture
def mock_queryset():
    """
    Fixture that returns a mocked QuerySet object,
    used to test filter functions without hitting the real database.
    
    Ensures unit test isolation from Django ORM.
    """
    return Mock(spec=QuerySet)

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
        hebrew_name='עיר בדיקה',
        active=True
    )

@pytest.fixture
def test_feature():
    return Feature.objects.create(
        name='Test Feature',
        description='A test feature',
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

@pytest.fixture
def request_factory():
    """Fixture for creating a RequestFactory"""
    return RequestFactory()

@pytest.fixture
def test_token(test_user):
    """Fixture for creating a JWT token for tests"""
    return generate_jwt(test_user, 'access')

# Apartment fixtures
@pytest.fixture
def valid_apartment_data(test_user, test_city):
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
def test_apartment(test_user, test_city):
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
def test_image():
    return SimpleUploadedFile(
        name="test_image.jpg",
        content=b"",  # Empty content for testing
        content_type="image/jpeg"
    )

@pytest.fixture
def valid_city_data():
    return {
        'name': 'Tel Aviv',
        'hebrew_name': 'תל אביב',
        'active': True
    }

@pytest.fixture
def valid_feature_data():
    return {
        'name': 'Parking',
        'description': 'Private parking spot',
        'active': True
    }

@pytest.fixture
def mock_apartment():
    apartment = Mock()
    apartment.id = 1
    apartment.city = Mock()
    apartment.city.name = "Tel Aviv"
    apartment.city.hebrew_name = "תל אביב"
    apartment.area = "Test Area"
    apartment.floor = 3
    apartment.number_of_rooms = 2
    apartment.number_of_available_rooms = 1
    apartment.total_price = 5000.00
    apartment.apartment_features = Mock()
    apartment.apartment_features.all.return_value = []
    apartment.photos = Mock()
    apartment.photos.all.return_value = []
    apartment.photo_urls = []  # Add photo_urls field
    
    # Mock datetime fields
    mock_datetime = Mock()
    mock_datetime.astimezone = Mock(return_value=mock_datetime)
    mock_datetime.isoformat = Mock(return_value="2024-03-20T12:00:00Z")
    apartment.created_at = mock_datetime
    apartment.updated_at = mock_datetime
    
    # Mock location fields
    apartment.latitude = Decimal('32.0853000')
    apartment.longitude = Decimal('34.7818000')
    
    return apartment

@pytest.fixture
def mock_user_details():
    user_details = Mock()
    user_details.email = "user@example.com"
    return user_details

@pytest.fixture
def user_details_dict():
    return {
        'email': "user@example.com",
        'first_name': "Test",
        'last_name': "User"
    }

@pytest.fixture
def mock_user_prefs():
    prefs = Mock()
    prefs.min_price = None
    prefs.max_price = None
    prefs.city = None
    prefs.area = None
    prefs.max_floor = None
    prefs.number_of_roommates = None
    prefs.move_in_date = None
    prefs.user_preference_features = Mock()
    return prefs

@pytest.fixture
def base_query():
    query = Mock()
    query.filter = Mock(return_value=query)
    return query

@pytest.fixture
def mock_city():
    city = Mock()
    city.id = 1
    city.name = "Test City"
    return city

@pytest.fixture
def mock_user_id():
    return 1

@pytest.fixture
def mock_question_metadata():
    return {
        'type': 'radio',
        'weight': 1.0,
        'title': 'Test Question'
    }

class MockApartment:
    def __init__(self, id, compatibility_score):
        self.id = id
        self.compatibility_score = compatibility_score
        self.user_id = 1  # Add user_id field
