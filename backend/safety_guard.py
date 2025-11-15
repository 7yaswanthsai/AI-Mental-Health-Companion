"""
Safety guard module to detect self-harm intent and provide emergency response.
Updated with stronger crisis detection patterns.
"""
import re

# Strong crisis detection keywords
KEYWORDS_SELF_HARM = [
    "i want to die",
    "end everything",
    "cut myself",
    "suicide",
    "kill myself",
    "end my life",
    "self harm",
    "hurt myself",
    "want to die",
    "i dont want to live",
    "can't go on",
    "no point living",
    "better off dead",
    "end it all",
    "not worth living",
    "give up",
    "no reason to live",
]

# Exact crisis response as specified
CRISIS_RESPONSE = """I'm really sorry you're feeling this much pain. You deserve help and support right now.

Please reach out immediately to someone who can keep you safe:

• India Mental Health Helpline: 9152987821
• Suicide Prevention: 1800-599-0019
• Emergency Ambulance: 108

You are not alone — I'm here with you."""

# Legacy alias for backward compatibility
EMERGENCY_RESPONSE = CRISIS_RESPONSE


def detect_crisis(text: str) -> bool:
    """
    Detect if the text contains self-harm or crisis keywords.
    Uses case-insensitive matching and word boundary detection.
    
    Args:
        text: User input text
        
    Returns:
        bool: True if crisis detected, False otherwise
    """
    if not text:
        return False
    
    text_lower = text.lower().strip()
    
    # Check for exact keyword matches
    for kw in KEYWORDS_SELF_HARM:
        if kw in text_lower:
            return True
    
    # Additional pattern matching for variations
    crisis_patterns = [
        r'\b(want|wanna|going to|gonna)\s+(to\s+)?(die|kill|end|hurt)',
        r'\b(suicide|self[\s-]?harm|cutting)',
        r'\b(no\s+point|not\s+worth|better\s+off)\s+(living|alive)',
    ]
    
    for pattern in crisis_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False
