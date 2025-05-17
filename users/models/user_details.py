from django.contrib.auth.models import User
from django.db import models
import logging
from cloudinary.models import CloudinaryField
import cloudinary.uploader


class UserDetails(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incrementing ID field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_details')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    occupation = models.CharField(max_length=30)
    birth_date = models.DateField()
    preferred_city = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15, unique=True)
    about_me = models.TextField(null=True)
    photo = CloudinaryField('image', folder='users/photos', null=True)
    is_yad2 = models.BooleanField(default=False)
    
    def delete(self, *args, **kwargs):
        """Override delete method to also delete the photo from Cloudinary"""
        try:
            # Get the public ID before deleting the model instance
            if self.photo and self.photo.public_id:
                public_id = self.photo.public_id
                # Delete the photo from Cloudinary
                cloudinary.uploader.destroy(public_id)
                logging.info(f"Deleted user photo with public_id: {public_id}")
        except Exception as e:
            # Log the error but continue with the deletion
            logging.error(f"Failed to delete user photo from Cloudinary: {str(e)}")
        
        # Call the parent class's delete method to delete the model instance
        super().delete(*args, **kwargs)
