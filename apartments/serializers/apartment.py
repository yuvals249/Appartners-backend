from rest_framework import serializers
from apartments.models import City, ApartmentFeature, Feature, ApartmentPhoto
from apartments.serializers import FeatureSerializer
from apartments.models.apartment import Apartment
from django.contrib.auth.models import User
from users.models.user_details import UserDetails
from users.serializers.user_details import UserDetailsSerializer


class ApartmentSerializer(serializers.ModelSerializer):
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())  # City ID validation
    features = serializers.PrimaryKeyRelatedField(
        queryset=Feature.objects.all(), many=True, write_only=True, required=False  # For input
    )
    feature_details = serializers.SerializerMethodField()
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, required=False)
    photos = serializers.ListField(
        child=serializers.ImageField(), required=False, write_only=True  # Make photos write-only
    )
    photo_urls = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Apartment
        fields = [
            'id', 'city', 'street', 'type', 'floor', 'number_of_rooms',
            'number_of_available_rooms', 'total_price', 'available_entry_date',
            'about', 'features', 'feature_details', 'user_id', 'created_at', 'photos', 'photo_urls',
            'latitude', 'longitude', 'area', 'is_yad2', 'user_details'
        ]

    def get_feature_details(self, obj):
        """
        Get features through the intermediate model
        """
        features = [af.feature for af in obj.apartment_features.all()]
        return FeatureSerializer(features, many=True).data

    def get_user_details(self, obj):
        """
        Get the user details for the apartment owner
        """
        if obj.user:
            try:
                user_details = UserDetails.objects.get(user=obj.user)
                data = UserDetailsSerializer(user_details).data
                # Remove user_id if it exists in the data
                if 'user_id' in data:
                    data.pop('user_id')
                return data
            except UserDetails.DoesNotExist:
                return None
        return None

    def get_photo_urls(self, obj):
        """
        Get the URLs of all photos for this apartment.
        For regular apartments, this returns Cloudinary URLs.
        For Yad2 apartments, it ensures the URLs have proper file extensions.
        """
        photos = list(obj.photos.all())
        
        # If there are no photos in the database but the apartment is from Yad2,
        # the photos might be stored in a different way
        if not photos and getattr(obj, 'is_yad2', False):
            # Try to get photo URLs from a custom attribute that might be set during migration
            if hasattr(obj, 'photo_urls') and obj.photo_urls:
                return obj.photo_urls
            
            return []
        
        urls = []
        for photo in photos:
            url = photo.photo.url
            
            # For Yad2 photos, ensure they have the correct file extension
            if getattr(obj, 'is_yad2', False) and url and 'yad2.co.il' in url:
                # If URL doesn't end with a file extension, add .jpeg
                if not any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                    url = f"{url}.jpeg"
            
            urls.append(url)
            
        return urls

    def create(self, validated_data):
        features = validated_data.pop('features', [])
        user = validated_data.pop('user_id', None)
        photos = validated_data.pop('photos', [])
        
        # Create the apartment
        apartment = Apartment.objects.create(user=user, **validated_data)

        # Create ApartmentFeature instances for each feature
        for feature in features:
            ApartmentFeature.objects.create(
                apartment=apartment,
                feature=feature
            )
            
        # Create ApartmentPhoto instances for each photo
        for photo in photos:
            ApartmentPhoto.objects.create(
                apartment=apartment,
                photo=photo
            )

        return apartment
