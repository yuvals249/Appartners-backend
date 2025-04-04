"""
Apartment detail views for retrieving and deleting apartments.
"""
from django.db import DatabaseError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apartments.serializers.apartment import ApartmentSerializer
from apartments.models import Apartment
from appartners.utils import get_user_from_token
from appartners.validators import UUIDValidator


class ApartmentView(APIView):
    """
    Retrieve or delete an apartment by ID.
    """
    
    def get(self, request, apartment_id):
        # Validate UUID format
        is_valid, error_response = UUIDValidator.validate(apartment_id)
        if not is_valid:
            return error_response
            
        try:
            apartment = Apartment.objects.get(id=apartment_id)
            serializer = ApartmentSerializer(apartment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Apartment.DoesNotExist:
            return Response(
                {"error": "Apartment not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except DatabaseError:
            return Response(
                {"error": "A database error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, apartment_id):
        # Validate UUID format
        is_valid, error_response = UUIDValidator.validate(apartment_id)
        if not is_valid:
            return error_response
            
        # Extract user from token using centralized function
        success, result = get_user_from_token(request)
        if not success:
            return result  # Return the error response
            
        user_id = result
            
        try:
            apartment = Apartment.objects.get(id=apartment_id)
            
            # Check if the user is the owner of the apartment
            if apartment.user.id != user_id:
                return Response(
                    {"error": "You do not have permission to delete this apartment"},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            apartment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Apartment.DoesNotExist:
            return Response(
                {"error": "Apartment not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except DatabaseError:
            return Response(
                {"error": "A database error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
