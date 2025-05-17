"""
User-related views for the users app.
"""
from django.db import DatabaseError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import UserDetails
from users.serializers import UserDetailsSerializer
from apartments.models import Feature, City
from apartments.serializers import CitySerializer, FeatureSerializer
from django.contrib.auth.models import User


class UserDetailsList(APIView):
    """
    View to list all user details.
    Requires authentication and staff privileges.
    """
    def get(self, request):
        if request.token_error:
            return request.token_error
            
        user_id = request.user_from_token
        
        try:
            user = User.objects.get(id=user_id)
            
            if not user.is_staff:
                return Response(
                    {"error": "You don't have permission to access this resource."},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            # If user is staff, return all user details
            user_details = UserDetails.objects.all()
            serializer = UserDetailsSerializer(user_details, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except DatabaseError:
            return Response(
                {"error": "A database error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CurrentUserView(APIView):
    """
    API endpoint for retrieving the current authenticated user's details.
    
    Endpoint: GET /api/v1/users/me/
    
    Returns:
        - 200: User details
        - 401: Unauthorized (invalid or missing token)
        - 404: User details not found
    """
    def get(self, request):
        # Check if there was a token error
        if request.token_error:
            return request.token_error
            
        # Get user ID from the token
        user_id = request.user_from_token
        
        try:
            # Get the user from the database
            user = User.objects.get(id=user_id)
            
            # Fetch the user's details from the UserDetails model
            try:
                user_details = UserDetails.objects.get(user=user)
            except UserDetails.DoesNotExist:
                return Response(
                    {"error": "User details not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Serialize the user details
            serializer = UserDetailsSerializer(user_details)
            
            # Return the user details
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error retrieving current user: {str(e)}")
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserPreferencesPayloadView(APIView):
    authentication_classes = []  # No authentication required
    permission_classes = []  # No permissions required
    """
    View to get payload data for user preferences form.
    Returns cities with their areas and apartment features.
    """
    def get(self, request):
        try:
            # Get all active cities
            cities = City.objects.filter(active=True)
            city_serializer = CitySerializer(cities, many=True)
            
            # Get all active features
            features = Feature.objects.filter(active=True)
            feature_serializer = FeatureSerializer(features, many=True)
            
            return Response({
                "cities": city_serializer.data,
                "apartment_features": feature_serializer.data
            }, status=status.HTTP_200_OK)
            
        except DatabaseError:
            return Response(
                {"error": "A database error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
