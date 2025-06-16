import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from faker import Faker

from users.models import UserResponse, Question, QuestionnaireTemplate

fake = Faker()

@pytest.mark.django_db
class TestUserResponseIntegration(TestCase):
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username=fake.email(),
            email=fake.email(),
            password='testpass123'
        )
        
        self.questionnaire = QuestionnaireTemplate.objects.create(
            title='Test Questionnaire',
            description='A test questionnaire'
        )
        
        self.question = Question.objects.create(
            questionnaire=self.questionnaire,
            title='What is your favorite color?',
            question_type='text',
            placeholder='Enter your favorite color'
        )
        
        self.response_data = {
            'user': self.user,
            'question': self.question,
            'text_response': 'Blue',
            'numeric_response': None
        }

    def test_create_user_response_success(self):
        """Test successful user response creation"""
        user_response = UserResponse.objects.create(**self.response_data)
        
        self.assertIsNotNone(user_response)
        self.assertEqual(user_response.user, self.user)
        self.assertEqual(user_response.question, self.question)
        self.assertEqual(user_response.text_response, self.response_data['text_response'])
        self.assertEqual(user_response.numeric_response, self.response_data['numeric_response'])

    def test_create_user_response_without_required_fields(self):
        """Test user response creation without required fields fails"""
        required_fields = ['user', 'question']
        
        for field in required_fields:
            data = self.response_data.copy()
            data.pop(field)
            with self.assertRaises(Exception):  # Should raise ValidationError or IntegrityError
                UserResponse.objects.create(**data)

    def test_update_user_response_success(self):
        """Test successful user response update"""
        user_response = UserResponse.objects.create(**self.response_data)
        
        # Update response
        new_response = 'Red'
        user_response.text_response = new_response
        user_response.save()
        
        # Refresh from database
        user_response.refresh_from_db()
        
        # Verify update
        self.assertEqual(user_response.text_response, new_response)

    def test_delete_user_response_success(self):
        """Test successful user response deletion"""
        user_response = UserResponse.objects.create(**self.response_data)
        user_response.delete()
        
        self.assertFalse(UserResponse.objects.filter(user=self.user, question=self.question).exists())

    def test_user_response_multiple_answers(self):
        """Test that a user can answer multiple questions"""
        # Create another question
        another_question = Question.objects.create(
            questionnaire=self.questionnaire,
            title='What is your favorite number?',
            question_type='radio',
            options={'min': 1, 'max': 10}
        )
        
        # Create response for first question
        UserResponse.objects.create(**self.response_data)
        
        # Create response for second question
        another_response_data = {
            'user': self.user,
            'question': another_question,
            'text_response': None,
            'numeric_response': 7
        }
        UserResponse.objects.create(**another_response_data)
        
        # Verify both responses exist
        self.assertEqual(UserResponse.objects.filter(user=self.user).count(), 2)

    def test_user_response_str_representation(self):
        """Test user response string representation"""
        user_response = UserResponse.objects.create(**self.response_data)
        expected_str = f"{self.user.email} - {self.question.title[:30]}"
        self.assertEqual(str(user_response), expected_str)

    def test_user_response_timestamps(self):
        """Test user response timestamps"""
        response = UserResponse.objects.create(**self.response_data)
        self.assertIsNotNone(response.created_at)
        self.assertIsNotNone(response.updated_at)
        
        # Test updated_at changes on modification
        old_updated_at = response.updated_at
        response.text_response = 'Green'
        response.save()
        self.assertGreater(response.updated_at, old_updated_at)

    def test_user_response_required_validation(self):
        """Test user response required validation"""
        # Test empty text response for text type question
        data = self.response_data.copy()
        data['text_response'] = ''
        # Since there's no validation for required fields, this should pass
        response = UserResponse.objects.create(**data)
        self.assertEqual(response.text_response, '')
