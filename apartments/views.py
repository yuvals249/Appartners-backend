from django.core.exceptions import ValidationError
from django.db import DatabaseError
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apartments.models import Apartment
from apartments.serializers import ApartmentPostPayloadSerializer
from apartments.serializers.apartment import ApartmentSerializer
from appartners.validators import UUIDValidator


class ApartmentCreateView(APIView):
    """
    API View to create a new apartment.
    """

    def post(self, request, *args, **kwargs):
        serializer = ApartmentSerializer(data=request.data)
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
    Retrieve an apartment by ID.
    """

    def get(self, request, apartment_id):
        # Validate UUID format
        print(f'type: {type(apartment_id)}')
        try:
            validator = UUIDValidator()
            if not validator(apartment_id):
                return Response(
                    {"error": "Invalid apartment ID format."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            apartment = Apartment.objects.get(id=apartment_id)
        except Apartment.DoesNotExist:
            return Response({"error": "Apartment not found."}, status=status.HTTP_404_NOT_FOUND)
        except DatabaseError:
            return Response(
                {"error": "A database error occurred. Please try again later"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Serialize the apartment data
        serializer = ApartmentSerializer(apartment)
        return Response(serializer.data, status=status.HTTP_200_OK)
