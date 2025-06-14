import pytest
from unittest.mock import Mock, patch
from apartments.utils.compatibility import (
    text_field_similarity,
    calculate_question_similarity,
    calculate_user_compatibility,
    get_user_responses,
    get_questions_metadata
)

def test_text_field_similarity_identical():
    """בדיקת דמיון בין שדות טקסט זהים"""
    text1 = "Hello World"
    text2 = "Hello World"
    similarity = text_field_similarity(text1, text2)
    assert similarity == 1.0

def test_text_field_similarity_different():
    """בדיקת דמיון בין שדות טקסט שונים"""
    text1 = "Hello World"
    text2 = "Python Programming"
    similarity = text_field_similarity(text1, text2)
    assert similarity == 0.0

def test_text_field_similarity_partial():
    """בדיקת דמיון בין שדות טקסט עם חפיפה חלקית"""
    text1 = "Hello World"
    text2 = "Hello Python"
    similarity = text_field_similarity(text1, text2)
    assert 0.0 < similarity < 1.0

def test_text_field_similarity_empty():
    """בדיקת דמיון עם שדות טקסט ריקים"""
    assert text_field_similarity("", "") == 0.5  # ציון ניטרלי למחרוזות ריקות
    assert text_field_similarity("Hello", "") == 0.0
    assert text_field_similarity("", "Hello") == 0.0
    assert text_field_similarity(None, None) == 0.5  # ציון ניטרלי ל-None
    assert text_field_similarity("Hello", None) == 0.0
    assert text_field_similarity(None, "Hello") == 0.0

def test_text_field_similarity_hebrew():
    """בדיקת דמיון בשדות טקסט בעברית"""
    text1 = "שלום עולם"
    text2 = "שלום עולם"
    similarity = text_field_similarity(text1, text2)
    assert similarity == 1.0

    text3 = "שלום עולם"
    text4 = "שלום לכולם"
    similarity = text_field_similarity(text3, text4)
    assert 0.0 < similarity < 1.0

@pytest.fixture
def mock_question_metadata():
    """Fixture ליצירת מטא-דאטה של שאלה בודדת"""
    return {
        'type': 'text',
        'weight': 1.0,
        'title': 'Test Question',
        'options': ['1', '2', '3', '4', '5']
    }

def test_calculate_question_similarity_numeric(mock_question_metadata):
    """בדיקת דמיון בשאלות מספריות"""
    mock_question_metadata['type'] = 'radio'
    
    # בדיקת ערכים זהים
    response1 = Mock(numeric_response=5, text_response=None)
    response2 = Mock(numeric_response=5, text_response=None)
    similarity = calculate_question_similarity(1, response1, response2, mock_question_metadata)
    assert similarity == 1.0
    
    # בדיקת ערכים שונים
    response2.numeric_response = 3
    similarity = calculate_question_similarity(1, response1, response2, mock_question_metadata)
    assert 0.0 < similarity < 1.0

def test_calculate_question_similarity_boolean(mock_question_metadata):
    """בדיקת דמיון בשאלות בוליאניות"""
    mock_question_metadata['type'] = 'radio'
    
    # בדיקת ערכים זהים
    response1 = Mock(numeric_response=1, text_response=None)  # True = 1
    response2 = Mock(numeric_response=1, text_response=None)  # True = 1
    similarity = calculate_question_similarity(3, response1, response2, mock_question_metadata)
    assert similarity == 1.0
    
    # בדיקת ערכים שונים
    response2.numeric_response = 5  # False = 5
    similarity = calculate_question_similarity(3, response1, response2, mock_question_metadata)
    assert similarity < 1.0

@patch('apartments.utils.compatibility.get_user_responses')
@patch('apartments.utils.compatibility.get_questions_metadata')
def test_calculate_user_compatibility(mock_get_metadata, mock_get_responses):
    """בדיקת חישוב ציון התאמה בין משתמשים"""
    # יצירת תשובות שונות לכל משתמש
    user1_responses = {
        1: Mock(numeric_response=5, text_response=None),
        2: Mock(numeric_response=None, text_response="Hello"),
        3: Mock(numeric_response=1, text_response=None)
    }
    user2_responses = {
        1: Mock(numeric_response=3, text_response=None),  # שונה
        2: Mock(numeric_response=None, text_response="World"),  # שונה
        3: Mock(numeric_response=1, text_response=None)  # זהה
    }
    
    # הגדרת התנהגות ה-mocks
    mock_get_responses.side_effect = lambda user_id: user1_responses if user_id == 1 else user2_responses
    mock_get_metadata.return_value = {
        1: {"type": "radio", "weight": 1.0, "title": "Question 1"},
        2: {"type": "text", "weight": 1.0, "title": "Question 2"},
        3: {"type": "radio", "weight": 1.0, "title": "Question 3"}
    }
    
    # בדיקת התאמה מלאה (אותו משתמש)
    score = calculate_user_compatibility(1, 1)
    assert score == 1.0
    
    # בדיקת התאמה חלקית (משתמשים שונים)
    score = calculate_user_compatibility(1, 2)
    assert 0.0 < score < 1.0  # ציון חיובי אבל לא מלא

@patch('apartments.utils.compatibility.get_user_responses')
@patch('apartments.utils.compatibility.get_questions_metadata')
def test_calculate_user_compatibility_missing_responses(mock_get_metadata, mock_get_responses):
    """בדיקת חישוב ציון התאמה עם תשובות חסרות"""
    # הגדרת התנהגות ה-mocks עם תשובות חסרות
    mock_get_responses.side_effect = lambda user_id: {
        1: Mock(numeric_response=5, text_response=None)
    } if user_id == 1 else {
        2: Mock(numeric_response=None, text_response="Hello")
    }
    mock_get_metadata.return_value = {
        1: {"type": "radio", "weight": 1.0, "title": "Question 1"},
        2: {"type": "text", "weight": 1.0, "title": "Question 2"}
    }
    
    # בדיקת התאמה עם תשובות חסרות
    score = calculate_user_compatibility(1, 2)
    assert 0.0 < score < 1.0  # ציון חיובי כי יש התאמה חלקית

@patch('apartments.utils.compatibility.get_user_responses')
@patch('apartments.utils.compatibility.get_questions_metadata')
def test_calculate_user_compatibility_no_responses(mock_get_metadata, mock_get_responses):
    """בדיקת חישוב ציון התאמה ללא תשובות"""
    # הגדרת התנהגות ה-mocks עם רשימות ריקות
    mock_get_responses.return_value = {}
    mock_get_metadata.return_value = {}
    
    # בדיקת התאמה ללא תשובות
    score = calculate_user_compatibility(1, 2)
    assert score == 0.5  # ציון ניטרלי כשאין תשובות 