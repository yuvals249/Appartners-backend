"""
Apartment filtering utilities for recommendations.
"""
import logging
from dateutil.relativedelta import relativedelta
from django.db.models import Q

from apartments.models import Apartment, ApartmentUserLike
from users.models import UserPreferences

logger = logging.getLogger(__name__)


def get_user_preferences(user_id):
    """
    Get user preferences for filtering apartments.
    
    Args:
        user_id: ID of the user
        
    Returns:
        UserPreferences or None if not found
    """
    try:
        return UserPreferences.objects.get(user_id=user_id)
    except UserPreferences.DoesNotExist:
        return None


def get_interacted_apartments(user_id):
    """
    Get IDs of apartments the user has already interacted with.
    
    Args:
        user_id: ID of the user
        
    Returns:
        list: List of apartment IDs
    """
    return ApartmentUserLike.objects.filter(
        user_id=user_id
    ).values_list('apartment_id', flat=True)


def apply_price_filter(query, user_prefs):
    """
    Filter apartments by price range.
    
    Args:
        query: Base apartment query
        user_prefs: User preferences
        
    Returns:
        Filtered query
    """
    if hasattr(user_prefs, 'price_range') and user_prefs.price_range:
        min_price = user_prefs.price_range.get('min', 0)
        max_price = user_prefs.price_range.get('max', 100000)  # High default max
        return query.filter(total_price__gte=min_price, total_price__lte=max_price)
    return query


def apply_city_filter(query, user_prefs):
    """
    Filter apartments by city.
    
    Args:
        query: Base apartment query
        user_prefs: User preferences
        
    Returns:
        Filtered query
    """
    if user_prefs.city:
        return query.filter(city_id=user_prefs.city.id)
    return query


def apply_roommates_filter(query, user_prefs):
    """
    Filter apartments by number of roommates.
    
    Args:
        query: Base apartment query
        user_prefs: User preferences
        
    Returns:
        Filtered query
    """
    if hasattr(user_prefs, 'number_of_roommates') and user_prefs.number_of_roommates is not None:
        num_roommates = user_prefs.number_of_roommates
        
        # Calculate the range based on the rule
        min_rooms = num_roommates
        if num_roommates >= 2:
            min_rooms = num_roommates - 1
            
        max_rooms = num_roommates + 1
        
        return query.filter(number_of_rooms__gte=min_rooms, number_of_rooms__lte=max_rooms)
    return query


def apply_features_filter(query, user_prefs):
    """
    Filter apartments by features.
    
    Args:
        query: Base apartment query
        user_prefs: User preferences
        
    Returns:
        Filtered query
    """
    if hasattr(user_prefs, 'features') and user_prefs.features.exists():
        user_feature_ids = user_prefs.features.values_list('id', flat=True)
        return query.filter(features__id__in=user_feature_ids).distinct()
    return query


def apply_date_filter(query, user_prefs):
    """
    Filter apartments by move-in date.
    
    Args:
        query: Base apartment query
        user_prefs: User preferences
        
    Returns:
        Filtered query
    """
    if hasattr(user_prefs, 'preferred_move_in_date') and user_prefs.preferred_move_in_date:
        preferred_date = user_prefs.preferred_move_in_date
        
        # Calculate date range (±1 month)
        min_date = preferred_date - relativedelta(months=1)
        max_date = preferred_date + relativedelta(months=1)
        
        # Filter apartments with available_entry_date within the range
        return query.filter(
            Q(available_entry_date__gte=min_date) & 
            Q(available_entry_date__lte=max_date)
        )
    return query


def filter_apartments(user_id):
    """
    Apply all filters to get apartments matching user preferences.
    
    Args:
        user_id: ID of the user
        
    Returns:
        QuerySet of filtered apartments
    """
    try:
        # Get user preferences
        user_prefs = get_user_preferences(user_id)
        
        if not user_prefs:
            return Apartment.objects.none()
        
        # Get apartments the user has already interacted with
        interacted_apartment_ids = get_interacted_apartments(user_id)
        
        # Base query excluding apartments the user has interacted with
        base_query = Apartment.objects.exclude(id__in=interacted_apartment_ids)
        
        # Apply all filters
        filtered_query = base_query
        filtered_query = apply_price_filter(filtered_query, user_prefs)
        filtered_query = apply_city_filter(filtered_query, user_prefs)
        filtered_query = apply_roommates_filter(filtered_query, user_prefs)
        filtered_query = apply_features_filter(filtered_query, user_prefs)
        filtered_query = apply_date_filter(filtered_query, user_prefs)
        
        return filtered_query
        
    except Exception as e:
        logger.error(f"Error in filter_apartments: {str(e)}")
        return Apartment.objects.none()
