import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from faker import Faker
from datetime import timedelta

from users.models import UserPreferences
from apartments.models import City

fake = Faker()

@pytest.mark.django_db
class TestUserPreferencesIntegration(TestCase):
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username=fake.email(),
            email=fake.email(),
            password='testpass123'
        )
        
        self.city = City.objects.create(
            name='Tel Aviv',
            hebrew_name='תל אביב'
        )
        
        self.preferences_data = {
            'user': self.user,
            'city': self.city,
            'move_in_date': timezone.now().date() + timedelta(days=30),
            'number_of_roommates': [1, 2],
            'min_price': 2000,
            'max_price': 4000,
            'max_floor': 5,
            'area': 'Center'
        }

    def test_create_user_preferences_success(self):
        """Test successful user preferences creation"""
        user_preferences = UserPreferences.objects.create(**self.preferences_data)
        
        self.assertIsNotNone(user_preferences)
        self.assertEqual(user_preferences.user, self.user)
        self.assertEqual(user_preferences.city, self.city)
        self.assertEqual(user_preferences.move_in_date, self.preferences_data['move_in_date'])
        self.assertEqual(user_preferences.number_of_roommates, self.preferences_data['number_of_roommates'])
        self.assertEqual(user_preferences.min_price, self.preferences_data['min_price'])
        self.assertEqual(user_preferences.max_price, self.preferences_data['max_price'])
        self.assertEqual(user_preferences.max_floor, self.preferences_data['max_floor'])
        self.assertEqual(user_preferences.area, self.preferences_data['area'])

    def test_create_user_preferences_without_required_fields(self):
        """Test user preferences creation without required fields fails"""
        required_fields = ['user', 'city']
        
        for field in required_fields:
            data = self.preferences_data.copy()
            data.pop(field)
            with self.assertRaises(ValidationError):
                user_preferences = UserPreferences(**data)
                user_preferences.full_clean()
                user_preferences.save()

    def test_update_user_preferences_success(self):
        """Test successful user preferences update"""
        user_preferences = UserPreferences.objects.create(**self.preferences_data)
        
        # Update preferences
        new_data = {
            'move_in_date': timezone.now().date() + timedelta(days=60),
            'number_of_roommates': [2, 3],
            'min_price': 3000,
            'max_price': 5000,
            'max_floor': 10,
            'area': 'North'
        }
        
        for key, value in new_data.items():
            setattr(user_preferences, key, value)
        user_preferences.save()
        
        # Refresh from database
        user_preferences.refresh_from_db()
        
        # Verify updates
        self.assertEqual(user_preferences.move_in_date, new_data['move_in_date'])
        self.assertEqual(user_preferences.number_of_roommates, new_data['number_of_roommates'])
        self.assertEqual(user_preferences.min_price, new_data['min_price'])
        self.assertEqual(user_preferences.max_price, new_data['max_price'])
        self.assertEqual(user_preferences.max_floor, new_data['max_floor'])
        self.assertEqual(user_preferences.area, new_data['area'])

    def test_delete_user_preferences_success(self):
        """Test successful user preferences deletion"""
        user_preferences = UserPreferences.objects.create(**self.preferences_data)
        user_preferences.delete()
        
        self.assertFalse(UserPreferences.objects.filter(user=self.user).exists())

    def test_user_preferences_validation(self):
        """Test user preferences validation"""
        # Test min_price < max_price
        self.preferences_data['min_price'] = 5000
        self.preferences_data['max_price'] = 3000
        
        with self.assertRaises(ValidationError):
            user_preferences = UserPreferences(**self.preferences_data)
            user_preferences.full_clean()
            user_preferences.save()
            
        # Test negative min_price
        self.preferences_data['min_price'] = -1000
        self.preferences_data['max_price'] = 3000
        
        with self.assertRaises(ValidationError):
            user_preferences = UserPreferences(**self.preferences_data)
            user_preferences.full_clean()
            user_preferences.save()
            
        # Test negative max_price
        self.preferences_data['min_price'] = 2000
        self.preferences_data['max_price'] = -1000
        
        with self.assertRaises(ValidationError):
            user_preferences = UserPreferences(**self.preferences_data)
            user_preferences.full_clean()
            user_preferences.save()
            
        # Test negative max_floor
        self.preferences_data['max_floor'] = -1
        
        with self.assertRaises(ValidationError):
            user_preferences = UserPreferences(**self.preferences_data)
            user_preferences.full_clean()
            user_preferences.save() 