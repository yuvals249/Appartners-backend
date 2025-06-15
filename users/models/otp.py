from django.db import models
from django.contrib.auth.models import User
import random
import string
from datetime import datetime, timedelta


class OTP(models.Model):
    """
    One-Time Password model for password reset functionality.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "OTP"
        verbose_name_plural = "OTPs"
    
    @classmethod
    def generate_otp(cls, user):
        """
        Generate a new OTP for the user and save it to the database.
        Invalidates any existing unused OTPs for the user.
        
        Args:
            user: The user for whom to generate an OTP
            
        Returns:
            str: The generated OTP code
        """
        # Invalidate any existing OTPs for this user
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Generate a random 6-digit OTP
        otp_code = ''.join(random.choices(string.digits, k=6))
        
        # Set expiration time (10 minutes from now)
        expires_at = datetime.now() + timedelta(minutes=5)
        
        # Create and save the OTP
        otp = cls(user=user, otp_code=otp_code, expires_at=expires_at)
        otp.save()
        
        return otp_code
    
    @classmethod
    def verify_otp(cls, user, otp_code):
        """
        Verify if the provided OTP is valid for the user.
        
        Args:
            user: The user for whom to verify the OTP
            otp_code: The OTP code to verify
            
        Returns:
            bool: True if OTP is valid, False otherwise
        """
        try:
            # Get the latest unused OTP for the user
            otp = cls.objects.filter(
                user=user,
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
