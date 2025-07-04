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

logger = logging.getLogger(__name__)


class ApartmentRecommendationView(APIView):
    """
    API View to retrieve apartments recommended for the authenticated user
    based on their preferences, up to a specified limit.
    """
    
    def get(self, request):
        if request.token_error:
            return request.token_error
            
        user_id = request.user_from_token
        
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
            # Now returns both apartments and compatibility scores
            recommended_apartments, compatibility_scores = get_recommended_apartments(user_id, limit)
            
            if not recommended_apartments.exists():
                return Response(
                    {
                        "message": "No matching apartments found based on your preferences",
                        "apartments": []
                    },
                    status=status.HTTP_200_OK
                )
                
            serializer = ApartmentSerializer(recommended_apartments, many=True)
            apartments_data = serializer.data
            
            # Add compatibility scores to each apartment (multiply by 100 to get percentage)
            for i, apartment in enumerate(apartments_data):
                if i < len(compatibility_scores):
                    # Convert score to percentage (0-100) and round to integer
                    apartments_data[i]['compatibility_score'] = round(compatibility_scores[i] * 100)
            
            return Response(
                {
                    "message": "Recommended apartments retrieved successfully",
                    "apartments": apartments_data
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
