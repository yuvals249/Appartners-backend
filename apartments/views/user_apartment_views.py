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

logger = logging.getLogger(__name__)


class UserApartmentsView(APIView):
    """
    API View to retrieve all apartments created by the authenticated user.
    """
    
    def get(self, request):
        # Return error if authentication failed
        if request.token_error:
            return request.token_error
            
        # Get user_id from the request (set by middleware)
        user_id = request.user_from_token
        
        try:
            # Get all apartments created by this user
            apartments = Apartment.objects.filter(user_id=user_id).order_by('-created_at')
            
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
        if request.token_error:
            return request.token_error
            
        user_id = request.user_from_token
        
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
