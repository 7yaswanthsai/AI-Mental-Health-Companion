"""
Relevance checker module to detect if messages are related to mental/physical health.
"""

MENTAL_HEALTH_TOPICS = [
    "stress", "anxiety", "sad", "fear", "angry", "health", "sleep",
    "panic", "worry", "feel", "emotion", "mental", "depressed",
    "tired", "exhausted", "overwhelmed", "upset", "frustrated",
    "lonely", "hopeless", "nervous", "scared", "worried", "mood",
    "therapy", "counseling", "wellness", "wellbeing", "mind",
    "thoughts", "feeling", "emotions", "happy", "joy", "relief"
]


def is_relevant(text):
    """
    Check if the text is relevant to mental/physical health topics.
    
    Args:
        text: User input text
        
    Returns:
        bool: True if relevant, False otherwise
    """
    if not text:
        return False
    
    text_lower = text.lower()
    for topic in MENTAL_HEALTH_TOPICS:
        if topic in text_lower:
            return True
    return False

