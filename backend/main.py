from datetime import datetime
from typing import Any, Dict, List

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from backend.emotion_service import predict_emotions
from database.chat_logger import log_chat
from database.fetch_chat_api import router as history_router
from backend.utils.emotion_fallback import detect_fallback_emotion
from backend.wellness_fusion import compute_pwi
from backend.recommendations import generate_recommendations
from backend.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
)



app = FastAPI()
app.include_router(history_router, dependencies=[Depends(get_current_user)])

class TextInput(BaseModel):
    text: str
    subject_id: str | None = None


class ChatResponse(BaseModel):
    text: str
    emotion: str
    probability: float
    wellness: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    timestamp: str


class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/login")
def login(data: LoginRequest):
    user = authenticate_user(data.email, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    access_token = create_access_token(user["email"])
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/chat")
def chat(current_user: dict = Depends(get_current_user)):
    return {"response": "Hello! How are you feeling today?"}


@app.post("/chat")
def chat_with_emotion(
    data: TextInput,
    current_user: dict = Depends(get_current_user),
):
    if not data.text or not data.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chat text cannot be empty",
        )

    text = data.text.strip()
    subject_id = data.subject_id or current_user.get("subject_id", "S10")

    # Predict with your trained model
    labels, probabilities = predict_emotions(text, top_n=3)

    emotion_label = labels[0] if labels else "neutral"
    emotion_prob = probabilities[0] if probabilities else 0.0

    # Apply fallback if probability is too low or model returns generic output
    if emotion_prob < 0.2 or emotion_label in ["neutral", "curiosity", "approval"]:
        fallback_emotion, sentiment = detect_fallback_emotion(text)
        emotion_label = fallback_emotion
        emotion_prob = abs(sentiment)

    wellness_snapshot = compute_pwi(subject_id)
    if not wellness_snapshot:
        wellness_snapshot = {"subject_id": subject_id, "pwi": None, "status": "No Wearable Data"}
    elif wellness_snapshot.get("pwi") is None:
        wellness_snapshot["status"] = wellness_snapshot.get("status") or "No Wearable Data"

    recommendations = generate_recommendations(
        emotion_label,
        wellness_snapshot.get("status"),
    )

    response_text = (
        recommendations[0]
        if recommendations
        else "I'm here for you. Tell me more about what’s on your mind."
    )
    timestamp = datetime.utcnow().isoformat()

    log_chat(
        text,
        emotion_label,
        emotion_prob,
        response_text,
        subject_id=subject_id,
        wellness=wellness_snapshot,
        recommendations=recommendations,
    )

    response = ChatResponse(
        text=response_text,
        emotion=emotion_label,
        probability=round(float(emotion_prob), 3),
        wellness=wellness_snapshot,
        recommendations=recommendations,
        timestamp=timestamp,
    )
    return response



@app.post("/emotion")
def emotion_analysis(
    data: TextInput,
    current_user: dict = Depends(get_current_user),
):
    if not data.text or not data.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chat text cannot be empty",
        )

    text = data.text.strip()
    labels, probabilities = predict_emotions(text, top_n=3)
    top_emotion = labels[0] if labels else "neutral"
    top_prob = probabilities[0] if probabilities else 0.0

    subject_id = data.subject_id or current_user.get("subject_id", "S10")
    wellness_snapshot = compute_pwi(subject_id)
    if not wellness_snapshot:
        wellness_snapshot = {"subject_id": subject_id, "pwi": None, "status": "No Wearable Data"}
    elif wellness_snapshot.get("pwi") is None:
        wellness_snapshot["status"] = wellness_snapshot.get("status") or "No Wearable Data"

    recommendations = generate_recommendations(
        top_emotion,
        wellness_snapshot.get("status"),
    )

    response_text = (
        recommendations[0]
        if recommendations
        else "I'm here for you. Tell me more about what’s on your mind."
    )
    timestamp = datetime.utcnow().isoformat()

    log_chat(
        text,
        top_emotion,
        top_prob,
        response_text,
        subject_id=subject_id,
        wellness=wellness_snapshot,
        recommendations=recommendations,
    )

    response = ChatResponse(
        text=response_text,
        emotion=top_emotion,
        probability=round(float(top_prob), 3),
        wellness=wellness_snapshot,
        recommendations=recommendations,
        timestamp=timestamp,
    )
    return response


@app.get("/wellness/{subject_id}")
def get_wellness(
    subject_id: str,
    current_user: dict = Depends(get_current_user),
):
    result = compute_pwi(subject_id)
    if not result:
        return {"subject_id": subject_id, "status": "no data"}
    return result


@app.get("/recommendations")
def get_recommendations(
    emotion: str,
    wellness_status: str | None = None,
    current_user: dict = Depends(get_current_user),
):
    recs = generate_recommendations(emotion, wellness_status)
    return {"emotion": emotion, "wellness_status": wellness_status, "recommendations": recs}

