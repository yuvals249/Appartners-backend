import uuid
import logging
from django.db import models
from cloudinary.models import CloudinaryField
import cloudinary.uploader

from apartments.models import Apartment


class ApartmentPhoto(models.Model):
    """
    This model represents photos associated with an apartment.
    Each photo is linked to a specific apartment.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name="photos")
    photo = CloudinaryField('image', folder='apartments/photos')

    def __str__(self):
        return f"Photo for Apartment {self.apartment.id}"
        
    def delete(self, *args, **kwargs):
        """Override delete method to also delete the photo from Cloudinary"""
        try:
            # Get the public ID before deleting the model instance
            if self.photo and self.photo.public_id:
                public_id = self.photo.public_id
                # Delete the photo from Cloudinary
                cloudinary.uploader.destroy(public_id)
                logging.info(f"Deleted apartment photo with public_id: {public_id}")
        except Exception as e:
            # Log the error but continue with the deletion
            logging.error(f"Failed to delete photo from Cloudinary: {str(e)}")
        
        # Call the parent class's delete method to delete the model instance
        super().delete(*args, **kwargs)
