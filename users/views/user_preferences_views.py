from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from appartners.utils import get_user_from_token

from users.models import UserPreferences, UserPreferencesFeatures
from users.serializers import UserPreferencesGetSerializer


class UserPreferencesView(APIView):
    """
    Get, Create or update user preferences for the authenticated user.
    """

    def get(self, request):
        # Extract user from token
        success, result = get_user_from_token(request)
        if not success:
            return result  # Return the error response
        user_id = result
        
        try:
            # Get the user's preferences
            try:
                user_preferences = UserPreferences.objects.get(user_id=user_id)
            except UserPreferences.DoesNotExist:
                return Response({"errors": "User preferences not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Serialize the user preferences
            serializer = UserPreferencesGetSerializer(user_preferences)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DatabaseError:
            return Response(
                {"errors": "A database error occurred. Please try again later"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        # Extract user from token
        success, result = get_user_from_token(request)
        if not success:
            return result  # Return the error response
        user_id = result

        # Extract and clean data
        data = request.data.copy()
        city = data.get('city')
        
        # Validate required fields
        if not city:
            return Response({"errors": "City is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Clean optional fields - normalize None values
        null_values = [None, '', 'null']
        fields = {
            'move_in_date': data.get('move_in_date'),
            'number_of_roommates': data.get('number_of_roommates'),
            'max_floor': data.get('max_floor'),
            'area': data.get('area')
        }
        
        # Set None for any null-like values
        cleaned_fields = {k: None if v in null_values else v for k, v in fields.items()}
        
        # Extract price range
        price_range = data.get('price_range', {})
        min_price = price_range.get('min_price') if price_range else None
        max_price = price_range.get('max_price') if price_range else None
        
        # Extract features
        features = data.get('features') or []

        try:
            # Create or update the user preferences
            prefs, created = UserPreferences.objects.update_or_create(
                user_id=user_id,
                defaults={
                    'city_id': city,
                    'move_in_date': cleaned_fields['move_in_date'],
                    'number_of_roommates': cleaned_fields['number_of_roommates'],
                    'min_price': min_price,
                    'max_price': max_price,
                    'max_floor': cleaned_fields['max_floor'],
                    'area': cleaned_fields['area'],
                }
            )
            
            # Handle features - clear existing and add new ones
            UserPreferencesFeatures.objects.filter(user_preferences=prefs).delete()
            
            # Bulk create feature associations if any features provided
            if features:
                feature_objects = [
                    UserPreferencesFeatures(user_preferences=prefs, feature_id=feature_id)
                    for feature_id in features
                ]
                UserPreferencesFeatures.objects.bulk_create(feature_objects)
            
            return Response(UserPreferencesGetSerializer(prefs).data, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Format error response
            if isinstance(e, ValidationError) and hasattr(e, 'message_dict'):
                return Response({"errors": list(e.message_dict.values())[0]}, status=status.HTTP_400_BAD_REQUEST)
                
            error_message = str(e)
            if "cannot be null" in error_message and "'" in error_message:
                field = error_message.split("'")[1]
                return Response({"errors": f"{field.capitalize()} is required"}, status=status.HTTP_400_BAD_REQUEST)
                
            return Response({"errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)
