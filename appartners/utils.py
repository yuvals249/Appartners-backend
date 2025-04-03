import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from jwt import ExpiredSignatureError, InvalidTokenError
import logging

logger = logging.getLogger(__name__)

def generate_jwt(user):
    """
    Generate a JWT token for the authenticated user.
    """
    payload = {
        'user_id': user.id,
        'email': user.email,
        'exp': datetime.now() + timedelta(minutes=30),  # Token expiration
        'iat': datetime.now(),  # Issued at
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


def decode_jwt(jwt_key):
    """
    Generate a JWT token for the authenticated user.
    """
    payload = jwt.decode(jwt_key, settings.SECRET_KEY, algorithms=['HS256'])
    user_id = payload.get('user_id')
    email = payload.get('email')
    return user_id, email


def get_user_from_token(request):
    """
    Extract user_id from the Authorization header token.
    
    Args:
        request: The request object containing the Authorization header
        
    Returns:
        tuple: (success, user_id or error_response)
            - If successful: (True, user_id)
            - If failed: (False, Response object with error)
    """
    auth_header = request.headers.get('Authorization')
    logger.info(f"Authorization header: {auth_header}")
    
    if not auth_header or not auth_header.startswith('Bearer '):
        logger.error("Missing or invalid Authorization header format")
        return False, Response(
            {"error": "Authorization token required"},
            status=status.HTTP_401_UNAUTHORIZED
        )
        
    try:
        token = auth_header.split(' ')[1]
        logger.info(f"Extracted token: {token[:10]}...")  # Log only first 10 chars for security
        
        user_id, email = decode_jwt(token)
        logger.info(f"Decoded user_id: {user_id}, email: {email}")
        
        return True, user_id
    except (ExpiredSignatureError, InvalidTokenError) as e:
        logger.error(f"Token validation error: {str(e)}")
        return False, Response(
            {"error": "Invalid or expired token"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_user_from_token: {str(e)}")
        return False, Response(
            {"error": "Authentication error"},
            status=status.HTTP_400_BAD_REQUEST
        )
