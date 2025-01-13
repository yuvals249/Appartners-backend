import uuid
from django.db import models


class Apartment(models.Model):
    """
    This module defines the models for the apartments application.
    It includes models for Apartment, ApartmentPhoto, and Feature.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    house_number = models.CharField(max_length=10)
    floor = models.IntegerField()
    number_of_rooms = models.IntegerField()
    number_of_available_rooms = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    available_entry_date = models.DateField()
    about = models.TextField()

    def __str__(self):
        return f"{self.city}, {self.street} ({self.type})"


class ApartmentPhoto(models.Model):
    """
    This model represents photos associated with an apartment.
    Each photo is linked to a specific apartment.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name="photos")
    photo = models.ImageField(upload_to='apartment_photos/')

    def __str__(self):
        return f"Photo for Apartment {self.apartment.id}"


class Feature(models.Model):
    """
    This model represents features that can be associated with an apartment.
    Each feature has a unique name and an active status.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=50)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ApartmentFeature(models.Model):
    """
    This model represents the many-to-many relationship between apartments and features.
    Each instance links a specific apartment with a specific feature.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name="apartment_features")
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, related_name="feature_apartments")

    def __str__(self):
        return f"{self.apartment.id} - {self.feature.name}"
