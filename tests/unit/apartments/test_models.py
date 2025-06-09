import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from apartments.models import City, Feature, Apartment, ApartmentFeature, ApartmentUserLike, ApartmentPhoto
from decimal import Decimal


@pytest.mark.django_db
def test_city_str_returns_name():
    city = City.objects.create(
        name="Tel Aviv",
        hebrew_name="תל אביב",
        active=True,
    )
    assert str(city) == "Tel Aviv תל אביב"


@pytest.mark.django_db
def test_city_default_active_true():
    city = City.objects.create(
        name="Inactive City",
        hebrew_name="עיר",
    )
    assert city.active is True


@pytest.mark.django_db
def test_feature_str_returns_name():
    feature = Feature.objects.create(
        name="Parking",
        description="Provides parking space for vehicles",
        active=True,
    )
    assert str(feature) == "Parking"


@pytest.mark.django_db
def test_feature_default_active_true():
    feature = Feature.objects.create(
        name="Balcony",
        description="Has a private balcony",
    )
    assert feature.active is True


@pytest.mark.django_db
def test_feature_name_unique():
    # Create first feature
    Feature.objects.create(
        name="Garden",
        description="Has a garden or green space",
    )
    
    # Try to create another feature with the same name
    with pytest.raises(Exception):  # Should raise IntegrityError
        Feature.objects.create(
            name="Garden",  # Same name as above
            description="Different description",
        )


@pytest.fixture
def test_user():
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )


@pytest.fixture
def test_city():
    return City.objects.create(
        name="Beer Sheva",
        hebrew_name="באר שבע",
    )


@pytest.fixture
def valid_apartment_data(test_user, test_city):
    return {
        "user": test_user,
        "city": test_city,
        "street": "Rager",
        "type": "Apartment",
        "floor": 3,
        "number_of_rooms": 3,
        "number_of_available_rooms": 2,
        "total_price": Decimal('2500.00'),
        "available_entry_date": date.today() + timedelta(days=30),  # 30 days from now
        "about": "A nice apartment in Beer Sheva",
        "latitude": Decimal('31.2518000'),  # Using Decimal with exactly 7 decimal places
        "longitude": Decimal('34.7913000'),  # Using Decimal with exactly 7 decimal places
        "area": "Old City",
    }


@pytest.mark.django_db
def test_apartment_str_representation(test_user, test_city):
    apartment = Apartment.objects.create(
        user=test_user,
        city=test_city,
        street="Rager",
        type="Apartment",
        floor=3,
        number_of_rooms=3,
        number_of_available_rooms=2,
        total_price=2500.00,
        available_entry_date=date.today() + timedelta(days=30),
    )
    assert str(apartment) == "Rager, Beer Sheva - 3 rooms"


@pytest.mark.django_db
def test_apartment_validation_valid_data(valid_apartment_data):
    apartment = Apartment(**valid_apartment_data)
    apartment.full_clean()  # Should not raise ValidationError
    apartment.save()
    assert apartment.id is not None


@pytest.mark.django_db
def test_apartment_validation_invalid_type(valid_apartment_data):
    valid_apartment_data["type"] = "Apartment123"  # Contains numbers
    apartment = Apartment(**valid_apartment_data)
    with pytest.raises(ValidationError) as exc_info:
        apartment.full_clean()
    assert "type" in exc_info.value.message_dict


@pytest.mark.django_db
def test_apartment_validation_invalid_floor(valid_apartment_data):
    valid_apartment_data["floor"] = -1  # Invalid floor
    apartment = Apartment(**valid_apartment_data)
    with pytest.raises(ValidationError) as exc_info:
        apartment.full_clean()
    assert "floor" in exc_info.value.message_dict


@pytest.mark.django_db
def test_apartment_validation_invalid_rooms(valid_apartment_data):
    valid_apartment_data["number_of_rooms"] = 11  # Too many rooms
    apartment = Apartment(**valid_apartment_data)
    with pytest.raises(ValidationError) as exc_info:
        apartment.full_clean()
    assert "number_of_rooms" in exc_info.value.message_dict


@pytest.mark.django_db
def test_apartment_validation_available_rooms_exceed_total(valid_apartment_data):
    valid_apartment_data["number_of_rooms"] = 3
    valid_apartment_data["number_of_available_rooms"] = 4  # More than total rooms
    apartment = Apartment(**valid_apartment_data)
    with pytest.raises(ValidationError) as exc_info:
        apartment.full_clean()
    assert "number_of_available_rooms" in exc_info.value.message_dict


