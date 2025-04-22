from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now

from apartments.models import City


class UserPreferences(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incrementing ID field
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="city_user_preferences")
    move_in_date = models.DateField(null=True, blank=True)
    number_of_roommates = models.IntegerField(null=True, blank=True)
    min_price = models.IntegerField(null=True, blank=True)
    max_price = models.IntegerField(null=True, blank=True)
    max_floor = models.IntegerField(null=True, blank=True, help_text="Maximum floor preference (optional)")
    area = models.CharField(max_length=100, null=True, blank=True, help_text="Preferred neighborhood or area")

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_preferences')

    def clean(self):
        # Ensure max_price >= min_price if both are provided
        if self.min_price is not None and self.min_price < 0:
            raise ValidationError("Min price cannot be negative")
        if self.max_price is not None and self.max_price < 0:
            raise ValidationError("Max price cannot be negative")
        if self.min_price is not None and self.max_price is not None and self.max_price < self.min_price:
            raise ValidationError("Max price must be greater than or equal to min price")

        # Ensure move_in_date is a future date if provided
        if self.move_in_date is not None and self.move_in_date <= now().date():
            raise ValidationError("Move-in date must be in the future.")

        # Ensure number_of_roommates >= 0 if provided
        if self.number_of_roommates is not None and self.number_of_roommates < 0:
            raise ValidationError("Number of roommates must be greater than or equal to 0.")
            
        # Validate max_floor if provided
        if self.max_floor is not None and self.max_floor < 0:
            raise ValidationError("Maximum floor must be greater than or equal to 0.")

    def save(self, *args, **kwargs):
        # Call full_clean to validate before saving
        self.full_clean()
        super().save(*args, **kwargs)