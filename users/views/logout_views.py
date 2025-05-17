"""
Logout views for the users app.
Handles user logout functionality by invalidating tokens.
"""
import logging
from datetime import datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from jwt import InvalidTokenError
import jwt
from appartners.utils import decode_jwt
from users.models import BlacklistedToken

logger = logging.getLogger(__name__)

class LogoutView(APIView):
    """
    API endpoint for user logout.
    Invalidates the user's tokens.
    
    Endpoint: POST /api/v1/authenticate/logout/
    Request body:
        - refresh_token: The refresh token to invalidate
    
    Returns:
        - 200: Logout successful
        - 400: Bad request (missing token)
        - 401: Unauthorized (invalid token)
    """
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Decode the token without checking the blacklist (we're adding it to the blacklist)
            user_id, email, token_type, jti = decode_jwt(refresh_token, check_blacklist=False)
            
            # Verify this is a refresh token
            if token_type != 'refresh':
                return Response(
                    {"error": "Invalid token type. Only refresh tokens can be invalidated."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get token expiration from payload
            payload = jwt.decode(refresh_token, options={"verify_signature": False})
            exp = payload.get('exp')
            
            if not jti:
                return Response(
                    {"error": "Token does not have a JTI (JWT ID)"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Add the token to the blacklist
            BlacklistedToken.objects.create(
                token_jti=jti,
                user_id=user_id,
                expires_at=datetime.fromtimestamp(exp) if exp else None
            )
            
            logger.info(f"User {user_id} logged out successfully. Token {jti[:10]}... blacklisted.")
            
            return Response(
                {"message": "Logged out successfully"},
                status=status.HTTP_200_OK
            )
            
        except InvalidTokenError as e:
            logger.warning(f"Invalid token in logout attempt: {str(e)}")
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")
            return Response(
                {"error": "An error occurred during logout"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
