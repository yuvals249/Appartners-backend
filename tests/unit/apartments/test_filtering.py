from apartments.utils.filtering import (
    apply_price_filter,
    apply_city_filter,
    apply_area_filter,
    apply_max_floor_filter,
    apply_roommates_filter,
    apply_features_filter,
    apply_date_filter
)


def test_apply_price_filter(mock_user_prefs, base_query):
    """Test price filter"""
    # Test valid price range
    mock_user_prefs.min_price = 1000
    mock_user_prefs.max_price = 5000
    filtered_query = apply_price_filter(base_query, mock_user_prefs)
    assert isinstance(filtered_query, type(base_query))
    
    # Test minimum price only
    mock_user_prefs.min_price = 1000
    mock_user_prefs.max_price = None
    filtered_query = apply_price_filter(base_query, mock_user_prefs)
    assert isinstance(filtered_query, type(base_query))
    
    # Test maximum price only
    mock_user_prefs.min_price = None
    mock_user_prefs.max_price = 5000
    filtered_query = apply_price_filter(base_query, mock_user_prefs)
    assert isinstance(filtered_query, type(base_query))
    
    # Test without filters
    mock_user_prefs.min_price = None
    mock_user_prefs.max_price = None
    filtered_query = apply_price_filter(base_query, mock_user_prefs)
    assert filtered_query == base_query

def test_apply_city_filter(mock_user_prefs, base_query, mock_city):
    """Test city filter"""
    # Test valid city
    mock_user_prefs.city = mock_city
    filtered_query = apply_city_filter(base_query, mock_user_prefs)
    assert isinstance(filtered_query, type(base_query))
    
    # Test without city
    mock_user_prefs.city = None
    filtered_query = apply_city_filter(base_query, mock_user_prefs)
    assert filtered_query == base_query

def test_apply_area_filter(mock_user_prefs, base_query):
    """Test area filter"""
    # Test valid area
    mock_user_prefs.area = "Neighborhood A"
    filtered_query = apply_area_filter(base_query, mock_user_prefs)
    assert isinstance(filtered_query, type(base_query))
    
    # Test empty area
    mock_user_prefs.area = ""
    filtered_query = apply_area_filter(base_query, mock_user_prefs)
    assert filtered_query == base_query
    
    # Test without area
    mock_user_prefs.area = None
    filtered_query = apply_area_filter(base_query, mock_user_prefs)
    assert filtered_query == base_query

def test_apply_max_floor_filter(mock_user_prefs, base_query):
    """Test maximum floor filter"""
    # Test valid floor
    mock_user_prefs.max_floor = 5
    filtered_query = apply_max_floor_filter(base_query, mock_user_prefs)
    assert isinstance(filtered_query, type(base_query))
    
    # Test without floor
    mock_user_prefs.max_floor = None
    filtered_query = apply_max_floor_filter(base_query, mock_user_prefs)
    assert filtered_query == base_query

def test_apply_roommates_filter(mock_user_prefs, base_query):
    """Test roommates filter"""
    # Test valid number of roommates
    mock_user_prefs.number_of_roommates = [2]
    filtered_query = apply_roommates_filter(base_query, mock_user_prefs)
    assert isinstance(filtered_query, type(base_query))
    
    # Test empty list
    mock_user_prefs.number_of_roommates = []
    filtered_query = apply_roommates_filter(base_query, mock_user_prefs)
    assert filtered_query == base_query
    
    # Test without roommates
    mock_user_prefs.number_of_roommates = None
    filtered_query = apply_roommates_filter(base_query, mock_user_prefs)
    assert filtered_query == base_query

def test_apply_features_filter(mock_user_prefs, base_query):
    """Test features filter"""
    # Test valid features list
    mock_user_prefs.user_preference_features.values_list.return_value = [1, 2, 3]
    filtered_query = apply_features_filter(base_query, mock_user_prefs)
    assert isinstance(filtered_query, type(base_query))
    
    # Test empty list
    mock_user_prefs.user_preference_features.values_list.return_value = []
    filtered_query = apply_features_filter(base_query, mock_user_prefs)
    assert filtered_query == base_query

def test_apply_date_filter(mock_user_prefs, base_query):
    """Test date filter"""
    # Test valid date
    mock_user_prefs.move_in_date = "2024-09-01"
    filtered_query = apply_date_filter(base_query, mock_user_prefs)
    assert isinstance(filtered_query, type(base_query))
    
    # Test without date
    mock_user_prefs.move_in_date = None
    filtered_query = apply_date_filter(base_query, mock_user_prefs)
    assert filtered_query == base_query

def test_combine_filters(mock_user_prefs, base_query, mock_city):
    """Test combining multiple filters"""
    # Set user preferences
    mock_user_prefs.min_price = 1000
    mock_user_prefs.max_price = 5000
    mock_user_prefs.city = mock_city
    mock_user_prefs.area = "Neighborhood A"

    # Combine multiple filters
    filtered_query = apply_price_filter(base_query, mock_user_prefs)
    filtered_query = apply_city_filter(filtered_query, mock_user_prefs)
    filtered_query = apply_area_filter(filtered_query, mock_user_prefs)

    assert isinstance(filtered_query, type(base_query))
    # Verify that filter was called for each filter
    assert base_query.filter.call_count >= 3

def test_filter_edge_cases(mock_user_prefs, base_query):
    """Test edge cases in filters"""
    # Test negative price values
    mock_user_prefs.min_price = -1000
    mock_user_prefs.max_price = -5000
    filtered_query = apply_price_filter(base_query, mock_user_prefs)
    assert isinstance(filtered_query, type(base_query))

    # Test zero price values
    mock_user_prefs.min_price = 0
    mock_user_prefs.max_price = 0
    filtered_query = apply_price_filter(base_query, mock_user_prefs)
    assert isinstance(filtered_query, type(base_query))

    # Test very large price values
    mock_user_prefs.min_price = 1000000
    mock_user_prefs.max_price = 2000000
    filtered_query = apply_price_filter(base_query, mock_user_prefs)
    assert isinstance(filtered_query, type(base_query))

    # Test None date
    mock_user_prefs.move_in_date = None
    filtered_query = apply_date_filter(base_query, mock_user_prefs)
    assert filtered_query == base_query

    # Test invalid date format
    mock_user_prefs.move_in_date = "not-a-date"
    filtered_query = apply_date_filter(base_query, mock_user_prefs)
    assert filtered_query == base_query 