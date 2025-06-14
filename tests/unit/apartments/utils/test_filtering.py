import pytest
from django.db.models import Q
from unittest.mock import Mock, PropertyMock
from apartments.models import Apartment, City
from apartments.utils.filtering import (
    apply_price_filter,
    apply_city_filter,
    apply_area_filter,
    apply_max_floor_filter,
    apply_roommates_filter,
    apply_features_filter,
    apply_date_filter
)

@pytest.fixture
def mock_user_prefs():
    """Fixture ליצירת user preferences מדומה"""
    prefs = Mock()
    prefs.min_price = None
    prefs.max_price = None
    prefs.city = None
    prefs.area = None
    prefs.max_floor = None
    prefs.number_of_roommates = None
    prefs.user_preference_features = Mock()
    prefs.user_preference_features.values_list.return_value = []
    prefs.move_in_date = None
    return prefs

@pytest.fixture
def mock_city():
    """Fixture ליצירת עיר מדומה"""
    city = Mock(spec=City)
    city.id = 1
    city.name = "תל אביב"
    
    # הוספת _meta מורכב
    meta = Mock()
    meta.concrete_model = City
    meta.model = City
    meta.get_parent_list = Mock(return_value=[City])
    city._meta = meta
    
    # הוספת התנהגות של resolve_expression
    city.resolve_expression = Mock(return_value=city)
    city.get_source_expressions = Mock(return_value=[])
    city.filterable = True
    
    # הוספת התנהגות של __eq__ ו-__hash__
    city.__eq__ = lambda self, other: isinstance(other, City) and self.id == other.id
    city.__hash__ = lambda self: hash(self.id)
    
    return city

@pytest.fixture
def base_query():
    """Fixture ליצירת query בסיסי"""
    return Apartment.objects.all()

def test_apply_price_filter(mock_user_prefs, base_query):
    """בדיקת פילטר מחיר"""
    # בדיקת טווח מחיר תקין
    mock_user_prefs.min_price = 1000
    mock_user_prefs.max_price = 5000
    filtered_query = apply_price_filter(base_query, mock_user_prefs)
    assert isinstance(filtered_query, type(base_query))
    
    # בדיקת מחיר מינימום בלבד
    mock_user_prefs.min_price = 1000
    mock_user_prefs.max_price = None
    filtered_query = apply_price_filter(base_query, mock_user_prefs)
    assert isinstance(filtered_query, type(base_query))
    
    # בדיקת מחיר מקסימום בלבד
    mock_user_prefs.min_price = None
    mock_user_prefs.max_price = 5000
    filtered_query = apply_price_filter(base_query, mock_user_prefs)
    assert isinstance(filtered_query, type(base_query))
    
    # בדיקת ללא פילטרים
    mock_user_prefs.min_price = None
    mock_user_prefs.max_price = None
    filtered_query = apply_price_filter(base_query, mock_user_prefs)
    assert filtered_query == base_query

def test_apply_city_filter(mock_user_prefs, base_query, mock_city):
    """בדיקת פילטר עיר"""
    # בדיקת עיר תקינה
    mock_user_prefs.city = mock_city
    filtered_query = apply_city_filter(base_query, mock_user_prefs)
    assert isinstance(filtered_query, type(base_query))
    
    # בדיקת ללא עיר
    mock_user_prefs.city = None
    filtered_query = apply_city_filter(base_query, mock_user_prefs)
    assert filtered_query == base_query

def test_apply_area_filter(mock_user_prefs, base_query):
    """בדיקת פילטר שטח"""
    # בדיקת שטח תקין
    mock_user_prefs.area = "שכונה א"
    filtered_query = apply_area_filter(base_query, mock_user_prefs)
    assert isinstance(filtered_query, type(base_query))
    
    # בדיקת שטח ריק
    mock_user_prefs.area = ""
    filtered_query = apply_area_filter(base_query, mock_user_prefs)
    assert filtered_query == base_query
    
    # בדיקת ללא שטח
    mock_user_prefs.area = None
    filtered_query = apply_area_filter(base_query, mock_user_prefs)
    assert filtered_query == base_query

