from django.urls import path
from .views import (
    ApartmentCreateView, ApartmentPostPayloadView, ApartmentView, 
    ApartmentLikeView, UserApartmentsView, UserLikedApartmentsView,
    ApartmentLikersView
)

urlpatterns = [
    path('new/', ApartmentCreateView.as_view(), name='apartment-create'),
    path('post-payload/', ApartmentPostPayloadView.as_view(), name='apartment-post-payload'),
    path('preference/', ApartmentLikeView.as_view(), name='apartment-like'),
    path('my/', UserApartmentsView.as_view(), name='user-apartments'),
    path('liked/', UserLikedApartmentsView.as_view(), name='user-liked-apartments'),
    path('likers/', ApartmentLikersView.as_view(), name='apartment-likers'),
    path('<str:apartment_id>/', ApartmentView.as_view(), name='apartment-get'),
    
]
