"""
Password validation utilities for the users app.
"""
from rest_framework import serializers


def validate_password(password):
    """
    Validate that the password:
    - Is at least 8 characters long
    - Contains at least one number
    - Contains at least one letter
    - Contains at least one uppercase letter
    
    Returns the password if valid, raises ValidationError if invalid.
    """
    if len(password) < 8:
        raise serializers.ValidationError("Password must be at least 8 characters long")
    
    if not any(char.isdigit() for char in password):
        raise serializers.ValidationError("Password must contain at least one number")
    
    if not any(char.isalpha() for char in password):
        raise serializers.ValidationError("Password must contain at least one letter")
    
    if not any(char.isupper() for char in password):
        raise serializers.ValidationError("Password must contain at least one uppercase letter")
    
    return password
