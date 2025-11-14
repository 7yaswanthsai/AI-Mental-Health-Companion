"""
Safety guard module to detect self-harm intent and provide emergency response.
"""

KEYWORDS_SELF_HARM = [
    "kill myself", "suicide", "end my life", "self harm",
    "hurt myself", "want to die", "cut myself", "i dont want to live",
    "can't go on", "no point living", "better off dead"
]

EMERGENCY_RESPONSE = """I'm really sorry you're feeling this way. You're not alone, and your feelings matter.

Please reach out to someone who can help immediately:

🇮🇳 India Emergency Contacts  
• Suicide Prevention (AASRA, 24x7): **9152987821**  
• National Mental Health Helpline: **1800-599-0019**  
• Emergency Ambulance: **108**

If you can, call a trusted friend or family member.  
I'm here with you, but you deserve immediate human support too."""


def detect_crisis(text):
    """
    Detect if the text contains self-harm or crisis keywords.
    
    Args:
        text: User input text
        
    Returns:
        bool: True if crisis detected, False otherwise
    """
    if not text:
        return False
    
    text_lower = text.lower()
    for kw in KEYWORDS_SELF_HARM:
        if kw in text_lower:
            return True
    return False

