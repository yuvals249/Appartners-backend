from django.db import models
from django.contrib.auth.models import User
import random
import string
from datetime import datetime, timedelta


class OTP(models.Model):
    """
    One-Time Password model for password reset functionality.
    Can work with either a User object or just an email address.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps', null=True, blank=True)
    email = models.EmailField(null=True, blank=True)  # For email-only OTPs
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "OTP"
        verbose_name_plural = "OTPs"
    
    @classmethod
    def generate_otp(cls, user=None, email=None):
        """
        Generate a new OTP for the user or email and save it to the database.
        Invalidates any existing unused OTPs for the user/email.
        
        Args:
            user: The user for whom to generate an OTP (optional)
            email: Email address for email-only OTP (optional)
            
        Returns:
            str: The generated OTP code
        """
        if not user and not email:
            raise ValueError("Either user or email must be provided")
            
        # Invalidate any existing OTPs for this user/email
        if user:
            cls.objects.filter(user=user, is_used=False).update(is_used=True)
        else:
            cls.objects.filter(email=email, is_used=False).update(is_used=True)
        
        # Generate a random 6-digit OTP
        otp_code = ''.join(random.choices(string.digits, k=6))
        
        # Set expiration time (5 minutes from now)
        expires_at = datetime.now() + timedelta(minutes=5)
        
        # Create and save the OTP
        otp = cls(user=user, email=email, otp_code=otp_code, expires_at=expires_at)
        otp.save()
        
        return otp_code
    
    @classmethod
    def verify_otp(cls, otp_code, user=None, email=None):
        """
        Verify if the provided OTP is valid for the user or email.
        
        Args:
            otp_code: The OTP code to verify
            user: The user for whom to verify the OTP (optional)
            email: Email address for email-only OTP (optional)
            
        Returns:
            bool: True if OTP is valid, False otherwise
        """
        if not user and not email:
            raise ValueError("Either user or email must be provided")
            
        try:
            # Get the latest unused OTP for the user/email
            if user:
                otp = cls.objects.filter(
                    user=user,
                    otp_code=otp_code,
                    is_used=False,
                    expires_at__gt=datetime.now()
                ).latest('created_at')
            else:
                otp = cls.objects.filter(
                    email=email,
                    otp_code=otp_code,
                    is_used=False,
                    expires_at__gt=datetime.now()
                ).latest('created_at')
            
            # Mark OTP as used
            otp.is_used = True
            otp.save()
            
            return True
        except cls.DoesNotExist:
            return False
