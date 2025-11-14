from typing import List


NEGATIVE_EMOTIONS = {"sad", "sadness", "grief", "remorse", "disappointment", "loneliness"}
ANGER_EMOTIONS = {"anger", "angry", "annoyance", "annoyed", "disgust", "frustration"}
FEAR_EMOTIONS = {"fear", "nervousness", "anxiety", "worry", "afraid", "scared"}
SURPRISE_EMOTIONS = {"surprise", "confusion", "confused", "astonished"}
POSITIVE_EMOTIONS = {"joy", "amusement", "gratitude", "love", "admiration", "pride", "relief", "happy"}


def generate_recommendations(emotion: str, pwi_status: str | None) -> List[str]:
    emotion_lower = (emotion or "").lower()
    pwi_status = pwi_status or ""
    recommendations: List[str] = []

    if emotion_lower in NEGATIVE_EMOTIONS:
        recommendations.extend(
            [
                "Spend 10 minutes journaling about what you're feeling.",
                "Try a 4-7-8 breathing exercise to calm your body.",
                "Note three small positives from today to reframe the moment.",
            ]
        )
    elif emotion_lower in ANGER_EMOTIONS:
        recommendations.extend(
            [
                "Practice the 5-4-3-2-1 grounding technique.",
                "Slow your breathing—inhale for 4, exhale for 6.",
            ]
        )
    elif emotion_lower in FEAR_EMOTIONS:
        recommendations.extend(
            [
                "Follow a 5-minute guided meditation.",
                "Remind yourself: 'It's okay to take things one step at a time.'",
            ]
        )
    elif emotion_lower in SURPRISE_EMOTIONS:
        recommendations.append("Write down what surprised you and how it impacts you.")
    elif emotion_lower in POSITIVE_EMOTIONS:
        recommendations.extend(
            [
                "Capture this moment in a gratitude note.",
                "Set a small goal for tomorrow to keep the momentum.",
            ]
        )
    else:
        recommendations.append("Check in with your breath and posture; stay mindful.")

    status_lower = pwi_status.lower()
    if "stressed" in status_lower:
        recommendations.append("Take a 5-minute deep breathing break.")
    elif "unknown" in status_lower:
        recommendations.append("Wearable not detected. Please sync device.")

    return recommendations

