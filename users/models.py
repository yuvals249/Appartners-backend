from django.contrib.auth.hashers import make_password
from django.db import models
import uuid

from django.db.models.signals import post_delete
from django.dispatch import receiver


# Create your models here.
class LoginInfo(models.Model):
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    email = models.EmailField()
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
    phone_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Signal to delete LoginInfo when UserDetails is deleted
@receiver(post_delete, sender=UserDetails)
def delete_login_info(sender, instance, **kwargs):
    """
    Deletes the associated LoginInfo when a UserDetails record is deleted.
    """
    if instance.login_info:
        instance.login_info.delete()
