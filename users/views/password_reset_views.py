"""
Password reset views for the users app.
Handles resetting password using OTP verification.
"""
import logging
from django.contrib.auth.models import User
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.conf import settings
import jwt
from users.utils.password_validation import validate_password

from appartners.utils import generate_auth_tokens

logger = logging.getLogger(__name__)


class ResetPasswordView(APIView):
    """
    API endpoint for resetting password using the reset token.
    
    Endpoint: POST /api/v1/users/password-reset/reset-password/
    Request body:
        - reset_token: Token received from verify-otp endpoint
        - new_password: New password to set
    
    Returns:
        - 200: Password reset successful (with new auth tokens)
        - 400: Invalid token or password
        - 500: Server error
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request):
        reset_token = request.data.get('reset_token')
        new_password = request.data.get('new_password')
        
        if not reset_token or not new_password:
            return Response(
                {"error": "Reset token and new password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Validate password using our common validation utility
        try:
            validate_password(new_password)
        except serializers.ValidationError as e:
            return Response(
                {"error": str(e.detail[0]) if hasattr(e, 'detail') else str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Decode and verify the reset token
            try:
                payload = jwt.decode(reset_token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = payload.get('user_id')
                user = User.objects.get(id=user_id)
                
            except (jwt.InvalidTokenError, User.DoesNotExist):
                return Response(
                    {"error": "Invalid or expired reset token"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Reset the password
            user.set_password(new_password)
            user.save()
            
            # Generate new auth tokens
            tokens = generate_auth_tokens(user)
            
            logger.info(f"Password reset successful for user: {user.email}")
            
            return Response(
                {
                    "message": "Password reset successful",
                    "UserAuth": tokens['access'],
                    "RefreshToken": tokens['refresh']
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error in ResetPasswordView: {str(e)}")
            return Response(
                {"error": "An error occurred while resetting password"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
