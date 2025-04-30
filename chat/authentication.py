from rest_framework import authentication
from rest_framework import exceptions
from appartners.utils import decode_jwt
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

class JWTAuthentication(authentication.BaseAuthentication):
    """
    Custom JWT authentication class for Django REST Framework.
    
    This class implements token-based authentication using JWT (JSON Web Tokens).
    It validates the token from the Authorization header and authenticates the user
    based on the token's payload.

    Authentication Process:
    1. Extracts the JWT token from the Authorization header
    2. Decodes the token to get user_id and email
    3. Retrieves the corresponding user from the database
    
    Usage:
        Add this class to REST_FRAMEWORK's DEFAULT_AUTHENTICATION_CLASSES in settings.py:
        REST_FRAMEWORK = {
            'DEFAULT_AUTHENTICATION_CLASSES': [
                'chat.authentication.JWTAuthentication',
            ],
        }
    """

    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).

        Args:
            request: The incoming request object containing the Authorization header

        Returns:
            tuple: A tuple of (user, None) if authentication succeeds
            None: If no token is provided (allowing other authentication methods to proceed)

        Raises:
            AuthenticationFailed: If the token is invalid or the user doesn't exist
        """
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            # Return None to allow other authentication methods to proceed
            return None

        try:
            # Extract the token from the Authorization header
            token = auth_header.split(' ')[1]
            logger.info(f"Attempting to authenticate with token: {token[:10]}...")
            
            # Decode the JWT token to get user information
            user_id, email = decode_jwt(token)
            logger.info(f"Decoded user_id: {user_id}, email: {email}")
            
            # Retrieve the user from the database
            user = User.objects.get(id=user_id)
            return (user, None)
        except Exception as e:
            # Log the error and raise authentication failure
            logger.error(f"Authentication failed: {str(e)}")
            raise exceptions.AuthenticationFailed('Invalid token')