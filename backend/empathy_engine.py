"""
Empathy Engine - Generates supportive, empathetic responses for mental health companion.
Implements exact behavioral rules as specified.
"""
import random
from typing import Optional


# -----------------------------------
# EXACT BEHAVIORAL RULES
# -----------------------------------

# 1. GREETINGS
GREETING_KEYWORDS = [
    "hi", "hello", "hey", "gm", "ga", "good morning", "good afternoon", 
    "good evening", "how are you", "what's up", "sup"
]

GREETING_RESPONSE = "Hi, it's good to hear from you. How are you feeling today?"


# 2. NEUTRAL
NEUTRAL_RESPONSES = [
    "Thanks for sharing. Sometimes being neutral can hide deeper feelings. How has your day been so far?",
    "I'm here to listen. Even neutral feelings can tell us something. How has your day been so far?",
]


# 3. JOYFUL
JOY_RESPONSES = [
    "That's wonderful to hear! What's making you feel happy today?",
    "I'm so glad you're feeling good! What's making you feel happy today?",
]


# 4. SADNESS
SADNESS_RESPONSES = [
    "I'm really sorry you're going through this. Do you want to talk about what made you feel this way?",
    "That sounds really difficult. I'm here for you. Do you want to talk about what made you feel this way?",
]


# 5. STRESS / ANXIETY
STRESS_RESPONSES = [
    "That sounds overwhelming. What's causing the most stress right now?",
    "I hear you. Stress can be really tough. What's causing the most stress right now?",
]


# 6. ANGER
ANGER_RESPONSES = [
    "I'm sorry something upset you. What happened?",
    "That must have been frustrating. I'm here to listen. What happened?",
]


# 7. FEAR
FEAR_RESPONSES = [
    "I hear you. What's making you feel afraid?",
    "That sounds scary. I'm here with you. What's making you feel afraid?",
]


# 8. IRRELEVANT QUESTIONS
IRRELEVANT_RESPONSE = (
    "I can only support conversations about your emotions or well-being. "
    "Tell me how you're feeling — I'm here for you."
)


# 9. HEALTH QUERIES
HEALTH_KEYWORDS = {
    "chest pain": "Thanks for sharing this — your health matters. Can you describe the symptoms a bit more? If it becomes severe, please contact medical support immediately.",
    "dizziness": "Thanks for sharing this — your health matters. Can you describe the symptoms a bit more? If it becomes severe, please contact medical support immediately.",
    "headache": "Thanks for sharing this — your health matters. Can you describe the symptoms a bit more? If it becomes severe, please contact medical support immediately.",
    "heart racing": "Thanks for sharing this — your health matters. Can you describe the symptoms a bit more? If it becomes severe, please contact medical support immediately.",
    "nausea": "Thanks for sharing this — your health matters. Can you describe the symptoms a bit more? If it becomes severe, please contact medical support immediately.",
}


# 10. FOLLOW-UP QUESTIONS (to be appended to responses)
FOLLOW_UP_QUESTIONS = [
    "What do you feel triggered this?",
    "Do you want to share more about it?",
    "How has this been affecting you?",
    "What happened next?",
    "Can you tell me more?",
    "How are you feeling about that now?",
]


# -----------------------------------
# EMOTION MAPPING
# -----------------------------------
EMOTION_MAP = {
    # Sadness variants
    "sad": "sadness",
    "sadness": "sadness",
    "upset": "sadness",
    "depressed": "sadness",
    "down": "sadness",
    "low": "sadness",
    "grief": "sadness",
    "sorrow": "sadness",
    
    # Anger variants
    "anger": "anger",
    "angry": "anger",
    "annoyed": "anger",
    "irritated": "anger",
    "mad": "anger",
    "frustrated": "anger",
    "frustration": "anger",
    
    # Fear/Anxiety variants
    "fear": "fear",
    "anxiety": "fear",
    "anxious": "fear",
    "scared": "fear",
    "afraid": "fear",
    "nervous": "fear",
    "worried": "fear",
    "panic": "fear",
    
    # Stress variants
    "stress": "stress",
    "stressed": "stress",
    "overwhelmed": "stress",
    "pressure": "stress",
    "tension": "stress",
    
    # Joy variants
    "joy": "joy",
    "happy": "joy",
    "happiness": "joy",
    "excited": "joy",
    "grateful": "joy",
    "relieved": "joy",
    "content": "joy",
    
    # Neutral
    "neutral": "neutral",
    "calm": "neutral",
}


