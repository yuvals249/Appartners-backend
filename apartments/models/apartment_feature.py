import uuid
from django.db import models
from apartments.models import Apartment, Feature


class ApartmentFeature(models.Model):
    """
    This model represents the many-to-many relationship between apartments and features.
    Each instance links a specific apartment with a specific feature.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name="apartment_features")
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, related_name="feature_apartments")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['apartment', 'feature'],
                name='unique_apartment_feature'
            )
        ]

    def __str__(self):
        return f"{self.apartment.id} - {self.feature.name}"
