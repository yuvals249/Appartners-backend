"""
Model for blacklisted tokens.
Used to track invalidated JWT tokens for logout functionality.
"""
from django.db import models
import uuid


class BlacklistedToken(models.Model):
    """
    Model to store blacklisted (invalidated) JWT tokens.
    Tokens in this table are considered invalid and can't be used for authentication.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token_jti = models.CharField(max_length=255, unique=True, db_index=True)
    user_id = models.IntegerField(null=True)  # Optional reference to the user
    blacklisted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True)  # When the token would naturally expire
    
    class Meta:
        db_table = 'blacklisted_tokens'
        
    def __str__(self):
        return f"Blacklisted token {self.token_jti[:10]}... for user {self.user_id}"
