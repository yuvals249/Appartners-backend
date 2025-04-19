"""
Apartment like-related views for the apartments app.
"""
from django.core.exceptions import ValidationError
from django.db import DatabaseError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apartments.models import Apartment, ApartmentUserLike
from users.serializers.user_basic import UserBasicSerializer
from users.models.user_details import UserDetails
from appartners.utils import get_user_from_token
from users.serializers.api_user_details import ApiUserDetailsSerializer
import logging

# Get logger
logger = logging.getLogger(__name__)


class ApartmentLikeView(APIView):
    """
    Endpoint to like or unlike an apartment for the authenticated user using JWT in Authorization header.
    """

    def post(self, request):
        # Extract user from token using centralized function
        success, result = get_user_from_token(request)
        if not success:
            return result  # Return the error response
            
        user_id = result

        # Get the apartment ID and like field from the request data
        apartment_id = request.data.get('apartment_id')
        like = request.data.get('like')  # Boolean value

        if not apartment_id or like is None:
            return Response({"error": "Apartment ID and like field are required"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            apartment = Apartment.objects.get(id=apartment_id)
            # Check if a record for the user and apartment already exists
            obj, created = ApartmentUserLike.objects.update_or_create(
                user_id=user_id,
                apartment=apartment,
                defaults={'like': like}
            )

            if created:
                message = "Apartment like created successfully."
            else:
                message = "Apartment like updated successfully."

            return Response({"message": message}, status=status.HTTP_200_OK)

        except Apartment.DoesNotExist:
            return Response({"error": "Apartment not found."},
                            status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            # Handle validation errors
            return Response(
                {"error": e.message if isinstance(e.message, str) else e.messages},
                status=status.HTTP_400_BAD_REQUEST
            )


class ApartmentLikersView(APIView):
    """
    API View to retrieve all users who liked the authenticated user's apartment.
    Returns full user details according to the API specification.
    """
    
    def get(self, request):
        # Extract user from token using centralized function
        success, result = get_user_from_token(request)
        if not success:
            return result  # Return the error response
            
        user_id = result
        
        try:
            # Find the user's apartment
            user_apartment = Apartment.objects.filter(user_id=user_id).first()
            
            if not user_apartment:
                return Response(
                    {"message": "You haven't created any apartments yet"},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            # Get all users who liked this apartment
            likers_ids = ApartmentUserLike.objects.filter(
                apartment=user_apartment,
                like=True
            ).values_list('user_id', flat=True)
            
            logger.info(f"Found {len(likers_ids)} likers for apartment {user_apartment.id}")
            
            # Get the user details for these users
            user_details = UserDetails.objects.filter(user_id__in=likers_ids)
            
            logger.info(f"Found {user_details.count()} user details records")
            
            if not user_details.exists():
                return Response(
                    {"message": "No users have liked your apartment yet"},
                    status=status.HTTP_200_OK
                )
            
            try:
                # Use the API-compliant serializer that matches the full specification
                serializer = ApiUserDetailsSerializer(user_details, many=True)
                data = serializer.data
                logger.info(f"Successfully serialized {len(data)} user details")
                return Response(data, status=status.HTTP_200_OK)
            except Exception as serializer_error:
                logger.error(f"Serializer error: {str(serializer_error)}")
                return Response(
                    {"error": f"Error serializing user data: {str(serializer_error)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
        except Exception as e:
            logger.error(f"Error in ApartmentLikersView: {str(e)}", exc_info=True)
            return Response(
                {"error": f"An error occurred while fetching data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
