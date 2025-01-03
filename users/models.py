from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db import models
import uuid

from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.timezone import now


# Create your models here.
class LoginInfo(models.Model):
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Encrypted Password

    def save(self, *args, **kwargs):
        if not self.pk:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)


class UserDetails(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incrementing ID field
    login_info = models.ForeignKey(LoginInfo, on_delete=models.CASCADE, related_name='user_details')
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    occupation = models.CharField(max_length=200)
    birth_date = models.DateField()
    address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UserPreferences(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incrementing ID field
    login_info = models.ForeignKey(LoginInfo, on_delete=models.CASCADE, related_name='user_preferences')
    area = models.CharField(max_length=200)
    min_price = models.IntegerField()
    max_price = models.IntegerField()
    move_in_date = models.DateField()
    # TODO: Thing what to do with features
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


# Signal to delete LoginInfo when UserDetails is deleted
@receiver(post_delete, sender=UserDetails)
def delete_login_info(sender, instance, **kwargs):
    """
    Deletes the associated LoginInfo when a UserDetails record is deleted.
    """
    if instance.login_info:
        instance.login_info.delete()
