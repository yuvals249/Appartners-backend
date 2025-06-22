from unittest.mock import Mock, patch
from apartments.utils.compatibility import (
    text_field_similarity,
    calculate_question_similarity,
    calculate_user_compatibility,
)


def test_text_field_similarity_identical():
    """Test similarity between identical text fields"""
    text1 = "Hello World"
    text2 = "Hello World"
    similarity = text_field_similarity(text1, text2)
    assert similarity == 1.0

def test_text_field_similarity_different():
    """Test similarity between different text fields"""
    text1 = "Hello World"
    text2 = "Python Programming"
    similarity = text_field_similarity(text1, text2)
    assert similarity == 0.0

def test_text_field_similarity_partial():
    """Test similarity between partially overlapping text fields"""
    text1 = "Hello World"
    text2 = "Hello Python"
    similarity = text_field_similarity(text1, text2)
    assert 0.0 < similarity < 1.0

def test_text_field_similarity_empty():
    """Test similarity with empty text fields"""
    assert text_field_similarity("", "") == 0.5  # Neutral score for empty strings
    assert text_field_similarity("Hello", "") == 0.0
    assert text_field_similarity("", "Hello") == 0.0
    assert text_field_similarity(None, None) == 0.5  # Neutral score for None
    assert text_field_similarity("Hello", None) == 0.0
    assert text_field_similarity(None, "Hello") == 0.0

def test_text_field_similarity_hebrew():
    """Test similarity in Hebrew text fields"""
    text1 = "שלום עולם"
    text2 = "שלום עולם"
    similarity = text_field_similarity(text1, text2)
    assert similarity == 1.0

    text3 = "שלום עולם"
    text4 = "שלום לכולם"
    similarity = text_field_similarity(text3, text4)
    assert 0.0 < similarity < 1.0

def test_calculate_question_similarity_numeric(mock_question_metadata):
    """Test similarity in numeric questions"""
    mock_question_metadata['type'] = 'radio'
    
    # Test identical values
    response1 = Mock(numeric_response=5, text_response=None)
    response2 = Mock(numeric_response=5, text_response=None)
    similarity = calculate_question_similarity(1, response1, response2, mock_question_metadata)
    assert similarity == 1.0
    
    # Test different values
    response2.numeric_response = 3
    similarity = calculate_question_similarity(1, response1, response2, mock_question_metadata)
    assert 0.0 < similarity < 1.0

def test_calculate_question_similarity_boolean(mock_question_metadata):
    """Test similarity in boolean questions"""
    mock_question_metadata['type'] = 'radio'
    
    # Test identical values
    response1 = Mock(numeric_response=1, text_response=None)  # True = 1
    response2 = Mock(numeric_response=1, text_response=None)  # True = 1
    similarity = calculate_question_similarity(3, response1, response2, mock_question_metadata)
    assert similarity == 1.0
    
    # Test different values
    response2.numeric_response = 5  # False = 5
    similarity = calculate_question_similarity(3, response1, response2, mock_question_metadata)
    assert similarity < 1.0

@patch('apartments.utils.compatibility.get_user_responses')
@patch('apartments.utils.compatibility.get_questions_metadata')
def test_calculate_user_compatibility(mock_get_metadata, mock_get_responses):
    """Test compatibility score calculation between users"""
    # Create different answers for each user
    user1_responses = {
        1: Mock(numeric_response=5, text_response=None),
        2: Mock(numeric_response=None, text_response="Hello"),
        3: Mock(numeric_response=1, text_response=None)
    }
    user2_responses = {
        1: Mock(numeric_response=3, text_response=None),  # Different
        2: Mock(numeric_response=None, text_response="World"),  # Different
        3: Mock(numeric_response=1, text_response=None)  # Identical
    }
    
    # Define mock behaviors
    mock_get_responses.side_effect = lambda user_id: user1_responses if user_id == 1 else user2_responses
    mock_get_metadata.return_value = {
        1: {"type": "radio", "weight": 1.0, "title": "Question 1"},
        2: {"type": "text", "weight": 1.0, "title": "Question 2"},
        3: {"type": "radio", "weight": 1.0, "title": "Question 3"}
    }
    
    # Test full compatibility (same user)
    score = calculate_user_compatibility(1, 1)
    assert score == 1.0
    
    # Test partial compatibility (different users)
    score = calculate_user_compatibility(1, 2)
    assert 0.0 < score < 1.0  # Positive but not full score

@patch('apartments.utils.compatibility.get_user_responses')
@patch('apartments.utils.compatibility.get_questions_metadata')
def test_calculate_user_compatibility_missing_responses(mock_get_metadata, mock_get_responses):
    """Test compatibility score calculation with missing responses"""
    # Define mock behaviors with missing responses
    mock_get_responses.side_effect = lambda user_id: {
        1: Mock(numeric_response=5, text_response=None)
    } if user_id == 1 else {
        2: Mock(numeric_response=None, text_response="Hello")
    }
    mock_get_metadata.return_value = {
        1: {"type": "radio", "weight": 1.0, "title": "Question 1"},
        2: {"type": "text", "weight": 1.0, "title": "Question 2"}
    }
    
    # Test compatibility with missing responses
    score = calculate_user_compatibility(1, 2)
    assert 0.0 < score < 1.0  # Positive but not full score

@patch('apartments.utils.compatibility.get_user_responses')
@patch('apartments.utils.compatibility.get_questions_metadata')
def test_calculate_user_compatibility_no_responses(mock_get_metadata, mock_get_responses):
    """Test compatibility score calculation with no responses"""
    # Define mock behaviors with empty lists
    mock_get_responses.return_value = {}
    mock_get_metadata.return_value = {}
    
    # Test compatibility with no responses
    score = calculate_user_compatibility(1, 2)
    assert score == 0.5  # Neutral score when there are no responses 