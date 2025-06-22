from unittest.mock import Mock, patch
from apartments.serializers.apartment import ApartmentSerializer
from apartments.models import Feature, ApartmentPhoto
from users.models import UserDetails


def test_apartment_serializer_basic(mock_apartment, mock_user_details, user_details_dict):
    """Test basic apartment serialization"""
    with patch.object(UserDetails.objects, 'get', return_value=mock_user_details):
        with patch('apartments.serializers.apartment.UserDetailsSerializer', return_value=Mock(data=user_details_dict)):
            serializer = ApartmentSerializer(mock_apartment)
            data = serializer.data
            assert data['id'] == str(1)
            assert data['city_details']['name'] == "Tel Aviv"
            assert data['city_details']['hebrew_name'] == "תל אביב"
            assert data['area'] == "Test Area"
            assert data['floor'] == 3
            assert data['number_of_rooms'] == 2
            assert data['number_of_available_rooms'] == 1
            assert data['total_price'] == '5000.00'
            assert data['user_details']['email'] == "user@example.com"
            assert isinstance(data['feature_details'], list)
            assert isinstance(data['photo_urls'], list)


def test_apartment_serializer_with_features(mock_apartment, mock_user_details, user_details_dict):
    """Test apartment serialization with features"""
    feature1 = Mock(spec=Feature)
    feature1.id = 1
    feature1.name = "Parking"
    feature2 = Mock(spec=Feature)
    feature2.id = 2
    feature2.name = "Balcony"
    apartment_feature1 = Mock()
    apartment_feature1.feature = feature1
    apartment_feature2 = Mock()
    apartment_feature2.feature = feature2
    mock_apartment.apartment_features.all.return_value = [apartment_feature1, apartment_feature2]
    with patch.object(UserDetails.objects, 'get', return_value=mock_user_details):
        with patch('apartments.serializers.apartment.UserDetailsSerializer', return_value=Mock(data=user_details_dict)):
            serializer = ApartmentSerializer(mock_apartment)
            data = serializer.data
            assert len(data['feature_details']) == 2
            assert data['feature_details'][0]['name'] == "Parking"
            assert data['feature_details'][1]['name'] == "Balcony"


def test_apartment_serializer_with_photos(mock_apartment, mock_user_details, user_details_dict):
    """Test apartment serialization with photos"""
    photo1 = Mock(spec=ApartmentPhoto)
    photo1.photo = Mock()
    photo1.photo.url = "http://example.com/photo1.jpg"
    photo2 = Mock(spec=ApartmentPhoto)
    photo2.photo = Mock()
    photo2.photo.url = "http://example.com/photo2.jpg"
    mock_apartment.photos.all.return_value = [photo1, photo2]
    with patch.object(UserDetails.objects, 'get', return_value=mock_user_details):
        with patch('apartments.serializers.apartment.UserDetailsSerializer', return_value=Mock(data=user_details_dict)):
            serializer = ApartmentSerializer(mock_apartment)
            data = serializer.data
            assert len(data['photo_urls']) == 2
            assert data['photo_urls'][0] == "http://example.com/photo1.jpg"
            assert data['photo_urls'][1] == "http://example.com/photo2.jpg"


def test_apartment_serializer_with_location(mock_apartment, mock_user_details, user_details_dict):
    """Test apartment serialization with location data"""
    mock_apartment.latitude = 32.0853
    mock_apartment.longitude = 34.7818
    with patch.object(UserDetails.objects, 'get', return_value=mock_user_details):
        with patch('apartments.serializers.apartment.UserDetailsSerializer', return_value=Mock(data=user_details_dict)):
            serializer = ApartmentSerializer(mock_apartment)
            data = serializer.data
            assert data['latitude'] == '32.0853000'
            assert data['longitude'] == '34.7818000'
