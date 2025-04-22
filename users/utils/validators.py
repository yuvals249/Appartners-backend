import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def validate_and_normalize_email(email):
    """
    Validates that the email is in the correct format and normalizes it to lowercase.
    
    Args:
        email (str): The email to validate and normalize
        
    Returns:
        tuple: (is_valid, normalized_email, error_message)
    """
    if not email:
        return False, None, "Email is required"
        
    # Convert to lowercase
    normalized_email = email.lower().strip()
    
    # Validate email format
    try:
        validate_email(normalized_email)
        return True, normalized_email, None
    except ValidationError:
        return False, None, "Invalid email format"

def validate_and_normalize_phone(phone):
    """
    Validates that the phone number is in the correct format (0XXXXXXXXX) and normalizes it.
    
    Args:
        phone (str): The phone number to validate and normalize
        
    Returns:
        tuple: (is_valid, normalized_phone, error_message)
    """
    if not phone:
        return False, None, "Phone number is required"
    
    # Remove any non-digit characters
    normalized_phone = re.sub(r'\D', '', phone)
    
    # Check if the phone number is in the correct format (0XXXXXXXXX)
    if not re.match(r'^0\d{9}$', normalized_phone):
        return False, None, "Phone number must be in format 0XXXXXXXXX"
    
    return True, normalized_phone, None
