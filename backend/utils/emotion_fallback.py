# backend/utils/emotion_fallback.py
from textblob import TextBlob

EMOTION_KEYWORDS = {
    "happy": ["happy", "joy", "delighted", "excited", "glad", "cheerful", "positive", "great"],
    "sad": ["sad", "down", "depressed", "unhappy", "cry", "miserable", "disappointed"],
    "angry": ["angry", "mad", "furious", "irritated", "annoyed", "rage"],
    "fear": ["fear", "scared", "afraid", "terrified", "worried", "nervous", "anxious"],
    "surprise": ["surprise", "amazed", "astonished", "shocked", "startled"],
    "disgust": ["disgust", "gross", "nasty", "offended"],
}

def detect_fallback_emotion(text: str):
    """Fallback emotion detection using keyword and sentiment polarity."""
    text_lower = text.lower()
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity  # -1 (neg) to +1 (pos)

    # Keyword-based detection
    for emotion, words in EMOTION_KEYWORDS.items():
        if any(word in text_lower for word in words):
            return emotion, sentiment

    # Sentiment-based fallback
    if sentiment > 0.4:
        return "happy", sentiment
    elif sentiment < -0.4:
        return "sad", sentiment
    else:
        return "neutral", sentiment
