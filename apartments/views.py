from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.contrib.auth.models import User
from jwt import ExpiredSignatureError, InvalidTokenError

from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apartments.serializers import ApartmentPostPayloadSerializer
from apartments.serializers.apartment import ApartmentSerializer
from appartners.utils import decode_jwt, get_user_from_token
from appartners.validators import UUIDValidator

from apartments.models import Apartment, ApartmentUserLike
from users.serializers.user_basic import UserBasicSerializer
from users.models.user_details import UserDetails

import logging

logger = logging.getLogger(__name__)

class ApartmentCreateView(APIView):
    """
    API View to create a new apartment.
    """

    def post(self, request, *args, **kwargs):
        # Extract user from token using centralized function
        success, result = get_user_from_token(request)
        if not success:
            return result  # Return the error response
            
        user_id = result
        
        # Add user to request data
        request_data = request.data.copy()
        request_data['user_id'] = user_id
        
        serializer = ApartmentSerializer(data=request_data)
        if serializer.is_valid():
            try:
                serializer.save()
            except ValidationError as e:
                # Handle model-level validation errors
                return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)
            except DatabaseError:
                # Handle database errors
                return Response(
                    {"error": "An error occurred while saving data"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApartmentPostPayloadView(APIView):
    """
    Get dropdown data for apartment post.
    """

    def get(self, request, *args, **kwargs):
        try:
            # Fetch payload using the serializer
            payload = ApartmentPostPayloadSerializer({}).data
            return Response(payload)
        except DatabaseError:
            # Handle database errors
            return Response(
                {"error": "An error occurred while fetching dropdown data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except APIException as e:
            # Handle serialization-related errors
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ApartmentView(APIView):
    """
    Retrieve or delete an apartment by ID.
    """

    def get(self, request, apartment_id):
        try:
            validator = UUIDValidator()
            if not validator(apartment_id):
                return Response(
                    {"error": "Invalid UUID format"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            apartment = Apartment.objects.get(id=apartment_id)
        except Apartment.DoesNotExist:
            return Response(
                {"error": "Apartment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ApartmentSerializer(apartment)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def delete(self, request, apartment_id):
        # Extract user from token using centralized function
        success, result = get_user_from_token(request)
        if not success:
            return result  # Return the error response
            
        user_id = result
        
        try:
            validator = UUIDValidator()
            if not validator(apartment_id):
                return Response(
                    {"error": "Invalid UUID format"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Get the apartment
            apartment = Apartment.objects.get(id=apartment_id)
            
            # Check if the user is the owner of the apartment
            if apartment.user_id != user_id:
                return Response(
                    {"error": "You don't have permission to delete this apartment"},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            # Delete the apartment (this will cascade to related entities)
            apartment.delete()
            
            return Response(
                {"message": "Apartment and all related data deleted successfully"},
                status=status.HTTP_200_OK
            )
            
        except Apartment.DoesNotExist:
            return Response(
                {"error": "Apartment not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except DatabaseError:
            return Response(
                {"error": "An error occurred while deleting the apartment"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
                    {"message": "You haven't created any apartments yet"},
                    status=status.HTTP_200_OK
                )
                
            serializer = ApartmentSerializer(apartments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
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


class ApartmentLikersView(APIView):
    """
    API View to retrieve all users who liked the authenticated user's apartment.
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
            
            # Get the user details for these users
            user_details = UserDetails.objects.filter(user_id__in=likers_ids)
            
            if not user_details.exists():
                return Response(
                    {"message": "No users have liked your apartment yet"},
                    status=status.HTTP_200_OK
                )
                
            serializer = UserBasicSerializer(user_details, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except DatabaseError:
            return Response(
                {"error": "An error occurred while fetching data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
