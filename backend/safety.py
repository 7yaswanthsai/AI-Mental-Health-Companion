from __future__ import annotations

from typing import List, Tuple

CRISIS_KEYWORDS = {
    "suicide",
    "kill myself",
    "end my life",
    "can't go on",
    "hurt myself",
    "self-harm",
    "cut myself",
    "jump off",
    "overdose",
}

VIOLENCE_KEYWORDS = {
    "hurt someone",
    "kill someone",
    "attack",
    "revenge",
    "violence",
}

CRISIS_RESPONSE = (
    "I'm really glad you told me. Your safety matters more than anything right now. "
    "Please contact emergency services or a trusted person nearby immediately. "
    "If you're able, reach a crisis hotline such as 988 (US) or your local emergency number."
)


def check_safety(text: str, pwi_status: str | None, history: List[dict]) -> Tuple[bool, List[str]]:
    text_lower = text.lower()
    flags: List[str] = []

    crisis_hit = any(keyword in text_lower for keyword in CRISIS_KEYWORDS)
    violence_hit = any(keyword in text_lower for keyword in VIOLENCE_KEYWORDS)

    repeated_distress = sum(1 for h in history if h.get("metadata", {}).get("emotion") in {"sadness", "fear"}) >= 3
    low_wellness = pwi_status and pwi_status.lower() in {"stressed", "high stress", "unknown (no data)"}

    escalate = False
    if crisis_hit or (repeated_distress and low_wellness):
        flags.append("crisis")
        escalate = True
    if violence_hit:
        flags.append("violence")
        escalate = True

    return escalate, flags


def crisis_message() -> str:
    return CRISIS_RESPONSE