def test_apply_max_floor_filter(mock_user_prefs, base_query):
    """בדיקת פילטר קומה מקסימלית"""
    # בדיקת קומה תקינה
    mock_user_prefs.max_floor = 5
    filtered_query = apply_max_floor_filter(base_query, mock_user_prefs)
    assert isinstance(filtered_query, type(base_query))
    
    # בדיקת ללא קומה
    mock_user_prefs.max_floor = None
    filtered_query = apply_max_floor_filter(base_query, mock_user_prefs)
    assert filtered_query == base_query

def test_apply_roommates_filter(mock_user_prefs, base_query):
    """בדיקת פילטר שותפים"""
    # בדיקת מספר שותפים תקין
    mock_user_prefs.number_of_roommates = [2]
    filtered_query = apply_roommates_filter(base_query, mock_user_prefs)
    assert isinstance(filtered_query, type(base_query))
    
    # בדיקת רשימה ריקה
    mock_user_prefs.number_of_roommates = []
    filtered_query = apply_roommates_filter(base_query, mock_user_prefs)
    assert filtered_query == base_query
    
    # בדיקת ללא שותפים
    mock_user_prefs.number_of_roommates = None
    filtered_query = apply_roommates_filter(base_query, mock_user_prefs)
    assert filtered_query == base_query

def test_apply_features_filter(mock_user_prefs, base_query):
    """בדיקת פילטר תכונות"""
    # בדיקת רשימת תכונות תקינה
    mock_user_prefs.user_preference_features.values_list.return_value = [1, 2, 3]
    filtered_query = apply_features_filter(base_query, mock_user_prefs)
    assert isinstance(filtered_query, type(base_query))
    
    # בדיקת רשימה ריקה
    mock_user_prefs.user_preference_features.values_list.return_value = []
    filtered_query = apply_features_filter(base_query, mock_user_prefs)
    assert filtered_query == base_query

def test_apply_date_filter(mock_user_prefs, base_query):
    """בדיקת פילטר תאריך"""
    # בדיקת תאריך תקין
    mock_user_prefs.move_in_date = "2024-09-01"
    filtered_query = apply_date_filter(base_query, mock_user_prefs)
    assert isinstance(filtered_query, type(base_query))
    
    # בדיקת ללא תאריך
    mock_user_prefs.move_in_date = None
    filtered_query = apply_date_filter(base_query, mock_user_prefs)
    assert filtered_query == base_query

def test_combine_filters(mock_user_prefs, base_query, mock_city):
    """בדיקת שילוב מספר פילטרים"""
    # הגדרת העדפות משתמש
    mock_user_prefs.min_price = 1000
    mock_user_prefs.max_price = 5000
    mock_user_prefs.city = mock_city
    mock_user_prefs.area = "שכונה א"
    
    # שילוב מספר פילטרים
    filtered_query = apply_price_filter(base_query, mock_user_prefs)
    filtered_query = apply_city_filter(filtered_query, mock_user_prefs)
    filtered_query = apply_area_filter(filtered_query, mock_user_prefs)
    
    assert isinstance(filtered_query, type(base_query))
    # בדיקה שהפילטרים לא מבטלים אחד את השני
    assert filtered_query != base_query

def test_filter_edge_cases(mock_user_prefs, base_query):
    """בדיקת מקרי קצה בפילטרים"""
    # בדיקת ערכים שליליים במחיר
    mock_user_prefs.min_price = -1000
    mock_user_prefs.max_price = -5000
    filtered_query = apply_price_filter(base_query, mock_user_prefs)
    assert isinstance(filtered_query, type(base_query))
    
    # בדיקת ערכים אפס במחיר
    mock_user_prefs.min_price = 0
    mock_user_prefs.max_price = 0
    filtered_query = apply_price_filter(base_query, mock_user_prefs)
    assert isinstance(filtered_query, type(base_query))
    
    # בדיקת ערכים גדולים מאוד במחיר
    mock_user_prefs.min_price = 1000000
    mock_user_prefs.max_price = 2000000
    filtered_query = apply_price_filter(base_query, mock_user_prefs)
    assert isinstance(filtered_query, type(base_query))
    
    # בדיקת תאריך None
    mock_user_prefs.move_in_date = None
    filtered_query = apply_date_filter(base_query, mock_user_prefs)
    assert filtered_query == base_query
    
    # בדיקת תאריך בפורמט לא תקין
    mock_user_prefs.move_in_date = "not-a-date"
    with pytest.raises(Exception):  # נצפה לקבל שגיאה כלשהי
        apply_date_filter(base_query, mock_user_prefs) 