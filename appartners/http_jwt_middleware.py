"""
Middleware for JWT authentication in HTTP requests.
"""
import logging
import jwt
from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from jwt import ExpiredSignatureError, InvalidTokenError
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

class JWTAuthMiddleware:
    """
    Middleware for JWT authentication in HTTP requests.
    
    This middleware extracts the JWT token from the Authorization header,
    decodes it, and sets the authenticated user and user_id in the request object.
    
    After this middleware runs:
    - request.user_from_token will contain the user_id if authentication was successful
    - request.token_error will contain an error response if authentication failed
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Process token authentication before the view is called
        self._authenticate_token(request)
        
        # Continue with the request
        response = self.get_response(request)
        
        return response
        
    def _authenticate_token(self, request):
        """
        Extract user_id from the Authorization header token and add it to the request.
        
        This sets:
        - request.user_from_token: The user ID if authentication was successful
        - request.token_error: An error response if authentication failed
        """
        # Skip authentication for paths that don't need it
        if any(path in request.path for path in ['/admin/', '/static/', '/media/']):
            return
        
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            logger.warning(f"Missing or invalid Authorization header for request to: {request.path}. Header: {auth_header if auth_header else 'None'}")
            request.user_from_token = None
            request.token_error = Response(
                {"error": "Authorization token required"},
                status=status.HTTP_401_UNAUTHORIZED
            )
            return
            
        try:
            token = auth_header.split(' ')[1]
            
            # Only log token info once per request
            if not hasattr(request, '_token_logged'):
                logger.debug(f"Processing token: {token[:10]}...")  # Log only first 10 chars for security
                request._token_logged = True
            
            # Decode the token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            # Set user_id in request for easy access in views
            request.user_from_token = user_id
            request.token_error = None
            
        except (ExpiredSignatureError, InvalidTokenError) as e:
            logger.warning(f"Invalid or expired token for request to: {request.path}. Error: {str(e)}")
            request.user_from_token = None
            request.token_error = Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            logger.error(f"Unexpected error in JWT authentication: {str(e)}")
            request.user_from_token = None
            request.token_error = Response(
                {"error": "Authentication error"},
                status=status.HTTP_400_BAD_REQUEST
            )
