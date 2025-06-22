import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from faker import Faker

from users.models import UserUserLike

fake = Faker()

@pytest.mark.django_db
class TestUserUserLikeIntegration(TestCase):
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username=fake.email(),
            email=fake.email(),
            password='testpass123'
        )
        
        self.target_user = User.objects.create_user(
            username=fake.email(),
            email=fake.email(),
            password='testpass123'
        )
        
        self.like_data = {
            'user': self.user,
            'target_user': self.target_user,
            'like': True
        }

    def test_create_user_like_success(self):
        """Test successful user like creation"""
        user_like = UserUserLike.objects.create(**self.like_data)
        
        self.assertIsNotNone(user_like)
        self.assertEqual(user_like.user, self.user)
        self.assertEqual(user_like.target_user, self.target_user)
        self.assertTrue(user_like.like)

    def test_create_user_like_without_required_fields(self):
        """Test user like creation without required fields fails"""
        required_fields = ['user', 'target_user', 'like']
        
        for field in required_fields:
            data = self.like_data.copy()
            data.pop(field)
            with self.assertRaises(Exception):  # Should raise ValidationError or IntegrityError
                user_like = UserUserLike(**data)
                user_like.full_clean()
                user_like.save()

    def test_update_user_like_success(self):
        """Test successful user like update"""
        user_like = UserUserLike.objects.create(**self.like_data)
        
        # Update like status
        user_like.like = False
        user_like.save()
        
        # Refresh from database
        user_like.refresh_from_db()
        
        # Verify update
        self.assertFalse(user_like.like)

    def test_delete_user_like_success(self):
        """Test successful user like deletion"""
        user_like = UserUserLike.objects.create(**self.like_data)
        user_like.delete()
        
        self.assertFalse(UserUserLike.objects.filter(user=self.user, target_user=self.target_user).exists())

    def test_user_like_str_representation(self):
        """Test user like string representation"""
        user_like = UserUserLike.objects.create(**self.like_data)
        expected_str = f"{self.user.email} {'likes' if user_like.like else 'dislikes'} {self.target_user.email}"
        self.assertEqual(str(user_like), expected_str)

    def test_user_like_timestamps(self):
        """Test that created_at and updated_at are set correctly"""
        user_like = UserUserLike.objects.create(**self.like_data)
        
        self.assertIsNotNone(user_like.created_at)
        self.assertIsNotNone(user_like.updated_at)
        # Allow for small time differences due to database operations
        self.assertAlmostEqual(user_like.created_at.timestamp(), user_like.updated_at.timestamp(), delta=1)

    def test_user_like_unique(self):
        """Test that a user can only like another user once"""
        UserUserLike.objects.create(**self.like_data)
        
        # Try to create another like for the same user pair
        with self.assertRaises(Exception):  # Should raise ValidationError or IntegrityError
            user_like = UserUserLike(**self.like_data)
            user_like.full_clean()
            user_like.save()

    def test_user_like_bidirectional(self):
        """Test that likes can be bidirectional"""
        # User1 likes User2
        UserUserLike.objects.create(**self.like_data)
        
        # User2 likes User1
        reverse_like_data = {
            'user': self.target_user,
            'target_user': self.user,
            'like': True
        }
        
        reverse_like = UserUserLike.objects.create(**reverse_like_data)
        
        self.assertIsNotNone(reverse_like)
        self.assertEqual(reverse_like.user, self.target_user)
        self.assertEqual(reverse_like.target_user, self.user)
        self.assertTrue(reverse_like.like) 