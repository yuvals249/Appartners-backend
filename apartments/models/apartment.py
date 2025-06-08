import uuid
from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User

from apartments.models import City


class Apartment(models.Model):
    """
    Model representing an apartment.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="apartments", null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="apartments", db_index=True)
    street = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    floor = models.IntegerField()
    number_of_rooms = models.IntegerField()
    number_of_available_rooms = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    available_entry_date = models.DateField()
    about = models.TextField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    area = models.CharField(max_length=100, null=True, blank=True)
    is_yad2 = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """
        Enforce model validation before saving.
        """
        self.full_clean()  # This calls the clean method and raises ValidationError if validation fails
        super().save(*args, **kwargs)

    def clean(self):
        """
        Custom validations for cross-field constraints and field-level rules.
        """
        if not self.type.isalpha():
            raise ValidationError({'type': 'Must contain only letters'})

        if self.floor <= 0 or self.floor > 100:
            raise ValidationError({'floor': 'Must be a valid integer'})

        if self.number_of_rooms <= 0 or self.number_of_rooms > 10:
            raise ValidationError({'number_of_rooms': 'Must be a valid integer'})
            
        # Remove trailing apostrophe from area names if it exists
        if self.area and self.area.endswith("'"):
            self.area = self.area[:-1]

        if self.number_of_available_rooms <= 0:
            raise ValidationError({'number_of_available_rooms': 'Must be a positive integer'})

        if self.number_of_available_rooms > self.number_of_rooms:
            raise ValidationError({'number_of_available_rooms': "Cannot exceed the total number of rooms"})

        if self.total_price <= 0:
            raise ValidationError({'total_price': 'Must be a positive decimal'})

        if self.about and len(self.about) > 1000:
            raise ValidationError({'about': 'Must not exceed 1000 characters'})

        if self.available_entry_date <= date.today():
            raise ValidationError({'available_entry_date': "Must be in the future"})

    def __str__(self):
        return f"{self.street}, {self.city.name} - {self.number_of_rooms} rooms"
