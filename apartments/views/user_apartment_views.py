"""
User-related apartment views for the apartments app.
"""
import logging
from django.db import DatabaseError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apartments.models import Apartment, ApartmentUserLike
from apartments.serializers.apartment import ApartmentSerializer
from appartners.utils import get_user_from_token

logger = logging.getLogger(__name__)


class UserApartmentsView(APIView):
    """
    API View to retrieve all apartments created by the authenticated user.
    """
    
    def get(self, request):
        # Add logging for request headers
        logger.info(f"Request headers: {request.headers}")
        
        # Extract user from token using centralized function
        success, result = get_user_from_token(request)
        if not success:
            logger.error(f"Authentication failed: {result.data if hasattr(result, 'data') else 'No error data'}")
            return result  # Return the error response
            
        user_id = result
        logger.info(f"Authenticated user_id: {user_id}")
        
        try:
            # Get all apartments created by this user
            apartments = Apartment.objects.filter(user_id=user_id).order_by('-created_at')
            logger.info(f"Found {apartments.count()} apartments for user {user_id}")
            
            if not apartments.exists():
                return Response(
                    {
                        "message": "You haven't created any apartments yet",
                        "apartments": []
                    },
                    status=status.HTTP_200_OK
                )
                
            serializer = ApartmentSerializer(apartments, many=True)
            return Response(
                {
                    "message": "Apartments retrieved successfully",
                    "apartments": serializer.data
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error in UserApartmentsView: {str(e)}")
            return Response(
                {"error": "An error occurred while fetching data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserLikedApartmentsView(APIView):
    """
    API View to retrieve all apartments liked by the authenticated user.
    """
    
    def get(self, request):
        # Extract user from token using centralized function
        success, result = get_user_from_token(request)
        if not success:
            return result  # Return the error response
            
        user_id = result
        
        try:
            # Get all apartment IDs that the user has liked
            liked_apartment_ids = ApartmentUserLike.objects.filter(
                user_id=user_id, 
                like=True
            ).values_list('apartment_id', flat=True)
            
            # Get the actual apartments
            liked_apartments = Apartment.objects.filter(id__in=liked_apartment_ids).order_by('-created_at')
            
            if not liked_apartments.exists():
                return Response(
                    {"message": "You haven't liked any apartments yet"},
                    status=status.HTTP_200_OK
                )
                
            serializer = ApartmentSerializer(liked_apartments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except DatabaseError:
            return Response(
                {"error": "An error occurred while fetching data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
