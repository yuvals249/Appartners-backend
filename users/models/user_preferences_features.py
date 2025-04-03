from django.db import models
import uuid

from .user_preferences import UserPreferences
from apartments.models import Feature


class UserPreferencesFeatures(models.Model):
    """
    This model represents the many-to-many relationship between user preferences and features.
    Each instance links a specific user preference with a specific feature.
    """
    id = models.AutoField(primary_key=True)  # Auto-incrementing ID field
    user_preferences = models.ForeignKey(UserPreferences, on_delete=models.CASCADE, related_name="user_preference_features")
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, related_name="feature_user_preferences")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) # hello im yuval the bitch

    def __str__(self):
        return f"{self.user_preferences.id} - {self.feature.name}"
