import uuid
from django.db import models

from apartments.models import Apartment


class ApartmentPhoto(models.Model):
    """
    This model represents photos associated with an apartment.
    Each photo is linked to a specific apartment.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name="photos")
    photo = models.ImageField(upload_to='apartments/photos')

    def __str__(self):
        return f"Photo for Apartment {self.apartment.id}"
