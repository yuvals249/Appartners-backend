import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

@pytest.mark.django_db
def test_smoke_create_apartment(api_client, token_header):
    # Create a test city first (required for apartment creation)
    from apartments.models import City
    city = City.objects.create(
        name="Test City",
        hebrew_name="עיר בדיקה",
        active=True
    )
    
    # Create a test photo
    test_image = SimpleUploadedFile(
        name='test_image.jpg',
        content=b'',  # Empty file for testing
        content_type='image/jpeg'
    )
    
    # Prepare apartment data with required fields
    data = {
        "city": city.id,
        "street": "Test Street",
        "type": "Regular",
        "floor": 1,
        "number_of_rooms": 2,
        "number_of_available_rooms": 1,
        "total_price": 3000,
        "available_entry_date": "2026-07-01",  # Future date in 2026
        "about": "Test apartment",
        "latitude": 32.0853,
        "longitude": 34.7818,
        "photos": test_image,  # Add the photo
    }
    
    response = api_client.post(
        "/api/v1/apartments/new/",
        data=data,  # Send as form data
        **token_header,
    )
    assert response.status_code == 201
    assert response.data["street"] == "Test Street"