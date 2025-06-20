"""
User compatibility utilities for apartment recommendations.
Implements a weighted hybrid approach for questionnaire matching.
"""
import logging
from difflib import SequenceMatcher
from users.models.questionnaire import UserResponse, Question

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


def get_questions_metadata():
    """
    Get metadata for all questions.
    
    Returns:
        dict: Dictionary of question metadata keyed by question ID
    """
    questions = Question.objects.all()
    metadata = {}
    
    for q in questions:
        metadata[q.id] = {
            'type': q.question_type,
            'weight': q.weight,
            'options': q.options,
            'order': q.order,
            'title': q.title  # Changed from 'text' to 'title' to match the model
        }
    
    return metadata


def text_field_similarity(text1, text2):
    """
    Calculate similarity between two text fields.
    
    Args:
        text1: First text string
        text2: Second text string
        
    Returns:
        float: Similarity score between 0 and 1
    """
    # Check for None, empty strings, or 'None' string values
    if text1 is None or text2 is None or text1 == '' or text2 == '' or text1 == 'None' or text2 == 'None':
        # If both are missing/empty/None, consider it neutral (0.5) rather than dissimilar
        if ((text1 is None or text1 == '' or text1 == 'None') and 
            (text2 is None or text2 == '' or text2 == 'None')):
            return 0.5
        # If only one is missing, it's a mismatch
        return 0.0
        
    # Normalize texts
    t1 = str(text1).lower().strip()
    t2 = str(text2).lower().strip()
    
    # Exact match
    if t1 == t2:
        return 1.0
    
    # For very short strings, use sequence matcher
    if len(t1) < 5 or len(t2) < 5:
        return SequenceMatcher(None, t1, t2).ratio()
    
    # For longer strings, use word-based comparison
    words1 = set(t1.split())
    words2 = set(t2.split())
    
    # Calculate Jaccard similarity of words
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    if union == 0:
        return 0.0
    
    return intersection / union


def calculate_question_similarity(q_id, response1, response2, q_metadata):
    """
    Calculate similarity for a specific question based on its type.
    
    Args:
        q_id: Question ID
        response1: First user's response
        response2: Second user's response
        q_metadata: Question metadata
        
    Returns:
        float: Similarity score between 0 and 1
    """
    q_type = q_metadata.get('type', 'radio')
    q_title = q_metadata.get('title', f'Question {q_id}')
    
    # Log the question we're comparing

    # Handle text questions
    if q_type == 'text':
        # Skip Question 1 (major/field of study) as requested
        if q_id == 1:
            return 0.0  # This will be filtered out in the main function
            
        # Year
        elif q_id == 2:
            # Exact match for year is preferred, but adjacent years get partial credit
            year1 = response1.text_response
            year2 = response2.text_response
            

            # Handle None/empty values
            if year1 is None or year1 == '' or year1 == 'None' or year2 is None or year2 == '' or year2 == 'None':
                return 0.0
            
            if year1 == year2:
                return 1.0
                
            # Try to parse as integers for year comparison
            try:
                y1 = int(year1)
                y2 = int(year2)
                diff = abs(y1 - y2)
                
                # Exact match
                if diff == 0:
                    return 1.0
                # Adjacent years (1 year apart)
                elif diff == 1:
                    return 0.8
                # 2 years apart
                elif diff == 2:
                    return 0.3
                # More than 2 years apart
                else:
                    return 0.0
            except (ValueError, TypeError):
                # If not parseable as integers, return 0
                return 0.0
    
    # Handle radio/numeric questions
    else:
        # Ensure we have numeric responses
        if response1.numeric_response is None or response2.numeric_response is None:
            return 0.0
            
        value1 = response1.numeric_response
        value2 = response2.numeric_response

        # Calculate absolute difference
        max_scale = 4  # Maximum possible difference on a 5-point scale (1-5)
        difference = abs(value1 - value2)

        # Questions where exact match is critical
        if q_id in [8]:  # Study environment importance
            # Very little partial credit - these are critical
            similarity = 1.0 if difference == 0 else (0.3 if difference == 1 else 0.0)
            return similarity
        # Standard questions where closeness matters
        else:
            # Linear scale for partial credit
            similarity = max(0, 1.0 - (difference / max_scale))
            return similarity


def calculate_user_compatibility(user_id1, user_id2):
    """
    Calculate compatibility score between two users based on questionnaire.
    Uses a weighted hybrid approach that handles different question types appropriately.
    
    Args:
        user_id1: ID of the first user
        user_id2: ID of the second user
        
    Returns:
        float or dict: Compatibility score between 0 and 1, or detailed results if detailed=True
    """
    try:

        # Get responses for both users
        user1_responses = get_user_responses(user_id1)
        user2_responses = get_user_responses(user_id2)
        
        # Get question metadata
        questions_metadata = get_questions_metadata()

        # If either user has no responses, return a neutral score
        if not user1_responses or not user2_responses:
            return 0.5
        
        # Calculate similarity for each common question
        common_questions = set(user1_responses.keys()) & set(user2_responses.keys())

        question_scores = {}
        total_weight = 0
        weighted_score = 0
        
        # Count how many questions have actual answers from both users
        valid_questions = 0
        
        for q_id in sorted(common_questions):  # Sort for consistent logging
            # Skip Question 1 (major/field of study) as requested
            if q_id == 1:
                continue
                
            if q_id not in questions_metadata:
                continue
                
            resp1 = user1_responses[q_id]
            resp2 = user2_responses[q_id]
            q_meta = questions_metadata[q_id]
            q_type = q_meta.get('type', 'radio')
            
            # Skip questions where both users have no meaningful response
            if q_type == 'text' and ((resp1.text_response is None or resp1.text_response == '' or resp1.text_response == 'None') and 
                                     (resp2.text_response is None or resp2.text_response == '' or resp2.text_response == 'None')):
                continue
                
            if q_type != 'text' and (resp1.numeric_response is None and resp2.numeric_response is None):
                continue
            
            # Get weight, default to 1.0 if not specified
            weight = q_meta.get('weight', 1.0)
            # Calculate similarity for this question
            similarity = calculate_question_similarity(q_id, resp1, resp2, q_meta)
            
            # Store individual question score
            question_scores[q_id] = {
                'similarity': similarity,
                'weight': weight
            }
            
            # Add to weighted total
            weighted_contribution = similarity * weight
            weighted_score += weighted_contribution
            total_weight += weight
            valid_questions += 1
            

        # Calculate overall score
        if total_weight == 0 or valid_questions == 0:
            return 0.5  # Return neutral score if no weights
        
        overall_score = weighted_score / total_weight
        return overall_score
            
    except Exception as e:
        logger.error(f"Error calculating user compatibility: {str(e)}")
        return 0.5  # Return neutral score on error