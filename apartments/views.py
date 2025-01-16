from django.core.exceptions import ValidationError
from django.db import DatabaseError
from jwt import ExpiredSignatureError, InvalidTokenError

from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apartments.serializers import ApartmentPostPayloadSerializer
from apartments.serializers.apartment import ApartmentSerializer
from appartners.utils import decode_jwt
from appartners.validators import UUIDValidator

from apartments.models import Apartment, ApartmentUserLike


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


class ApartmentLikeView(APIView):
    """
    Endpoint to like or unlike an apartment for the authenticated user using JWT in UserAuth header.
    """

    def post(self, request):
        # Extract the token from the UserAuth header
        token = request.headers.get('UserAuth')
        print(f'token: {token}')
        if not token:
            return Response({"error": "UserAuth header missing"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            # Decode the JWT
            user_id, email = decode_jwt(token)
        except ExpiredSignatureError:
            return Response({"error": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
        except InvalidTokenError:
            return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

        # Validate the user ID from the token
        if not user_id:
            return Response({"error": "Invalid token payload"}, status=status.HTTP_401_UNAUTHORIZED)

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
