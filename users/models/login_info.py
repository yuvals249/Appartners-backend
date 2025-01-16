import uuid

from django.contrib.auth.hashers import make_password
from django.db import models


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