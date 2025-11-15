"""
Relevance checker module to detect if messages are related to mental/physical health.
Expanded to detect irrelevant questions (math, coding, politics, knowledge).
"""
import re

# Mental health and wellness topics
MENTAL_HEALTH_TOPICS = [
    "stress", "anxiety", "sad", "fear", "angry", "health", "sleep",
    "panic", "worry", "feel", "emotion", "mental", "depressed",
    "tired", "exhausted", "overwhelmed", "upset", "frustrated",
    "lonely", "hopeless", "nervous", "scared", "worried", "mood",
    "therapy", "counseling", "wellness", "wellbeing", "mind",
    "thoughts", "feeling", "emotions", "happy", "joy", "relief",
    "sadness", "anger", "fear", "grief", "sorrow", "contentment",
]

# Greetings and conversational phrases that should be allowed
GREETINGS_AND_CONVERSATIONAL = [
    "hi", "hello", "hey", "how are you", "how's it going", "what's up",
    "good morning", "good afternoon", "good evening", "how do you do",
    "nice to meet you", "thanks", "thank you", "please", "help",
    "talk", "chat", "conversation", "tell me", "share", "listen",
    "gm", "ga", "sup",
]

# Irrelevant question patterns (math, coding, politics, knowledge)
IRRELEVANT_PATTERNS = [
    # Math
    r'\d+\s*[+\-*/]\s*\d+',  # Arithmetic: 1+1, 5-3, etc.
    r'calculate|solve|math|equation|formula',
    r'what is \d+ \+\d+|what is \d+ \-\d+',
    
    # Coding/Programming
    r'write code|programming|python|javascript|java|c\+\+|code|function|algorithm',
    r'how to code|how do i code|debug|syntax error',
    
    # Politics
    r'who is the (pm|president|prime minister|minister)',
    r'political|politics|election|vote|government|parliament',
    
    # General knowledge
    r'what is the capital of|who is|what is|when did|where is|which country',
    r'define|explain|meaning of|history of',
    
    # Weather
    r'weather|temperature|rain|forecast',
    
    # Sports
    r'sports|football|cricket|match|game score',
    
    # Other
    r'recipe|cooking|how to cook',
    r'translate|language|dictionary',
]


def is_relevant(text: str) -> bool:
    """
    Check if the text is relevant to mental/physical health topics.
    Allows greetings and conversational phrases.
    Blocks math, coding, politics, and general knowledge questions.
    
    Args:
        text: User input text
        
    Returns:
        bool: True if relevant, False if irrelevant
    """
    if not text:
        return False
    
    text_lower = text.lower().strip()
    
    # 1. Allow greetings and conversational phrases
    for greeting in GREETINGS_AND_CONVERSATIONAL:
        if greeting in text_lower:
            return True
    
    # 2. Check for irrelevant patterns (math, coding, politics, etc.)
    for pattern in IRRELEVANT_PATTERNS:
        if re.search(pattern, text_lower):
            return False  # Explicitly irrelevant
    
    # 3. Check for mental health topics
    for topic in MENTAL_HEALTH_TOPICS:
        if topic in text_lower:
            return True
    
    # 4. If text is very short (likely a greeting or simple response), allow it
    if len(text_lower.split()) <= 3:
        return True
    
    # 5. Check for emotional language patterns
    emotional_words = [
        "feel", "feeling", "emotion", "mood", "upset", "worried",
        "anxious", "stressed", "sad", "happy", "angry", "scared",
    ]
    for word in emotional_words:
        if word in text_lower:
            return True
    
    # Default: if we can't determine, assume relevant (fail-open for mental health)
    return True
