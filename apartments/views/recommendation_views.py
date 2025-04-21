"""
Apartment recommendation views for the apartments app.
"""
import logging
from django.db import DatabaseError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apartments.serializers.apartment import ApartmentSerializer
from apartments.utils.recommendation import get_recommended_apartments
from appartners.utils import get_user_from_token

logger = logging.getLogger(__name__)


class ApartmentRecommendationView(APIView):
    """
    API View to retrieve apartments recommended for the authenticated user
    based on their preferences, up to a specified limit.
    """
    
    def get(self, request):
        # Extract user from token using centralized function
        success, result = get_user_from_token(request)
        if not success:
            return result  # Return the error response
            
        user_id = result
        
        # Get the limit parameter from the query string
        try:
            limit = int(request.query_params.get('limit', 10))
            if limit <= 0:
                return Response(
                    {"error": "Limit must be a positive integer"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {"error": "Limit must be a valid integer"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Get recommended apartments using the utility function
            recommended_apartments = get_recommended_apartments(user_id, limit)
            
            if not recommended_apartments.exists():
                return Response(
                    {
                        "message": "No matching apartments found based on your preferences",
                        "apartments": []
                    },
                    status=status.HTTP_200_OK
                )
                
            serializer = ApartmentSerializer(recommended_apartments, many=True)
            return Response(
                {
                    "message": "Recommended apartments retrieved successfully",
                    "apartments": serializer.data
                },
                status=status.HTTP_200_OK
            )
            
        except DatabaseError:
            logger.error(f"Database error in ApartmentRecommendationView for user {user_id}")
            return Response(
                {"error": "An error occurred while fetching recommendations"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Error in ApartmentRecommendationView: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
