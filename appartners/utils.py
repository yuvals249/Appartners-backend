import jwt
import uuid
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from jwt import ExpiredSignatureError, InvalidTokenError
import logging

logger = logging.getLogger(__name__)

def generate_jwt(user, token_type='access'):
    """
    Generate a JWT token for the authenticated user.
    
    Args:
        user: The user object for which to generate a token
        token_type: Type of token ('access' or 'refresh')
        
    Returns:
        str: The encoded JWT token
    """
    # Create a unique token ID for tracking/revocation purposes
    jti = str(uuid.uuid4())
    
    # Set expiration based on token type
    if token_type == 'access':
        # Short-lived access token
        expiration = datetime.now() + timedelta(hours=1)
    else:  # refresh token
        # Long-lived refresh token for auto-login functionality
        expiration = datetime.now() + timedelta(days=180)
    
    payload = {
        'user_id': user.id,
        'email': user.email,
        'exp': expiration,  # Token expiration
        'iat': datetime.now(),  # Issued at
        'jti': jti,  # JWT ID for tracking/revocation
        'type': token_type  # Token type
    }
    
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


def generate_auth_tokens(user):
    """
    Generate both access and refresh tokens for a user.
    
    Args:
        user: The user object for which to generate tokens
        
    Returns:
        dict: Dictionary containing both tokens
    """
    access_token = generate_jwt(user, 'access')
    refresh_token = generate_jwt(user, 'refresh')
    
    return {
        'access': access_token,
        'refresh': refresh_token
    }


def decode_jwt(jwt_key, check_blacklist=True):
    """
    Decode a JWT token and extract user information.
    
    Args:
        jwt_key: The JWT token to decode
        check_blacklist: Whether to check if the token is blacklisted
        
    Returns:
        tuple: (user_id, email, token_type, jti)
        
    Raises:
        InvalidTokenError: If the token is blacklisted
    """
    payload = jwt.decode(jwt_key, settings.SECRET_KEY, algorithms=['HS256'])
    user_id = payload.get('user_id')
    email = payload.get('email')
    token_type = payload.get('type', 'access')  # Default to 'access' for backward compatibility
    jti = payload.get('jti')
    
    # Check if token is blacklisted
    if check_blacklist and jti:
        from users.models import BlacklistedToken
        
        try:
            if BlacklistedToken.objects.filter(token_jti=jti).exists():
                logger.warning(f"Attempt to use blacklisted token: {jti}")
                raise InvalidTokenError("Token has been blacklisted")
        except Exception as e:
            logger.error(f"Error checking token blacklist: {str(e)}")
            # Continue even if there's a database error
            pass
    
    return user_id, email, token_type, jti