"""
Token refresh views for the users app.
Handles refreshing of JWT tokens for auto-login functionality.
"""
import logging
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from appartners.utils import decode_jwt, generate_auth_tokens

logger = logging.getLogger(__name__)

class TokenRefreshView(APIView):
    authentication_classes = []  # No authentication required
    permission_classes = []  # No permissions required
    """
    API endpoint for refreshing JWT tokens.
    Allows clients to get a new access token using their refresh token.
    
    Endpoint: POST /api/v1/users/token/refresh/
    Request body:
        - refresh_token: The refresh token
    
    Returns:
        - 200: New access and refresh tokens
        - 401: Invalid refresh token
        - 404: User not found
    """
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Decode the refresh token
            user_id, email, token_type, jti = decode_jwt(refresh_token)
            
            # Verify this is a refresh token
            if token_type != 'refresh':
                logger.warning(f"Token refresh attempt with non-refresh token type: {token_type}")
                return Response(
                    {"error": "Invalid token type"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Get the user
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Generate new tokens
            tokens = generate_auth_tokens(user)
            
            # Return the new tokens
            return Response({
                "UserAuth": tokens['access'],
                "RefreshToken": tokens['refresh']
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )
