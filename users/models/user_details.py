from django.contrib.auth.models import User
from django.db import models
from cloudinary.models import CloudinaryField


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
