import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from apartments.models import Apartment

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