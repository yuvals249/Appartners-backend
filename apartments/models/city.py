import uuid
from django.db import models


class City(models.Model):
    """
    This model represents a city.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=50, unique=True)
    hebrew_name = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.name} {self.hebrew_name}'

