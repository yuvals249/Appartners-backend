"""
Views for updating user information.
"""
import logging
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import cloudinary.uploader

from users.utils.password_validation import validate_password

# Authentication now handled by middleware
from users.models import UserDetails
from users.serializers.user_details import UserDetailsSerializer

logger = logging.getLogger(__name__)


class UpdatePasswordView(APIView):
    """
    API endpoint for updating user password.
    
    Endpoint: PUT /api/v1/users/update-password/
    Request body:
        - current_password: User's current password
        - new_password: User's new password
    
    Returns:
        - 200: Password updated successfully
        - 400: Invalid input or validation error
        - 401: Current password is incorrect
        - 500: Server error
    """
    def put(self, request):
        if request.token_error:
            return request.token_error
            
        user_id = request.user_from_token
        # Get request data
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        
        # Validate input
        if not current_password or not new_password:
            return Response(
                {"error": "Current password and new password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Validate new password using our common validation utility
        try:
            validate_password(new_password)
        except serializers.ValidationError as e:
            return Response(
                {"error": str(e.detail[0]) if hasattr(e, 'detail') else str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Get the user
            user = User.objects.get(id=user_id)
            
            # Check if current password is correct
            if not user.check_password(current_password):
                return Response(
                    {"error": "Current password is incorrect"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
            # Update password
            user.set_password(new_password)
            user.save()
            
            return Response(
                {"message": "Password updated successfully"},
                status=status.HTTP_200_OK
            )
            
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating password: {str(e)}")
            return Response(
                {"error": "An error occurred while updating the password"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateUserDetailsView(APIView):
    """
    API endpoint for updating user details.
    
    Endpoint: PUT /api/v1/users/update-details/
    Request body (multipart/form-data):
        - first_name: User's first name (optional)
        - last_name: User's last name (optional)
        - occupation: User's occupation (optional)
        - about_me: User's bio (optional)
        - photo: Profile photo file (optional)
    
    Returns:
        - 200: User details updated successfully
        - 400: Invalid input or validation error
        - 404: User details not found
        - 500: Server error
    """
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def _delete_cloudinary_photo(self, public_id):
        """
        Helper method to delete a photo from Cloudinary.
        
        Args:
            public_id (str): The public ID of the photo to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            cloudinary.uploader.destroy(public_id)
            logging.info(f"Deleted photo with public_id: {public_id}")
            return True
        except Exception as e:
            # Log the error but don't fail the request
            logging.error(f"Failed to delete photo from Cloudinary: {str(e)}")
            return False
    
    def put(self, request):
        if request.token_error:
            return request.token_error
            
        user_id = request.user_from_token
        
        try:
            # Get the user and user details
            user = User.objects.get(id=user_id)
            user_details = UserDetails.objects.get(user=user)
            
            # Extract fields to update
            fields_to_update = {}
            
            # Check which fields are provided in the request
            if 'first_name' in request.data:
                fields_to_update['first_name'] = request.data.get('first_name')
                
            if 'last_name' in request.data:
                fields_to_update['last_name'] = request.data.get('last_name')
                
            if 'occupation' in request.data:
                fields_to_update['occupation'] = request.data.get('occupation')
                
            if 'about_me' in request.data:
                fields_to_update['about_me'] = request.data.get('about_me')
            
            # Store old photo public_id if it exists and we're uploading a new photo
            old_photo_public_id = None
            if 'photo' in request.FILES and user_details.photo:
                # Get the public ID from the CloudinaryField
                old_photo_public_id = user_details.photo.public_id
                
            # Handle photo upload
            if 'photo' in request.FILES:
                fields_to_update['photo'] = request.FILES.get('photo')
                
            # If no fields to update, return error
            if not fields_to_update:
                return Response(
                    {"error": "No fields to update provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Update user details
            with transaction.atomic():
                for field, value in fields_to_update.items():
                    setattr(user_details, field, value)
                user_details.save()
                
                # Delete old photo from Cloudinary if we uploaded a new one
                if old_photo_public_id:
                    self._delete_cloudinary_photo(old_photo_public_id)
                
            # Return updated user details
            serializer = UserDetailsSerializer(user_details)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except UserDetails.DoesNotExist:
            return Response(
                {"error": "User details not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating user details: {str(e)}")
            return Response(
                {"error": "An error occurred while updating user details"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
