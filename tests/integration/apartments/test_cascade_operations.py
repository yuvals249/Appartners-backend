import pytest
from apartments.models import ApartmentFeature, ApartmentUserLike, Apartment, Feature


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