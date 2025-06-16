import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from faker import Faker
from datetime import date

from users.models import UserDetails

fake = Faker()

@pytest.mark.django_db
class TestUserDetailsIntegration(TestCase):
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username=fake.email(),
            email=fake.email(),
            password='testpass123'
        )
        
        self.user_details_data = {
            'user': self.user,
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'gender': 'Male',
            'birth_date': date(1990, 1, 1),
            'phone_number': '+972501234567',
            'occupation': 'Software Engineer',
            'preferred_city': 'Tel Aviv',
            'about_me': 'I love coding and hiking'
        }

    def test_create_user_details_success(self):
        """Test successful user details creation"""
        user_details = UserDetails.objects.create(**self.user_details_data)
        
        self.assertIsNotNone(user_details)
        self.assertEqual(user_details.user, self.user)
        self.assertEqual(user_details.first_name, self.user_details_data['first_name'])
        self.assertEqual(user_details.last_name, self.user_details_data['last_name'])
        self.assertEqual(user_details.gender, self.user_details_data['gender'])
        self.assertEqual(user_details.birth_date, self.user_details_data['birth_date'])
        self.assertEqual(user_details.phone_number, self.user_details_data['phone_number'])
        self.assertEqual(user_details.occupation, self.user_details_data['occupation'])
        self.assertEqual(user_details.preferred_city, self.user_details_data['preferred_city'])
        self.assertEqual(user_details.about_me, self.user_details_data['about_me'])

    def test_create_user_details_without_required_fields(self):
        """Test user details creation without required fields fails"""
        required_fields = ['user', 'first_name', 'last_name', 'gender', 'birth_date', 'phone_number']
        
        for field in required_fields:
            data = self.user_details_data.copy()
            data.pop(field)
            with self.assertRaises(Exception):  # Should raise ValidationError or IntegrityError
                user_details = UserDetails(**data)
                user_details.full_clean()
                user_details.save()

    def test_update_user_details_success(self):
        """Test successful user details update"""
        user_details = UserDetails.objects.create(**self.user_details_data)
        
        # Update details
        new_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'gender': 'Female',
            'birth_date': date(1992, 2, 2),
            'occupation': 'Data Scientist',
            'preferred_city': 'Jerusalem',
            'about_me': 'I love data and AI'
        }
        
        for key, value in new_data.items():
            setattr(user_details, key, value)
        user_details.save()
        
        # Refresh from database
        user_details.refresh_from_db()
        
        # Verify updates
        self.assertEqual(user_details.first_name, new_data['first_name'])
        self.assertEqual(user_details.last_name, new_data['last_name'])
        self.assertEqual(user_details.gender, new_data['gender'])
        self.assertEqual(user_details.birth_date, new_data['birth_date'])
        self.assertEqual(user_details.occupation, new_data['occupation'])
        self.assertEqual(user_details.preferred_city, new_data['preferred_city'])
        self.assertEqual(user_details.about_me, new_data['about_me'])

    def test_delete_user_details_success(self):
        """Test successful user details deletion"""
        user_details = UserDetails.objects.create(**self.user_details_data)
        user_details.delete()
        
        self.assertFalse(UserDetails.objects.filter(user=self.user).exists())

    def test_user_details_str_representation(self):
        """Test user details string representation"""
        user_details = UserDetails.objects.create(**self.user_details_data)
        self.assertEqual(str(user_details), f"UserDetails object ({user_details.id})")

    def test_user_details_timestamps(self):
        """Test that created_at and updated_at are set correctly"""
        user_details = UserDetails.objects.create(**self.user_details_data)
        
        self.assertIsNotNone(user_details.created_at)
        self.assertIsNotNone(user_details.updated_at)
        # Allow for small time differences due to database operations
        self.assertAlmostEqual(user_details.created_at.timestamp(), user_details.updated_at.timestamp(), delta=1)

    def test_user_details_phone_number_validation(self):
        """Test phone number validation"""
        # Test invalid phone number format
        self.user_details_data['phone_number'] = 'invalid'
        
        with self.assertRaises(Exception):  # Should raise ValidationError or IntegrityError
            user_details = UserDetails(**self.user_details_data)
            user_details.full_clean()
            user_details.save()
        
        # Test phone number too long
        self.user_details_data['phone_number'] = '+972501234567890'
        
        with self.assertRaises(Exception):  # Should raise ValidationError or IntegrityError
            user_details = UserDetails(**self.user_details_data)
            user_details.full_clean()
            user_details.save()
            
    def test_user_details_gender_validation(self):
        """Test gender validation"""
        # Test invalid gender
        self.user_details_data['gender'] = 'Invalid'
        
        with self.assertRaises(Exception):  # Should raise ValidationError or IntegrityError
            user_details = UserDetails(**self.user_details_data)
            user_details.full_clean()
            user_details.save()
            
    def test_user_details_birth_date_validation(self):
        """Test birth date validation"""
        # Test future birth date
        self.user_details_data['birth_date'] = date(2025, 1, 1)
        
        with self.assertRaises(Exception):  # Should raise ValidationError or IntegrityError
            user_details = UserDetails(**self.user_details_data)
            user_details.full_clean()
            user_details.save() 