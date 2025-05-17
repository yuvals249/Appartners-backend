"""
Model for storing user-to-user likes/dislikes.
"""
import uuid
from django.db import models
from django.contrib.auth.models import User

class UserUserLike(models.Model):
    """
    Model to store when a user likes or dislikes another user.
    This is used when a user responds to someone who has liked their apartment.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # The user who is performing the like/dislike action
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='user_to_user_likes'
    )
    
    # The user who is being liked/disliked
    target_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='user_liked_by'
    )
    
    # Whether this is a like (True) or dislike (False)
    like = models.BooleanField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # Ensure a user can only like/dislike another user once
        # (they can update their preference, but not create multiple records)
        unique_together = ('user', 'target_user')
        
    def __str__(self):
        action = "likes" if self.like else "dislikes"
        return f"{self.user.email} {action} {self.target_user.email}"
