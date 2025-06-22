import pytest
from apartments.utils.recommendation import (
    rank_apartments_by_compatibility,
)
from tests.unit.conftest import MockApartment


def test_rank_apartments_by_compatibility_empty(mock_user_id):
    """Test ranking apartments with an empty list"""
    ranked_apartments = rank_apartments_by_compatibility([], mock_user_id, limit=5)
    assert isinstance(ranked_apartments, list)
    assert len(ranked_apartments) == 0

def test_rank_apartments_by_compatibility_single(mock_user_id):
    """Test ranking apartments with a single apartment"""
    apartments = [MockApartment(1, 0.8)]
    ranked_apartments = rank_apartments_by_compatibility(apartments, mock_user_id, limit=1)
    assert len(ranked_apartments) == 1
    assert ranked_apartments[0][0].id == 1
    # Check that the score is between 0 and 1
    assert 0 <= ranked_apartments[0][1] <= 1

def test_rank_apartments_by_compatibility_equal_scores(mock_user_id):
    """Test ranking apartments with identical compatibility scores"""
    apartments = [
        MockApartment(1, 0.8),
        MockApartment(2, 0.8),
        MockApartment(3, 0.8)
    ]
    ranked_apartments = rank_apartments_by_compatibility(apartments, mock_user_id, limit=3)
    assert len(ranked_apartments) == 3
    # Check that all scores are between 0 and 1
    assert all(0 <= score <= 1 for _, score in ranked_apartments)
