from apartments.utils.text_similarity import preprocess_text, calculate_text_similarity


def test_preprocess_text_basic():
    """Test basic text handling"""
    text = "Hello World! This is a TEST."
    result = preprocess_text(text)
    assert result == "hello world this is a test"
    assert isinstance(result, str)

def test_preprocess_text_empty():
    """Test handling of empty text"""
    assert preprocess_text("") == ""
    assert preprocess_text("   ") == ""
    assert preprocess_text(None) == ""

def test_preprocess_text_special_chars():
    """Test handling of special characters"""
    text = "Hello! @#$%^&*() World... Test123"
    result = preprocess_text(text)
    assert result == "hello world test123"
    assert "@" not in result
    assert "..." not in result
    assert "123" in result

def test_preprocess_text_hebrew():
    """Test handling of Hebrew text"""
    text = "שלום עולם! זהו מבחן."
    result = preprocess_text(text)
    assert result == "שלום עולם זהו מבחן"
    assert "!" not in result
    assert "." not in result

def test_calculate_text_similarity_identical():
    """Test similarity between identical texts"""
    text1 = "Hello World"
    text2 = "Hello World"
    similarity = calculate_text_similarity(text1, text2)
    assert similarity == 1.0

def test_calculate_text_similarity_different():
    """Test similarity between completely different texts"""
    text1 = "Hello World"
    text2 = "Python Programming"
    similarity = calculate_text_similarity(text1, text2)
    assert 0.0 < similarity < 0.5

def test_calculate_text_similarity_partial():
    """Test similarity between partially overlapping texts"""
    text1 = "Hello World"
    text2 = "Hello Python"
    similarity = calculate_text_similarity(text1, text2)
    assert 0.0 < similarity < 1.0

def test_calculate_text_similarity_empty():
    """Test similarity with empty text"""
    assert calculate_text_similarity("", "") == 0.0
    assert calculate_text_similarity("Hello", "") == 0.0
    assert calculate_text_similarity("", "Hello") == 0.0

def test_calculate_text_similarity_case_insensitive():
    """Test similarity regardless of case"""
    text1 = "Hello World"
    text2 = "hello world"
    similarity = calculate_text_similarity(text1, text2)
    assert similarity == 1.0

def test_calculate_text_similarity_hebrew():
    """Test similarity between Hebrew texts"""
    text1 = "שלום עולם"
    text2 = "שלום עולם"
    similarity = calculate_text_similarity(text1, text2)
    assert similarity == 1.0

    text3 = "שלום עולם"
    text4 = "שלום לכולם"
    similarity = calculate_text_similarity(text3, text4)
    assert 0.0 < similarity < 1.0 