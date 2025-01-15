from django.urls import path
from .views import (
    ApartmentCreateView,
    # ApartmentDetailView,
    # ApartmentPhotoListView,
    # FeatureListCreateView,
    # AddFeatureToApartmentView
)

urlpatterns = [
    path('new', ApartmentCreateView.as_view(), name='apartment-create'),
    # path('<uuid:pk>/', ApartmentDetailView.as_view(), name='apartment-detail'),
    # path('features/', FeatureListCreateView.as_view(), name='feature-list-create'),
    # path('apartments/add-feature/', AddFeatureToApartmentView.as_view(), name='add-feature-to-apartment'),
    # path('apartments/<uuid:apartment_id>/photos/', ApartmentPhotoListView.as_view(), name='apartment-photo-list')
]
