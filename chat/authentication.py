from rest_framework import authentication
from rest_framework import exceptions
from appartners.utils import decode_jwt
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        try:
            token = auth_header.split(' ')[1]
            logger.info(f"Attempting to authenticate with token: {token[:10]}...")
            user_id, email = decode_jwt(token)
            logger.info(f"Decoded user_id: {user_id}, email: {email}")
            user = User.objects.get(id=user_id)
            return (user, None)
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise exceptions.AuthenticationFailed('Invalid token')