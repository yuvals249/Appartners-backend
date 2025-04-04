"""
User compatibility utilities for apartment recommendations.
"""
import logging
import numpy as np
from users.models.questionnaire import UserResponse
from apartments.utils.text_similarity import calculate_text_similarity

logger = logging.getLogger(__name__)


def get_user_responses(user_id):
    """
    Get a user's questionnaire responses.
    
    Args:
        user_id: ID of the user
        
    Returns:
        dict: Dictionary of responses keyed by question ID
    """
    responses = UserResponse.objects.filter(user_id=user_id).select_related('question')
    return {resp.question.id: resp for resp in responses}


def check_response_validity(resp1, resp2):
    """
    Check if both responses are valid for comparison.
    
    Args:
        resp1: First user response
        resp2: Second user response
        
    Returns:
        bool: True if both responses are valid, False otherwise
    """
    # For now, only compare numeric responses
    if resp1.numeric_response is None or resp2.numeric_response is None:
        return False
    
    return True


def cosine_similarity(vector1, vector2, weights=None):
    """
    Calculate cosine similarity between two vectors with optional weights.
    
    Args:
        vector1: First vector
        vector2: Second vector
        weights: Optional weights for each dimension
        
    Returns:
        float: Cosine similarity between 0 and 1
    """
    # Apply weights if provided
    if weights is not None:
        vector1 = np.multiply(vector1, weights)
        vector2 = np.multiply(vector2, weights)
    
    # Calculate dot product
    dot_product = np.dot(vector1, vector2)
    
    # Calculate magnitudes
    magnitude1 = np.sqrt(np.sum(np.square(vector1)))
    magnitude2 = np.sqrt(np.sum(np.square(vector2)))
    
    # Avoid division by zero
    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    
    # Calculate cosine similarity
    return dot_product / (magnitude1 * magnitude2)


def calculate_user_compatibility(user_id1, user_id2):
    """
    Calculate compatibility score between two users based on questionnaire.
    
    Args:
        user_id1: ID of the first user
        user_id2: ID of the second user
        
    Returns:
        float: Compatibility score between 0 and 1
    """
    try:
        # Get responses for both users
        user1_responses = get_user_responses(user_id1)
        user2_responses = get_user_responses(user_id2)
        
        # If either user has no responses, return a neutral score
        if not user1_responses or not user2_responses:
            return 0.5
        
        # Find common questions with numeric responses
        common_questions = []
        numeric_responses1 = []
        numeric_responses2 = []
        weights = []
        
        for q_id in set(user1_responses.keys()) & set(user2_responses.keys()):
            resp1 = user1_responses[q_id]
            resp2 = user2_responses[q_id]
            
            # Skip invalid responses
            if not check_response_validity(resp1, resp2):
                continue
                
            # Add to vectors for cosine similarity
            common_questions.append(q_id)
            numeric_responses1.append(resp1.numeric_response)
            numeric_responses2.append(resp2.numeric_response)
            weights.append(resp1.question.weight)
        
        # If no common questions with valid responses, return neutral score
        if not common_questions:
            return 0.5
            
        # Convert to numpy arrays
        vector1 = np.array(numeric_responses1)
        vector2 = np.array(numeric_responses2)
        weights = np.array(weights)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(vector1, vector2, weights)
        
        return similarity
            
    except Exception as e:
        logger.error(f"Error calculating user compatibility: {str(e)}")
        return 0.5  # Return neutral score on error


# Keep the text comparison code but don't use it for now
def calculate_text_similarity_disabled(text1, text2):
    """
    Calculate similarity between two text strings.
    This function is currently disabled but kept for future use.
    
    Args:
        text1: First text string
        text2: Second text string
        
    Returns:
        float: Similarity score between 0 and 1
    """
    return calculate_text_similarity(text1, text2)
