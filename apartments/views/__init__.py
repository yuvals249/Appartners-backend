"""
Apartment views package.
This package contains all the views for the apartments app.
"""

from .apartment_views import ApartmentCreateView, ApartmentView, ApartmentPostPayloadView
from .like_views import ApartmentLikeView, ApartmentLikersView
from .user_apartment_views import UserApartmentsView, UserLikedApartmentsView
from .recommendation_views import ApartmentRecommendationView

__all__ = [
    'ApartmentCreateView',
    'ApartmentView',
    'ApartmentPostPayloadView',
    'ApartmentLikeView',
    'ApartmentLikersView',
    'UserApartmentsView',
    'UserLikedApartmentsView',
    'ApartmentRecommendationView',
]
