"""
Apartment filtering utilities for recommendations.
"""
import logging
from dateutil.relativedelta import relativedelta
from django.db.models import Q
from django.db import connection

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
        connection.close()
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
    app =  ApartmentUserLike.objects.filter(
        user_id=user_id
    ).values_list('apartment_id', flat=True)
    logger.debug(f'apps i liked user_id: {user_id}, apps: {app}')
    return app


def apply_price_filter(query, user_prefs):
    """
    Filter apartments by price range.
    
    Args:
        query: Base apartment query
        user_prefs: User preferences
        
    Returns:
        Filtered query
    """
    if user_prefs and hasattr(user_prefs, 'min_price') and hasattr(user_prefs, 'max_price'):
        min_price = user_prefs.min_price
        max_price = user_prefs.max_price
        
        # Apply filters conditionally based on which values are provided
        if min_price is not None and max_price is not None:
            return query.filter(total_price__gte=min_price, total_price__lte=max_price)
        elif min_price is not None:
            return query.filter(total_price__gte=min_price)
        elif max_price is not None:
            return query.filter(total_price__lte=max_price)
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
    if user_prefs and hasattr(user_prefs, 'city') and user_prefs.city:
        return query.filter(city=user_prefs.city)
    return query


def apply_area_filter(query, user_prefs):
    """
    Filter apartments by area/neighborhood.
    
    Args:
        query: Base apartment query
        user_prefs: User preferences
        
    Returns:
        Filtered query
    """
    if user_prefs and hasattr(user_prefs, 'area') and user_prefs.area is not None and user_prefs.area != '':
        return query.filter(area=user_prefs.area)
    return query


def apply_max_floor_filter(query, user_prefs):
    """
    Filter apartments by maximum floor preference.
    
    Args:
        query: Base apartment query
        user_prefs: User preferences
        
    Returns:
        Filtered query
    """
    if user_prefs and hasattr(user_prefs, 'max_floor') and user_prefs.max_floor is not None:
        return query.filter(floor__lte=user_prefs.max_floor)
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
    if user_prefs and hasattr(user_prefs, 'number_of_roommates'):
        # If number_of_roommates is None or empty list, skip filtering
        if user_prefs.number_of_roommates is None or len(user_prefs.number_of_roommates) == 0:
            return query
            
        # Create a Q object for OR conditions
        roommate_filter = Q()
        
        # For each preferred number of roommates, add a condition
        for num_roommates in user_prefs.number_of_roommates:
            # Calculate total number of people in the apartment
            # For example, if user wants 2 roommates, they need an apartment with 3 rooms total
            total_people = num_roommates + 1
            
            # Add this condition to our filter
            roommate_filter |= Q(number_of_rooms__gte=total_people)
        
        # Apply the combined filter
        return query.filter(roommate_filter)
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
    if user_prefs and hasattr(user_prefs, 'user_preference_features'):
        # Get the features from user preferences
        feature_ids = user_prefs.user_preference_features.values_list('feature_id', flat=True)
        
        if feature_ids:
            # Filter apartments that have ALL the requested features
            for feature_id in feature_ids:
                query = query.filter(apartment_features__feature_id=feature_id)
                
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
    if user_prefs and hasattr(user_prefs, 'move_in_date') and user_prefs.move_in_date is not None:
        # Only show apartments that are available on or before the user's preferred move-in date
        # This ensures users don't see apartments that aren't available when they need them
        return query.filter(available_entry_date__lte=user_prefs.move_in_date)
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
        # Get apartments the user has already interacted with (always exclude these)
        interacted_apartment_ids = get_interacted_apartments(user_id)
        
        # Base query excluding apartments the user has interacted with
        base_query = Apartment.objects.exclude(id__in=interacted_apartment_ids)
        
        # Get user preferences
        user_prefs = get_user_preferences(user_id)
        if not user_prefs:
            # If no preferences, return all apartments except interacted ones
            return base_query
            
        # Apply all preference-based filters
        filtered_query = base_query
        filtered_query = apply_price_filter(filtered_query, user_prefs)
        filtered_query = apply_city_filter(filtered_query, user_prefs)
        filtered_query = apply_roommates_filter(filtered_query, user_prefs)
        filtered_query = apply_features_filter(filtered_query, user_prefs)
        filtered_query = apply_date_filter(filtered_query, user_prefs)
        filtered_query = apply_max_floor_filter(filtered_query, user_prefs)
        filtered_query = apply_area_filter(filtered_query, user_prefs)

        return filtered_query
        
    except Exception as e:
        logger.error(f"Error in filter_apartments: {str(e)}")
        return Apartment.objects.none()
