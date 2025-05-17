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