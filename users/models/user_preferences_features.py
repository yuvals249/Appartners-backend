from django.db import models
import uuid

from .user_preferences import UserPreferences
from apartments.models import Feature


class UserPreferencesFeatures(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id = models.AutoField(primary_key=True)  # Auto-incrementing ID field
    user_preferences = models.ForeignKey(UserPreferences, on_delete=models.CASCADE, related_name="user_preference_features")
    # feature = models.ForeignKey(Feature, on_delete=models.CASCADE, related_name="feature_user_preferences")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_preferences.id} - {self.feature.name}"
