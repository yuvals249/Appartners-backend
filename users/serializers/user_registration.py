from rest_framework import serializers
from django.contrib.auth.models import User
from users.models.user_details import UserDetails
import re


class UserRegistrationSerializer(serializers.Serializer):
    # User model fields
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    # UserDetails model fields
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    gender = serializers.ChoiceField(choices=['Male', 'Female', 'Other'], required=True)
    occupation = serializers.CharField(required=True)
    birth_date = serializers.DateField(required=True)
    preferred_city = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    about_me = serializers.CharField(required=False, allow_blank=True)
    photo = serializers.ImageField(required=True)
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    def validate_phone_number(self, value):
        if UserDetails.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already exists")
        return value
    
    def validate_password(self, value):
        """
        Validate that the password:
        - Is at least 8 characters long
        - Contains at least one number
        - Contains at least one letter
        - Contains at least one uppercase letter
        """
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one number")
        
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError("Password must contain at least one letter")
        
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        
        return value
    
    def create(self, validated_data):
        # Extract User model data
        user_data = {
            'username': validated_data['email'],  # Using email as username
            'email': validated_data['email'],
            'password': validated_data['password']
        }
        
        # Extract UserDetails model data
        user_details_data = {
            'first_name': validated_data['first_name'],
            'last_name': validated_data['last_name'],
            'gender': validated_data['gender'],
            'occupation': validated_data['occupation'],
            'birth_date': validated_data['birth_date'],
            'preferred_city': validated_data['preferred_city'],
            'phone_number': validated_data['phone_number'],
            'about_me': validated_data.get('about_me', ''),
        }
        
        # Handle photo if provided
        if 'photo' in validated_data:
            user_details_data['photo'] = validated_data['photo']
        
        # Create User instance
        user = User.objects.create_user(**user_data)
        
        # Create UserDetails instance
        user_details = UserDetails.objects.create(user=user, **user_details_data)
        
        return {
            'user': user,
            'user_details': user_details
        }
