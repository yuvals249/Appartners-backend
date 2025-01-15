import uuid
from datetime import date
from django.core.exceptions import ValidationError
from django.db import models

from apartments.models import City


class Apartment(models.Model):
    """
    Model representing an apartment.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="apartments")
    street = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    house_number = models.CharField(max_length=10)
    floor = models.IntegerField()
    number_of_rooms = models.IntegerField()
    number_of_available_rooms = models.IntegerField()
    total_price = models.DecimalField(max_digits=6, decimal_places=2)
    available_entry_date = models.DateField()
    about = models.TextField(null=True, blank=True)

    def clean(self):
        """
        Custom validations for cross-field constraints and field-level rules.
        """
        # Cross-field validation: number_of_available_rooms <= number_of_rooms
        if self.number_of_available_rooms > self.number_of_rooms:
            raise ValidationError(
                {'number_of_available_rooms': "Cannot exceed the total number of rooms."}
            )

        # Validation for available_entry_date
        if self.available_entry_date <= date.today():
            raise ValidationError(
                {'available_entry_date': "Available entry date must be in the future."}
            )

        # Ensure street has a reasonable length (this is already enforced by max_length)
        if len(self.street) > 50:
            raise ValidationError({'street': "Street name cannot exceed 50 characters."})

        # Ensure house number meets pattern rules
        if len(self.house_number) > 10:
            raise ValidationError({'house_number': "House number cannot exceed 10 characters."})

    def __str__(self):
        return f'{self.city} {self.street} {self.house_number}'
