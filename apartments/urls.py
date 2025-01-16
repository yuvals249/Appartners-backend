from django.urls import path
from .views import (
    ApartmentCreateView,ApartmentPostPayloadView, ApartmentView, ApartmentLikeView
)

urlpatterns = [
    path('new', ApartmentCreateView.as_view(), name='apartment-create'),
    path('post-payload', ApartmentPostPayloadView.as_view(), name='apartment-post-payload'),
    path('<str:apartment_id>/', ApartmentView.as_view(), name='apartment-get'),
    path('preference', ApartmentLikeView.as_view(), name='apartment-like'),
    # path('<uuid:pk>/', ApartmentDetailView.as_view(), name='apartment-detail'),
    # path('features/', FeatureListCreateView.as_view(), name='feature-list-create'),
    # path('apartments/add-feature/', AddFeatureToApartmentView.as_view(), name='add-feature-to-apartment'),
    # path('apartments/<uuid:apartment_id>/photos/', ApartmentPhotoListView.as_view(), name='apartment-photo-list')
]
