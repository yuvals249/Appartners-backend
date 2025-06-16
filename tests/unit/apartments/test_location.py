from apartments.utils.location import add_random_offset, truncate_coordinates

def test_add_random_offset_basic():
    """Test basic random offset addition"""
    lat, lon = 32.0853, 34.7818  # Tel Aviv
    new_lat, new_lon = add_random_offset(lat, lon)
    
    assert abs(new_lat - lat) < 0.001
    assert abs(new_lon - lon) < 0.001
    
    assert new_lat != lat or new_lon != lon

def test_add_random_offset_edge_cases():
    """Test edge cases for coordinate offsets"""
    test_cases = [
        (90, 180),
        (-90, -180),
        (0, 0),
        (90, 0),
        (-90, 0),
    ]
    
    for lat, lon in test_cases:
        new_lat, new_lon = add_random_offset(lat, lon)
        assert -90.001 <= new_lat <= 90.001
        assert -180.001 <= new_lon <= 180.001

def test_truncate_coordinates_basic():
    """Test basic coordinate truncation"""
    lat, lon = 32.0853123, 34.7818123
    truncated_lat, truncated_lon = truncate_coordinates(lat, lon)
    
    assert truncated_lat == 32.0853123
    assert truncated_lon == 34.7818123

def test_truncate_coordinates_edge_cases():
    """Test edge cases for coordinate truncation"""
    test_cases = [
        (90.0, 180.0),
        (-90.0, -180.0),
        (0.0, 0.0),
        (32.0853123456, 34.7818123456),
    ]
    
    for lat, lon in test_cases:
        truncated_lat, truncated_lon = truncate_coordinates(lat, lon)

        assert isinstance(truncated_lat, float)
        assert isinstance(truncated_lon, float)
        
        lat_str = f"{truncated_lat:.7f}"
        lon_str = f"{truncated_lon:.7f}"
        
        lat_str = lat_str.rstrip('0').rstrip('.')
        lon_str = lon_str.rstrip('0').rstrip('.')
        
        assert float(lat_str) == truncated_lat
        assert float(lon_str) == truncated_lon

def test_truncate_coordinates_truncation():
    """Test proper coordinate truncation"""
    lat, lon = 32.0853125, 34.7818125
    truncated_lat, truncated_lon = truncate_coordinates(lat, lon)
    assert truncated_lat == 32.0853125
    assert truncated_lon == 34.7818125
    
    lat, lon = 32.0853123456, 34.7818123456
    truncated_lat, truncated_lon = truncate_coordinates(lat, lon)
    assert truncated_lat == 32.0853123
    assert truncated_lon == 34.7818123
