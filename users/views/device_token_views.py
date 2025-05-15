"""
Views for managing device tokens for push notifications.
"""
import logging
from django.db import DatabaseError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from appartners.utils import get_user_from_token
from users.models import DeviceToken

logger = logging.getLogger(__name__)


class DeviceTokenView(APIView):
    """
    API endpoint for registering and managing device tokens for push notifications.
    
    Endpoint: POST /api/v1/users/device-token/
    Request body:
        - token: FCM device token
        - device_type: Device type (android, ios, web)
    
    Returns:
        - 201: Token registered successfully
        - 400: Invalid input
        - 500: Server error
    """
    def post(self, request):
        # Add debug logging
        logger.info(f"Device token registration request received: {request.data}")
        
        # Extract user from token
        success, result = get_user_from_token(request)
        if not success:
            logger.error(f"Failed to get user from token: {result}")
            return result  # Return the error response
        user_id = result
        logger.info(f"User ID extracted: {user_id}")
        
        # Get request data
        token = request.data.get('token')
        device_type = request.data.get('device_type')
        logger.info(f"Token: {token}, Device Type: {device_type}")
        
        # Validate input
        if not token:
            return Response(
                {"error": "Device token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if not device_type or device_type not in ['android', 'ios', 'web']:
            return Response(
                {"error": "Valid device type is required (android, ios, web)"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Create or update the device token
            logger.info(f"Attempting to update or create device token for user_id: {user_id}")
            device_token, created = DeviceToken.objects.update_or_create(
                token=token,
                defaults={
                    'user_id': user_id,
                    'device_type': device_type,
                    'is_active': True
                }
            )
            logger.info(f"Device token {'created' if created else 'updated'}: {device_token.id}")
            
            action = "registered" if created else "updated"
            response_data = {"message": f"Device token {action} successfully", "token_id": device_token.id}
            logger.info(f"Success response: {response_data}")
            return Response(
                response_data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )
            
        except DatabaseError as e:
            logger.error(f"Database error registering device token: {str(e)}")
            return Response(
                {"error": "A database error occurred. Please try again later"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Error registering device token: {str(e)}")
            return Response(
                {"error": "An error occurred while registering the device token"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    def delete(self, request):
        """
        Delete a device token to stop receiving notifications.
        """
        # Extract user from token
        success, result = get_user_from_token(request)
        if not success:
            return result  # Return the error response
        user_id = result
        
        # Get request data
        token = request.data.get('token')
        
        # Validate input
        if not token:
            return Response(
                {"error": "Device token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Find and delete the token
            deleted, _ = DeviceToken.objects.filter(
                user_id=user_id,
                token=token
            ).delete()
            
            if deleted:
                return Response(
                    {"message": "Device token deleted successfully"},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "Device token not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
                
        except Exception as e:
            logger.error(f"Error deleting device token: {str(e)}")
            return Response(
                {"error": "An error occurred while deleting the device token"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
