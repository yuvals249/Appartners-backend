from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class UserPresence(models.Model):
    """
    Tracks user presence and last seen timestamp.
    
    This model stores information about when a user was last active on the platform.
    It is used to display "last seen" indicators in the chat interface.
    
    Attributes:
        user (ForeignKey): Reference to the User this presence record belongs to
            - Deleting a user will delete their presence record (CASCADE)
        last_seen_at (DateTimeField): Timestamp when the user was last active
            - Automatically updated whenever the user performs an action
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='presence')
    last_seen_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        """
        String representation of UserPresence.
        
        Returns:
            str: Format: "username last seen at datetime"
                Example: "john_doe last seen at 2023-01-01 12:00:00"
        """
        return f"{self.user.username} last seen at {self.last_seen_at}"
    
    def update_presence(self):
        """
        Updates the last_seen_at timestamp to the current time.
        """
        self.last_seen_at = timezone.now()
        self.save()