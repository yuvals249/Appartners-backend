"""
Apartment like-related views for the apartments app.
"""
import logging
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apartments.models import Apartment, ApartmentUserLike
from apartments.serializers.apartment import ApartmentSerializer
from apartments.utils.compatibility import calculate_user_compatibility
from users.models.user_details import UserDetails
from users.models.user_like import UserUserLike
from users.serializers.api_user_details import ApiUserDetailsSerializer
from users.services.firebase_service import FirebaseService

# Get logger
logger = logging.getLogger(__name__)


class ApartmentLikeView(APIView):
    """
    Endpoint to like or unlike an apartment for the authenticated user using JWT in Authorization header.
    """

    def post(self, request):
        if request.token_error:
            return request.token_error
            
        user_id = request.user_from_token

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
            
            # Send push notification if the user liked the apartment (not if they unliked it)
            if like and (created or not obj.like):
                try:
                    # Get the apartment owner's user ID
                    apartment_owner_id = apartment.user_id
                    
                    # Get the liker's name
                    liker = User.objects.get(id=user_id)
                    liker_name = f"{liker.first_name} {liker.last_name}"
                    
                    # Get the apartment address as the title
                    apartment_title = f"Apartment at {apartment.street}, {apartment.city.name}"
                    
                    # Send push notification to the apartment owner
                    FirebaseService.send_apartment_like_notification(
                        apartment_owner_id=apartment_owner_id,
                        liker_name=liker_name,
                        apartment_title=apartment_title
                    )
                    
                    logger.info(f"Sent push notification to user {apartment_owner_id} about apartment like")
                except Exception as e:
                    # Log the error but don't fail the request
                    logger.error(f"Error sending push notification: {str(e)}")

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
    Returns full user details according to the API specification, along with the apartment
    that was liked and a compatibility score between users.
    """
    
    def get(self, request):
        if request.token_error:
            return request.token_error
            
        user_id = request.user_from_token
        
        try:
            # Get all apartments owned by the user
            user_apartments = Apartment.objects.filter(user_id=user_id)
            
            if not user_apartments.exists():
                return Response(
                    {"message": "You haven't created any apartments yet"},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            # Get all likes for the user's apartments
            apartment_likes = ApartmentUserLike.objects.filter(
                apartment__in=user_apartments,
                like=True
            ).select_related('apartment').order_by('-created_at')
            
            # Extract liker IDs
            likers_ids = [like.user_id for like in apartment_likes]
            
            # Create a mapping of liker_id to apartment
            liker_to_apartment = {}
            for like in apartment_likes:
                liker_to_apartment[like.user_id] = like.apartment
            
            # Get all user-to-user likes/dislikes
            user_likes = UserUserLike.objects.filter(
                user_id=user_id,
                target_user_id__in=likers_ids
            )
            
            # Get all users that have already been liked or disliked
            responded_users = {ul.target_user_id for ul in user_likes}
            
            # Filter out users that have already been liked or disliked
            likers_ids = [uid for uid in likers_ids if uid not in responded_users]
            
            # Get the user details for these users
            user_details = UserDetails.objects.filter(user_id__in=likers_ids)
            
            if not user_details.exists():
                return Response(
                    {"message": "No new users have liked your apartment"},
                    status=status.HTTP_200_OK
                )
            
            try:
                # Use the API-compliant serializer for user details
                user_serializer = ApiUserDetailsSerializer(user_details, many=True)
                users_data = user_serializer.data
                
                # Add apartment and compatibility score to each user
                for i, user_data in enumerate(users_data):
                    liker_id = user_data.get('id')
                    
                    # Get the specific apartment this user liked
                    liked_apartment = liker_to_apartment.get(liker_id)
                    if liked_apartment:
                        # Serialize the apartment
                        apartment_serializer = ApartmentSerializer(liked_apartment)
                        users_data[i]['liked_apartment'] = apartment_serializer.data
                    
                    # Calculate compatibility score (0-1) and convert to percentage (0-100)
                    compatibility_score = calculate_user_compatibility(user_id, liker_id) * 100
                    # Round to nearest integer
                    users_data[i]['compatibility_score'] = round(compatibility_score)
                
                # Prepare the response data - just return the users with embedded apartment data
                response_data = users_data
                
                return Response(response_data, status=status.HTTP_200_OK)
            except Exception as serializer_error:
                logger.error(f"Error serializing data: {str(serializer_error)}", exc_info=True)
                return Response(
                    {"error": f"Error serializing data: {str(serializer_error)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
        except Exception as e:
            logger.error(f"Error in ApartmentLikersView: {str(e)}", exc_info=True)
            return Response(
                {"error": f"An error occurred while fetching data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
