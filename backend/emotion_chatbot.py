# backend/emotion_chatbot.py

def get_empathetic_response(emotion: str, user_text: str) -> str:
    """
    Returns an emotion-aware response for the chatbot based on the detected emotion.
    """

    emotion = emotion.lower()

    responses = {
        "joy": [
            "That’s wonderful to hear! What made you feel so happy today?",
            "I’m glad you’re feeling great! Keep spreading the positivity 😊"
        ],
        "sadness": [
            "I’m really sorry to hear that. It’s okay to feel sad sometimes.",
            "That sounds tough. Want to talk more about what’s making you feel this way?"
        ],
        "anger": [
            "It’s completely okay to feel angry sometimes. Would you like to share what happened?",
            "That sounds frustrating. Let’s take a deep breath together."
        ],
        "fear": [
            "It sounds like something is worrying you. You’re not alone in this.",
            "Fear can be hard to deal with — I’m here to listen if you want to talk."
        ],
        "disgust": [
            "That must have been unpleasant. It’s okay to step back from things that upset you.",
            "It’s good that you can express what makes you uncomfortable."
        ],
        "surprise": [
            "That sounds surprising! What happened?",
            "Wow, I didn’t expect that either! Tell me more!"
        ],
        "neutral": [
            "I’m here to listen to you. What’s on your mind?",
            "I see. Would you like to tell me more about it?"
        ]
    }

    # fallback response
    default_response = "I’m here with you. How are you feeling about it?"

    # get appropriate response set
    for key, reply_list in responses.items():
        if key in emotion:
            import random
            return random.choice(reply_list)

    return default_response
