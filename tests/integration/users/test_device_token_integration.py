import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from faker import Faker

from users.models import DeviceToken

fake = Faker()

@pytest.mark.django_db
class TestDeviceTokenIntegration(TestCase):
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username=fake.email(),
            email=fake.email(),
            password='testpass123'
        )
        
        self.device_token_data = {
            'user': self.user,
            'token': 'test-device-token-123',
            'device_type': 'ios'
        }

    def test_create_device_token_success(self):
        """Test successful device token creation"""
        device_token = DeviceToken.objects.create(**self.device_token_data)
        
        self.assertIsNotNone(device_token)
        self.assertEqual(device_token.user, self.user)
        self.assertEqual(device_token.token, self.device_token_data['token'])
        self.assertEqual(device_token.device_type, self.device_token_data['device_type'])
        self.assertTrue(device_token.is_active)

    def test_create_device_token_without_required_fields(self):
        """Test device token creation without required fields fails"""
        required_fields = ['user', 'token', 'device_type']
        
        for field in required_fields:
            data = self.device_token_data.copy()
            data.pop(field)
            with self.assertRaises(Exception):  # Should raise ValidationError or IntegrityError
                device_token = DeviceToken(**data)
                device_token.full_clean()
                device_token.save()

    def test_update_device_token_success(self):
        """Test successful device token update"""
        device_token = DeviceToken.objects.create(**self.device_token_data)
        
        # Update token
        new_token = 'new-device-token-456'
        device_token.token = new_token
        device_token.save()
        
        # Refresh from database
        device_token.refresh_from_db()
        
        # Verify update
        self.assertEqual(device_token.token, new_token)

    def test_delete_device_token_success(self):
        """Test successful device token deletion"""
        device_token = DeviceToken.objects.create(**self.device_token_data)
        device_token.delete()
        
        self.assertFalse(DeviceToken.objects.filter(user=self.user).exists())

    def test_device_token_deactivation(self):
        """Test device token deactivation"""
        device_token = DeviceToken.objects.create(**self.device_token_data)
        
        # Deactivate token
        device_token.is_active = False
        device_token.save()
        
        # Refresh from database
        device_token.refresh_from_db()
        
        # Verify deactivation
        self.assertFalse(device_token.is_active)

    def test_device_token_multiple_devices(self):
        """Test that a user can have multiple device tokens"""
        # Create first device token
        DeviceToken.objects.create(**self.device_token_data)
        
        # Create second device token
        second_token_data = self.device_token_data.copy()
        second_token_data['token'] = 'test-device-token-456'
        second_token_data['device_type'] = 'android'
        DeviceToken.objects.create(**second_token_data)
        
        # Verify both tokens exist
        self.assertEqual(DeviceToken.objects.filter(user=self.user).count(), 2)

    def test_device_token_str_representation(self):
        """Test device token string representation"""
        device_token = DeviceToken.objects.create(**self.device_token_data)
        expected_str = f"{self.user.email} - {self.device_token_data['device_type']} - {self.device_token_data['token'][:10]}..."
        self.assertEqual(str(device_token), expected_str)

    def test_device_token_unique_token(self):
        """Test that token must be unique"""
        DeviceToken.objects.create(**self.device_token_data)
        
        # Try to create another device token with the same token
        another_token_data = self.device_token_data.copy()
        another_token_data['user'] = User.objects.create_user(
            username=fake.email(),
            email=fake.email(),
            password='testpass123'
        )
        
        with self.assertRaises(Exception):  # Should raise ValidationError or IntegrityError
            device_token = DeviceToken(**another_token_data)
            device_token.full_clean()
            device_token.save() 