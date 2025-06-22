import pytest
from datetime import date, timedelta
from apartments.models import City, Feature, Apartment, ApartmentFeature, ApartmentUserLike


def assert_timestamps_equal(ts1, ts2, tolerance_microseconds=50):
    """Assert that two timestamps are equal within a microsecond tolerance."""
    assert abs(ts1 - ts2).total_seconds() * 1_000_000 < tolerance_microseconds


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
    assert str(apartment) == "Rager, Test City - 3 rooms"


@pytest.mark.django_db
def test_apartment_feature_str_representation(test_apartment, test_feature):
    apartment_feature = ApartmentFeature.objects.create(
        apartment=test_apartment,
        feature=test_feature,
    )
    assert str(apartment_feature) == f"{test_apartment.id} - Test Feature"


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
def test_city_str_representation(valid_city_data):
    city = City.objects.create(**valid_city_data)
    assert str(city) == f"{valid_city_data['name']} {valid_city_data['hebrew_name']}"


@pytest.mark.django_db
def test_city_auto_timestamps(valid_city_data):
    city = City.objects.create(**valid_city_data)
    assert city.created_at is not None
    assert city.updated_at is not None
    assert_timestamps_equal(city.created_at, city.updated_at)


@pytest.mark.django_db
def test_city_default_active(valid_city_data):
    # Remove active from data to test default
    del valid_city_data['active']
    city = City.objects.create(**valid_city_data)
    assert city.active is True  # Default value


@pytest.mark.django_db
def test_feature_str_representation(valid_feature_data):
    feature = Feature.objects.create(**valid_feature_data)
    assert str(feature) == valid_feature_data['name']


@pytest.mark.django_db
def test_feature_auto_timestamps(valid_feature_data):
    feature = Feature.objects.create(**valid_feature_data)
    assert feature.created_at is not None
    assert feature.updated_at is not None
    assert_timestamps_equal(feature.created_at, feature.updated_at, tolerance_microseconds=100)


@pytest.mark.django_db
def test_feature_default_active(valid_feature_data):
    # Remove active from data to test default
    del valid_feature_data['active']
    feature = Feature.objects.create(**valid_feature_data)
    assert feature.active is True  # Default value