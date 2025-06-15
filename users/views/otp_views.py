"""
OTP-related views for the users app.
Handles sending and verifying OTPs for various purposes.
"""
import logging
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.conf import settings
import jwt

from users.models import OTP

logger = logging.getLogger(__name__)


class SendOTPView(APIView):
    """
    API endpoint for sending OTP to user's email.
    
    Endpoint: POST /api/v1/users/otp/send/
    Request body:
        - email: User's email to send OTP to
        - purpose: Purpose of the OTP (e.g., 'password_reset', 'email_verification')
    
    Returns:
        - 200: OTP sent successfully
        - 404: User with the provided email not found
        - 500: Server error
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response(
                {"error": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Check if user exists with the provided email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {"error": "No user found with this email address"},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            # Generate OTP for the user
            otp_code = OTP.generate_otp(user)
            
            # Send OTP to user's email
            subject = "Your OTP for Appartners app"
            message = f"Hi {user.first_name.upper()},\nYour OTP for Appartners app is: {otp_code}.\nThis OTP is valid for 5 minutes."
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]
            
            try:
                send_mail(subject, message, from_email, recipient_list)
                logger.info(f"OTP email sent to {email}")
            except Exception as e:
                # Log the error but don't fail - in development, emails might not be configured
                logger.warning(f"Failed to send OTP email: {str(e)}")
                # Print the OTP to console for development purposes
                print(f"\n[DEV MODE] OTP for {email}: {otp_code}\n")
            
            logger.info(f"OTP sent to: {email}")
            
            return Response(
                {"message": "OTP sent to your email"},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error in SendOTPView: {str(e)}")
            return Response(
                {"error": "An error occurred while sending OTP"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyOTPView(APIView):
    """
    API endpoint for verifying OTP and generating a token.
    
    Endpoint: POST /api/v1/users/otp/verify/
    Request body:
        - email: User's email
        - otp_code: OTP code to verify

    Returns:
        - 200: OTP verified successfully (with token)
        - 400: Invalid OTP
        - 404: User not found
        - 500: Server error
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request):
        email = request.data.get('email')
        otp_code = request.data.get('otp_code')

        if not email or not otp_code:
            return Response(
                {"error": "Email and OTP code are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Check if user exists with the provided email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {"error": "No user found with this email address"},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            # Verify OTP
            if not OTP.verify_otp(user, otp_code):
                return Response(
                    {"error": "Invalid or expired OTP"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Generate a special token
            payload = {
                'user_id': user.id,
                'email': user.email,
                'exp': timezone.now() + timezone.timedelta(minutes=15),  # Token valid for 15 minutes
            }
            
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            
            logger.info(f"Token generated for user: {email}")
            
            return Response(
                {"token": token},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error in VerifyOTPView: {str(e)}")
            return Response(
                {"error": "An error occurred while verifying OTP"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
