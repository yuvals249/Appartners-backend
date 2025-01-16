from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now


class UserPreferences(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incrementing ID field
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_preferences')
    city = models.CharField(max_length=40)
    min_price = models.IntegerField()
    max_price = models.IntegerField()
    move_in_date = models.DateField()
    number_of_roommates = models.IntegerField()

    def clean(self):
        # Ensure max_price >= min_price
        if self.min_price < 0:
            raise ValidationError("Minimum price must be greater than or equal to 0.")
        if self.max_price < 0:
            raise ValidationError("Maximum price must be greater than or equal to 0.")
        if self.min_price > self.max_price:
            raise ValidationError("Maximum price must be greater than or equal to minimum price.")

        # Ensure move_in_date is a future date
        if self.move_in_date <= now().date():
            raise ValidationError("Move-in date must be in the future.")

        # Ensure number_of_roommates >= 0
        if self.number_of_roommates < 0:
            raise ValidationError("Number of roommates must be greater than or equal to 0.")

    def save(self, *args, **kwargs):
        # Call full_clean to validate before saving
        self.full_clean()
        super().save(*args, **kwargs)
