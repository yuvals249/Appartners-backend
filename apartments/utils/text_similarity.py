"""
Text similarity utilities for apartment recommendations.
"""
import re
from difflib import SequenceMatcher


def preprocess_text(text):
    """
    Preprocess text for better similarity comparison.
    
    Args:
        text: Input text string
        
    Returns:
        Preprocessed text string
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def calculate_text_similarity(text1, text2):
    """
    Calculate similarity between two text strings.
    
    Uses a combination of methods for better accuracy:
    - Sequence matching for overall similarity
    - Word overlap for semantic similarity
    
    Args:
        text1: First text string
        text2: Second text string
        
    Returns:
        float: Similarity score between 0 and 1
    """
    # Handle empty strings
    if not text1 or not text2:
        return 0.0
    
    # Preprocess texts
    clean_text1 = preprocess_text(text1)
    clean_text2 = preprocess_text(text2)
    
    if not clean_text1 or not clean_text2:
        return 0.0
    
    # Calculate sequence similarity
    sequence_similarity = SequenceMatcher(None, clean_text1, clean_text2).ratio()
    
    # Calculate word overlap similarity
    words1 = set(clean_text1.split())
    words2 = set(clean_text2.split())
    
    if not words1 or not words2:
        return sequence_similarity
    
    # Jaccard similarity for word overlap
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    word_similarity = intersection / union if union > 0 else 0
    
    # Combine both similarity measures (weighted average)
    combined_similarity = (0.7 * sequence_similarity) + (0.3 * word_similarity)
    
    return combined_similarity
