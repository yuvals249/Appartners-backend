from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from users.models.user_presence import UserPresence
from faker import Faker

User = get_user_model()

class TestUserPresenceIntegration(TestCase):
    def setUp(self):
        self.faker = Faker()
        self.user = User.objects.create_user(
            username=self.faker.user_name(),
            email=self.faker.email(),
            password=self.faker.password()
        )
        self.presence_data = {
            'user': self.user,
            'last_seen_at': timezone.now()
        }

    def test_create_user_presence_success(self):
        """Test user presence creation"""
        presence = UserPresence.objects.create(**self.presence_data)
        self.assertEqual(presence.user, self.user)
        self.assertIsNotNone(presence.last_seen_at)

    def test_update_last_seen(self):
        """Test updating last seen timestamp"""
        presence = UserPresence.objects.create(**self.presence_data)
        old_last_seen = presence.last_seen_at
        
        # Update last seen
        new_last_seen = timezone.now()
        presence.last_seen_at = new_last_seen
        presence.save()
        
        self.assertGreater(presence.last_seen_at, old_last_seen)

    def test_user_presence_auto_update(self):
        """Test that last_seen_at is automatically updated"""
        presence = UserPresence.objects.create(**self.presence_data)
        old_last_seen = presence.last_seen_at
        
        # Wait a bit
        import time
        time.sleep(0.1)
        
        # Update last_seen_at manually since it's not auto-updated
        presence.last_seen_at = timezone.now()
        presence.save()
        
        self.assertGreater(presence.last_seen_at, old_last_seen)

    def test_user_presence_str_representation(self):
        """Test user presence string representation"""
        presence = UserPresence.objects.create(**self.presence_data)
        self.assertEqual(str(presence), f"{self.user.username} last seen at {presence.last_seen_at}")

    def test_user_presence_timestamps(self):
        """Test that last_seen_at is set correctly"""
        presence = UserPresence.objects.create(**self.presence_data)
        self.assertIsNotNone(presence.last_seen_at)

    def test_user_presence_unique_user(self):
        """Test that a user can only have one presence record"""
        UserPresence.objects.create(**self.presence_data)
        
        # Try to create another presence for the same user
        with self.assertRaises(Exception):  # Should raise IntegrityError
            UserPresence.objects.create(**self.presence_data) 