@pytest.mark.django_db
def test_apartment_validation_past_entry_date(valid_apartment_data):
    valid_apartment_data["available_entry_date"] = date.today() - timedelta(days=1)  # Yesterday
    apartment = Apartment(**valid_apartment_data)
    with pytest.raises(ValidationError) as exc_info:
        apartment.full_clean()
    assert "available_entry_date" in exc_info.value.message_dict


@pytest.mark.django_db
def test_apartment_validation_about_too_long(valid_apartment_data):
    valid_apartment_data["about"] = "x" * 1001  # 1001 characters
    apartment = Apartment(**valid_apartment_data)
    with pytest.raises(ValidationError) as exc_info:
        apartment.full_clean()
    assert "about" in exc_info.value.message_dict


@pytest.mark.django_db
def test_apartment_validation_area_apostrophe_removal(valid_apartment_data):
    valid_apartment_data["area"] = "Old City'"  # With trailing apostrophe
    apartment = Apartment(**valid_apartment_data)
    apartment.full_clean()
    apartment.save()
    assert apartment.area == "Old City"  # Apostrophe should be removed


@pytest.fixture
def test_apartment(valid_apartment_data):
    apartment = Apartment(**valid_apartment_data)
    apartment.save()
    return apartment


@pytest.fixture
def test_feature():
    return Feature.objects.create(
        name="Parking",
        description="Provides parking space for vehicles",
    )


@pytest.mark.django_db
def test_apartment_feature_str_representation(test_apartment, test_feature):
    apartment_feature = ApartmentFeature.objects.create(
        apartment=test_apartment,
        feature=test_feature,
    )
    assert str(apartment_feature) == f"{test_apartment.id} - Parking"


@pytest.mark.django_db
def test_apartment_feature_cascade_delete(test_apartment, test_feature):
    # Create apartment-feature relationship
    apartment_feature = ApartmentFeature.objects.create(
        apartment=test_apartment,
        feature=test_feature,
    )
    
    # Delete the apartment
    test_apartment.delete()
    
    # The relationship should be deleted
    assert not ApartmentFeature.objects.filter(id=apartment_feature.id).exists()
    # But the feature should still exist
    assert Feature.objects.filter(id=test_feature.id).exists()


@pytest.mark.django_db
def test_apartment_user_like_create(test_user, test_apartment):
    like = ApartmentUserLike.objects.create(
        apartment=test_apartment,
        user=test_user,
        like=True,
    )
    assert like.id is not None
    assert like.like is True


@pytest.mark.django_db
def test_apartment_user_like_cascade_delete_apartment(test_user, test_apartment):
    # Create a like
    like = ApartmentUserLike.objects.create(
        apartment=test_apartment,
        user=test_user,
        like=True,
    )
    
    # Delete the apartment
    test_apartment.delete()
    
    # The like should be deleted
    assert not ApartmentUserLike.objects.filter(id=like.id).exists()


@pytest.mark.django_db
def test_apartment_user_like_cascade_delete_user(test_user, test_apartment):
    # Create a like
    like = ApartmentUserLike.objects.create(
        apartment=test_apartment,
        user=test_user,
        like=True,
    )
    
    # Delete the user
    test_user.delete()
    
    # Both the like and the apartment should be deleted
    assert not ApartmentUserLike.objects.filter(id=like.id).exists()
    assert not Apartment.objects.filter(id=test_apartment.id).exists()


@pytest.fixture
def test_image():
    return SimpleUploadedFile(
        name="test_image.jpg",
        content=b"",  # Empty content for testing
        content_type="image/jpeg"
    )


@pytest.mark.django_db
def test_apartment_photo_str_representation(test_apartment, test_image):
    photo = ApartmentPhoto.objects.create(
        apartment=test_apartment,
        photo=test_image,
    )
    assert str(photo) == f"Photo for Apartment {test_apartment.id}"


@pytest.mark.django_db
def test_apartment_photo_cascade_delete(test_apartment, test_image):
    # Create a photo
    photo = ApartmentPhoto.objects.create(
        apartment=test_apartment,
        photo=test_image,
    )
    
    # Delete the apartment
    test_apartment.delete()
    
    # The photo should be deleted
    assert not ApartmentPhoto.objects.filter(id=photo.id).exists() 