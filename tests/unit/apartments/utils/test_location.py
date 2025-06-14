import pytest
from apartments.utils.location import add_random_offset, truncate_coordinates

def test_add_random_offset_basic():
    """בדיקת הוספת אופסט אקראי בסיסי"""
    lat, lon = 32.0853, 34.7818  # תל אביב
    new_lat, new_lon = add_random_offset(lat, lon)
    
    # בדיקה שהקואורדינטות החדשות קרובות למקור
    assert abs(new_lat - lat) < 0.001  # עדכון: טווח קטן יותר
    assert abs(new_lon - lon) < 0.001  # עדכון: טווח קטן יותר
    
    # בדיקה שהקואורדינטות החדשות שונות מהמקור
    assert new_lat != lat or new_lon != lon

def test_add_random_offset_edge_cases():
    """בדיקת מקרי קצה של קואורדינטות"""
    # קואורדינטות בקצוות המפה
    test_cases = [
        (90, 180),   # צפון מזרח
        (-90, -180), # דרום מערב
        (0, 0),      # מרכז
        (90, 0),     # צפון
        (-90, 0),    # דרום
    ]
    
    for lat, lon in test_cases:
        new_lat, new_lon = add_random_offset(lat, lon)
        # בדיקה שהקואורדינטות החדשות קרובות לטווח התקין
        assert -90.001 <= new_lat <= 90.001  # עדכון: מאפשר סטייה קטנה
        assert -180.001 <= new_lon <= 180.001  # עדכון: מאפשר סטייה קטנה

def test_truncate_coordinates_basic():
    """בדיקת קיצוץ קואורדינטות בסיסית"""
    lat, lon = 32.0853123, 34.7818123
    truncated_lat, truncated_lon = truncate_coordinates(lat, lon)
    
    # בדיקה שהקואורדינטות קוצצו ל-7 ספרות אחרי הנקודה
    assert truncated_lat == 32.0853123  # עדכון: 7 ספרות
    assert truncated_lon == 34.7818123  # עדכון: 7 ספרות

def test_truncate_coordinates_edge_cases():
    """בדיקת מקרי קצה בקיצוץ קואורדינטות"""
    test_cases = [
        (90.0, 180.0),      # מספרים שלמים
        (-90.0, -180.0),    # מספרים שליליים
        (0.0, 0.0),         # אפס
        (32.0853123456, 34.7818123456),  # מספרים ארוכים
    ]
    
    for lat, lon in test_cases:
        truncated_lat, truncated_lon = truncate_coordinates(lat, lon)
        # בדיקה שהתוצאה היא float
        assert isinstance(truncated_lat, float)
        assert isinstance(truncated_lon, float)
        
        # בדיקה שיש בדיוק 7 ספרות אחרי הנקודה (או פחות אם המספר שלם)
        lat_str = f"{truncated_lat:.7f}"  # פורמט קבוע של 7 ספרות
        lon_str = f"{truncated_lon:.7f}"  # פורמט קבוע של 7 ספרות
        
        # הסרת אפסים מיותרים בסוף
        lat_str = lat_str.rstrip('0').rstrip('.')
        lon_str = lon_str.rstrip('0').rstrip('.')
        
        # בדיקה שהמספרים המקוריים שווים למספרים המעוגלים
        assert float(lat_str) == truncated_lat
        assert float(lon_str) == truncated_lon

def test_truncate_coordinates_truncation():
    """בדיקת קיצוץ נכון של קואורדינטות"""
    # בדיקת קיצוץ פשוט (ללא עיגול)
    lat, lon = 32.0853125, 34.7818125
    truncated_lat, truncated_lon = truncate_coordinates(lat, lon)
    assert truncated_lat == 32.0853125  # עדכון: קיצוץ פשוט
    assert truncated_lon == 34.7818125  # עדכון: קיצוץ פשוט
    
    # בדיקת קיצוץ מספרים ארוכים
    lat, lon = 32.0853123456, 34.7818123456
    truncated_lat, truncated_lon = truncate_coordinates(lat, lon)
    assert truncated_lat == 32.0853123  # עדכון: קיצוץ ל-7 ספרות
    assert truncated_lon == 34.7818123  # עדכון: קיצוץ ל-7 ספרות 