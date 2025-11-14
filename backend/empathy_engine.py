from __future__ import annotations

import json
import os
import random
from typing import Dict, List, Optional

PERSONALITY_PATH = os.path.join(os.path.dirname(__file__), "personality.json")

try:
    with open(PERSONALITY_PATH, "r", encoding="utf-8") as f:
        PERSONALITY = json.load(f)
except FileNotFoundError:  # pragma: no cover
    PERSONALITY = {
        "name": "Companion",
        "tone": {"default": "gentle"},
        "signoffs": ["I'm here with you."],
        "reminders": [],
    }


TEMPLATES: Dict[str, List[str]] = {
    "joy": [
        "That's wonderful to hear! I love how you notice the bright spots. What made that moment feel so special?",
        "Your joy really shines through. Tell me more so we can celebrate it together.",
    ],
    "sadness": [
        "I'm really sorry you're carrying this weight. It's completely okay to feel what you're feeling.",
        "Thank you for trusting me with this. We can take it slow and sit with the sadness together.",
    ],
    "anger": [
        "It's understandable to feel upset after something so frustrating. Your emotions are valid.",
        "That sounds really tough, and anyone would feel agitated in that situation.",
    ],
    "fear": [
        "Feeling anxious can be exhausting. Let's take a calming breath while we talk it through.",
        "You're not alone in this worry. We can break it down step by step together.",
    ],
    "surprise": [
        "That sounds unexpected! How are you holding up with it all?",
        "It can take a minute to process something surprising. I'm here while you do.",
    ],
    "neutral": [
        "I'm listening. Whatever you're feeling matters here.",
        "Thanks for checking in—what would feel helpful to talk about right now?",
    ],
}

ACTION_TAGS = {
    "sadness": ["journaling", "breathing", "reaching_out"],
    "anger": ["grounding", "breathing"],
    "fear": ["guided_meditation", "reassurance"],
    "surprise": ["reflection"],
    "joy": ["celebration", "gratitude"],
    "neutral": ["check_in"],
}


def _pick_template(emotion: str) -> str:
    pool = TEMPLATES.get(emotion, TEMPLATES["neutral"])
    return random.choice(pool)


def _describe_context(history: List[dict]) -> Optional[str]:
    if not history:
        return None
    last = history[-1]
    prev_emotion = last.get("metadata", {}).get("emotion")
    if prev_emotion:
        return f"I remember earlier you mentioned feeling {prev_emotion}. "
    return None


def _pwi_advice(pwi_snapshot: dict | None) -> Optional[str]:
    if not pwi_snapshot:
        return None
    status = (pwi_snapshot.get("status") or "").lower()
    if "stressed" in status:
        return "Let’s try a grounding exercise—placing a hand on your chest and feeling each inhale and exhale."
    if "calm" in status:
        return "It’s great to notice this steadiness. Maybe note what’s supporting it so you can revisit it later."
    if "unknown" in status:
        return "If you’re able, syncing your wearable later might give us clearer wellness signals."
    return None


def generate_response(
    text: str,
    emotion: str,
    probability: float,
    pwi_snapshot: Optional[dict],
    history: List[dict],
    tone_hint: Optional[str] = None,
) -> dict:
    emotion_key = emotion if emotion in TEMPLATES else "neutral"
    base = _pick_template(emotion_key)
    personalization = _describe_context(history) or ""

    encouragement = PERSONALITY["reminders"]
    reminder_line = random.choice(encouragement) if encouragement else ""

    pwi_line = _pwi_advice(pwi_snapshot) or ""

    sentences = [personalization + base]
    if emotion_key in {"sadness", "fear", "anger"}:
        sentences.append("You deserve kindness from yourself right now; let's slow down together.")
    if pwi_line:
        sentences.append(pwi_line)
    if reminder_line:
        sentences.append(reminder_line)

    final_text = " ".join(sentence.strip() for sentence in sentences if sentence.strip())

    tone = tone_hint or PERSONALITY["tone"].get("default", "gentle")
    if pwi_snapshot and (pwi_snapshot.get("status") or "").lower().startswith("stress"):
        tone = PERSONALITY["tone"].get("stressed", tone)

    tags = ACTION_TAGS.get(emotion_key, ["check_in"])
    if pwi_snapshot and (pwi_snapshot.get("status") or "").lower() in {"stressed", "high stress"}:
        tags = list(dict.fromkeys(tags + ["grounding", "breathing"]))

    return {
        "text": final_text,
        "tags": tags,
        "tone": tone,
        "escalate": False,
    }

