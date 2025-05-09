"""
Main recommendation module for apartment recommendations.
"""
import logging
from django.db.models import Case, When, Value, FloatField

from apartments.models import Apartment
from apartments.utils.filtering import filter_apartments
from apartments.utils.compatibility import calculate_user_compatibility

logger = logging.getLogger(__name__)


def rank_apartments_by_compatibility(filtered_apartments, user_id, limit):
    """
    Rank filtered apartments by compatibility with the user.
    
    Args:
        filtered_apartments: QuerySet of filtered apartments
        user_id: ID of the user searching for apartments
        limit: Maximum number of apartments to return
        
    Returns:
        list: List of apartments sorted by compatibility
    """
    # Calculate compatibility scores
    scored_apartments = []
    
    for apartment in filtered_apartments:
        owner_id = apartment.user_id
        compatibility_score = calculate_user_compatibility(user_id, owner_id)
        scored_apartments.append((apartment, compatibility_score))
    
    # Sort by compatibility score (descending)
    scored_apartments.sort(key=lambda x: x[1], reverse=True)
    
    # Return top N apartments
    return [apt for apt, score in scored_apartments[:limit]]


def convert_to_ordered_queryset(ranked_apartments):
    """
    Convert a list of apartments to a queryset with preserved order.
    
    Args:
        ranked_apartments: List of apartment objects in desired order
        
    Returns:
        QuerySet with preserved order
    """
    if not ranked_apartments:
        return Apartment.objects.none()
        
    # Create a Case expression to preserve the order
    preserved_order = Case(
        *[When(pk=pk, then=Value(pos)) 
          for pos, pk in enumerate([a.pk for a in ranked_apartments])],
        output_field=FloatField()
    )
    
    # Return ordered queryset
    return Apartment.objects.filter(
        pk__in=[a.pk for a in ranked_apartments]
    ).order_by(preserved_order)


def get_recommended_apartments(user_id, limit=10):
    """
    Get recommended apartments for a user based on preferences and compatibility.
    
    Args:
        user_id: The ID of the user to get recommendations for
        limit: Maximum number of apartments to return
        
    Returns:
        QuerySet of recommended Apartment objects
    """
    try:
        # Get filtered apartments based on user preferences
        filtered_apartments = filter_apartments(user_id)
        logger.info(f"Filtered apartments for user {user_id}: {filtered_apartments}")
        
        # If no apartments match the basic criteria, return empty queryset
        if not filtered_apartments.exists():
            return Apartment.objects.none()
        
        # Get list of apartments and convert to Python list for ranking
        apartment_list = list(filtered_apartments)
        
        # Rank apartments by compatibility with the user
        ranked_apartments = rank_apartments_by_compatibility(
            apartment_list, user_id, limit
        )
        logger.info(f"Ranked apartments for user {user_id}: {ranked_apartments}")
        
        # Convert back to a queryset with preserved order
        return convert_to_ordered_queryset(ranked_apartments)
        
    except Exception as e:
        logger.error(f"Error in get_recommended_apartments: {str(e)}")
        return Apartment.objects.none()
