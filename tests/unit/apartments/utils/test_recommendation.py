import pytest
from django.db.models import Q, QuerySet
from apartments.models import Apartment
from apartments.utils.recommendation import (
    rank_apartments_by_compatibility,
    convert_to_ordered_queryset,
)

class MockApartment:
    def __init__(self, id, compatibility_score, user_id=1):
        self.id = id
        self.pk = id
        self.compatibility_score = compatibility_score
        self.user_id = user_id

@pytest.fixture
def mock_apartments():
    """Fixture ליצירת דירות מדומות לבדיקות"""
    return [
        MockApartment(1, 0.8),
        MockApartment(2, 0.6),
        MockApartment(3, 0.9),
        MockApartment(4, 0.7),
        MockApartment(5, 0.5)
    ]

@pytest.fixture
def mock_user_id():
    """Fixture ליצירת מזהה משתמש מדומה"""
    return 1

def test_rank_apartments_by_compatibility_empty(mock_user_id):
    """בדיקת דירוג דירות עם רשימה ריקה"""
    ranked_apartments = rank_apartments_by_compatibility([], mock_user_id, limit=5)
    assert isinstance(ranked_apartments, list)
    assert len(ranked_apartments) == 0

def test_rank_apartments_by_compatibility_single(mock_user_id):
    """בדיקת דירוג דירות עם דירה אחת"""
    apartments = [MockApartment(1, 0.8)]
    ranked_apartments = rank_apartments_by_compatibility(apartments, mock_user_id, limit=1)
    assert len(ranked_apartments) == 1
    assert ranked_apartments[0][0].id == 1
    # בדיקה שהציון הוא בין 0 ל-1
    assert 0 <= ranked_apartments[0][1] <= 1

def test_rank_apartments_by_compatibility_equal_scores(mock_user_id):
    """בדיקת דירוג דירות עם ציוני התאמה זהים"""
    apartments = [
        MockApartment(1, 0.8),
        MockApartment(2, 0.8),
        MockApartment(3, 0.8)
    ]
    ranked_apartments = rank_apartments_by_compatibility(apartments, mock_user_id, limit=3)
    assert len(ranked_apartments) == 3
    # בדיקה שכל הציונים הם בין 0 ל-1
    assert all(0 <= score <= 1 for _, score in ranked_apartments)

def test_convert_to_ordered_queryset_empty():
    """בדיקת המרה ל-QuerySet ממוין עם רשימה ריקה"""
    ordered_qs = convert_to_ordered_queryset([])
    assert isinstance(ordered_qs, QuerySet)
    assert len(ordered_qs) == 0