def normalize_emotion(emotion: str) -> str:
    """
    Normalize emotion label to one of: sadness, anger, fear, stress, joy, neutral.
    """
    if not emotion:
        return "neutral"
    
    emotion_lower = emotion.lower().strip()
    return EMOTION_MAP.get(emotion_lower, "neutral")


def generate_empathetic_reply(
    user_text: str,
    emotion: str,
    wellness_status: Optional[str] = None
) -> str:
    """
    Generate empathetic response based on user text and detected emotion.
    
    Args:
        user_text: User's input message
        emotion: Detected emotion label
        wellness_status: Wellness status (NOT used in chat response, only for internal logic)
        
    Returns:
        str: Empathetic response text
    """
    if not user_text:
        return "I'm here to listen. How are you feeling?"
    
    text_lower = user_text.lower().strip()
    
    # 1. GREETING DETECTION
    if any(greet in text_lower for greet in GREETING_KEYWORDS):
        return GREETING_RESPONSE
    
    # 2. HEALTH QUERIES
    for symptom, response in HEALTH_KEYWORDS.items():
        if symptom in text_lower:
            return response
    
    # 3. Normalize emotion
    emotion_key = normalize_emotion(emotion)
    
    # 4. Generate emotion-specific response
    base_response = None
    
    if emotion_key == "neutral":
        base_response = random.choice(NEUTRAL_RESPONSES)
    elif emotion_key == "joy":
        base_response = random.choice(JOY_RESPONSES)
    elif emotion_key == "sadness":
        base_response = random.choice(SADNESS_RESPONSES)
    elif emotion_key == "stress":
        base_response = random.choice(STRESS_RESPONSES)
    elif emotion_key == "anger":
        base_response = random.choice(ANGER_RESPONSES)
    elif emotion_key == "fear":
        base_response = random.choice(FEAR_RESPONSES)
    else:
        # Fallback to neutral
        base_response = random.choice(NEUTRAL_RESPONSES)
    
    # 5. Add follow-up question if not already present
    # (Some responses already have questions, but we ensure one is always there)
    if "?" not in base_response:
        follow_up = random.choice(FOLLOW_UP_QUESTIONS)
        base_response = f"{base_response} {follow_up}"
    
    return base_response


def generate_response(
    text: str,
    emotion: str,
    probability: float,
    pwi_snapshot: Optional[dict],
    history: list,
    tone_hint: Optional[str] = None,
) -> dict:
    """
    Advanced response generator (used internally for metadata).
    
    Args:
        text: User input
        emotion: Detected emotion
        probability: Emotion confidence
        pwi_snapshot: Wellness data (internal only, not shown in chat)
        history: Conversation history
        tone_hint: Optional tone override
        
    Returns:
        dict: Response with text, tags, tone, escalate flag
    """
    wellness_status = pwi_snapshot.get("status") if pwi_snapshot else None
    
    # Generate empathetic reply (wellness_status used internally, not in response text)
    reply_text = generate_empathetic_reply(text, emotion, wellness_status)
    
    # Determine tags and tone
    emotion_key = normalize_emotion(emotion)
    tags = ["empathetic", emotion_key]
    tone = tone_hint or "gentle"
    
    return {
        "text": reply_text,
        "tags": tags,
        "tone": tone,
        "escalate": False,
    }
