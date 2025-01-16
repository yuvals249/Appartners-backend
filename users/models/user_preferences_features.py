from django.db import models
import uuid

from .user_preferences import UserPreferences
from apartments.models import Feature


class UserPreferencesFeatures(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_preferences = models.ForeignKey(UserPreferences, on_delete=models.CASCADE, related_name="user_preference_features")
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, related_name="feature_users")