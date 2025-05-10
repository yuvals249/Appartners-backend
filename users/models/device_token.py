from django.db import models
from django.contrib.auth.models import User


class DeviceToken(models.Model):
    """
    Model to store FCM device tokens for push notifications.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='device_tokens')
    token = models.CharField(max_length=255, unique=True)
    device_type = models.CharField(max_length=20, choices=[
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('web', 'Web')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'token')
        
    def __str__(self):
        return f"{self.user.email} - {self.device_type} - {self.token[:10]}..."
