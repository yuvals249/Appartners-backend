"""
This file is maintained for backward compatibility.
All views have been moved to the views/ directory for better organization.
"""

from apartments.views.apartment_views import ApartmentCreateView, ApartmentView, ApartmentPostPayloadView
from apartments.views.like_views import ApartmentLikeView, ApartmentLikersView
from apartments.views.user_apartment_views import UserApartmentsView, UserLikedApartmentsView
from apartments.views.recommendation_views import ApartmentRecommendationView

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
