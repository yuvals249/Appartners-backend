"""
Views for user-to-user likes/dislikes.
"""
import logging
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response    
from rest_framework.views import APIView

from users.models import UserUserLike
from apartments.models import Apartment, ApartmentUserLike

logger = logging.getLogger(__name__)


class UserLikeView(APIView):
    """
    API endpoint for liking or disliking a user who has liked your apartment.
    
    Endpoint: POST /api/v1/users/like/
    Request body:
        - target_user_id: ID of the user to like/dislike
        - like: Boolean value (true for like, false for dislike)
    
    Returns:
        - 200: Like/dislike recorded successfully
        - 400: Invalid input or validation error
        - 404: User not found or target user hasn't liked your apartment
        - 500: Server error
    """
    
    def post(self, request):
        # Return error if authentication failed
        if request.token_error:
            return request.token_error
            
        # Get user_id from the request (set by middleware)
        user_id = request.user_from_token
        
        # Get request data
        target_user_id = request.data.get('target_user_id')
        like = request.data.get('like')  # Boolean value
        
        # Validate input
        if target_user_id is None or like is None:
            return Response(
                {"error": "Target user ID and like field are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Convert target_user_id to int if it's a string
            if isinstance(target_user_id, str) and target_user_id.isdigit():
                target_user_id = int(target_user_id)
                
            # Get the users
            user = User.objects.get(id=user_id)
            target_user = User.objects.get(id=target_user_id)
            
            # Verify that the target user has liked the user's apartment
            user_apartment = Apartment.objects.filter(user=user).first()
            if not user_apartment:
                return Response(
                    {"error": "You don't have an apartment to receive likes"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Check if target user has liked the user's apartment
            has_liked = ApartmentUserLike.objects.filter(
                apartment=user_apartment,
                user=target_user,
                like=True
            ).exists()
            
            if not has_liked:
                return Response(
                    {"error": "This user hasn't liked your apartment"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Create or update the user like record
            with transaction.atomic():
                user_like, created = UserUserLike.objects.update_or_create(
                    user=user,
                    target_user=target_user,
                    defaults={'like': like}
                )
                
                action = "liked" if like else "disliked"
                logger.info(f"User {user.id} has {action} user {target_user.id}")
                
                return Response(
                    {"message": f"You have {action} this user"},
                    status=status.HTTP_200_OK
                )
                
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error in user like view: {str(e)}")
            return Response(
                {"error": "An error occurred while processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )