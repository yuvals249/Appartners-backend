import uuid

from django.contrib.auth.models import User
from django.db import models
from apartments.models import Apartment


class ApartmentUserLike(models.Model):
    """
    This model represents the many-to-many relationship
     between apartments and users and their likes on them.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name="apartment_likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_likes")
    like = models.BooleanField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['apartment', 'user'],
                name='unique_apartment_user_like'
            )
        ]
