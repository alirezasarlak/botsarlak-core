"""
🌌 SarlakBot v2.4.0 - Persian Text Utilities
MERGE-SAFE: Persian text normalization and processing
"""

import re

def normalize_persian(s: str) -> str:
    """
    Normalize Persian text for consistent processing
    Args:
        s: Input string
    Returns:
        Normalized Persian string
    """
    if s is None: 
        return ""
    
    s = s.strip()
    s = re.sub(r"\s+", " ", s)  # Normalize whitespace
    
    # Arabic Yeh/Kaf → Persian
    s = s.replace("ي", "ی").replace("ك", "ک")
    
    # Eastern digits to Persian
    trans = str.maketrans(
        "0123456789٠١٢٣٤٥٦٧٨٩", 
        "۰۱۲۳۴۵۶۷۸۹۰۱۲۳۴۵۶۷۸۹"
    )
    return s.translate(trans)

def clean_nickname(nickname: str) -> str:
    """
    Clean and validate nickname
    Args:
        nickname: Raw nickname input
    Returns:
        Cleaned nickname
    """
    if not nickname:
        return ""
    
    # Normalize Persian text
    cleaned = normalize_persian(nickname)
    
    # Remove extra spaces and special characters
    cleaned = re.sub(r'[^\w\s\u0600-\u06FF]', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned

def is_inappropriate_content(text: str) -> bool:
    """
    Check if text contains inappropriate content
    Args:
        text: Text to check
    Returns:
        True if inappropriate content found
    """
    if not text:
        return False
    
    inappropriate_words = [
        'کص', 'کیر', 'خایه', 'جنده', 'فحش', 'لاشی', 'کونی', 
        'کصکش', 'خارکصه', 'ننه', 'مادر', 'بابات', 'بابا',
        'کونی', 'لاشی', 'خایه', 'کیر', 'کص', 'جنده'
    ]
    
    text_lower = text.lower()
    return any(word in text_lower for word in inappropriate_words)




