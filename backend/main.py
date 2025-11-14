from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import logging
from backend.emotion_service import predict_emotions
from backend.empathy_engine import generate_response as generate_empathy_response
from backend.context_memory import append_context, get_context
from backend.safety import check_safety, crisis_message
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
from mlops.log_inference import (
    log_emotion_prediction,
    log_wellness_snapshot,
    log_recommendation_triggered,
    log_chat_interaction,
)



app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Configure CORS to allow mobile app requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    tags: List[str] = Field(default_factory=list)
    tone: Optional[str] = None
    escalate: bool = False


class LoginRequest(BaseModel):
    email: str
    password: str


@app.get("/health")
def health_check():
    """Health check endpoint to test connectivity"""
    return {"status": "ok", "message": "Backend is running"}

@app.post("/login")
def login(data: LoginRequest):
    logger.info(f"Login attempt for email: {data.email}")
    user = authenticate_user(data.email, data.password)
    if not user:
        logger.warning(f"Login failed for email: {data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    access_token = create_access_token(user["email"])
    logger.info(f"Login successful for email: {data.email}")
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

    # Log to MLflow
    log_emotion_prediction(text, emotion_label, emotion_prob, subject_id=subject_id)
    if wellness_snapshot.get("pwi") is not None:
        log_wellness_snapshot(
            subject_id,
            wellness_snapshot["pwi"],
            wellness_snapshot.get("status", "unknown"),
            wellness_snapshot.get("features"),
        )
    log_recommendation_triggered(
        emotion_label,
        wellness_snapshot.get("status"),
        recommendations,
        subject_id=subject_id,
    )

    history = get_context(subject_id)
    escalate, _ = check_safety(text, wellness_snapshot.get("status"), history)

    empathy_payload = generate_empathy_response(
        text=text,
        emotion=emotion_label,
        probability=emotion_prob,
        pwi_snapshot=wellness_snapshot,
        history=history,
    )

    response_text = empathy_payload["text"]
    tags = empathy_payload.get("tags", [])
    tone = empathy_payload.get("tone")

    if escalate or empathy_payload.get("escalate"):
        response_text = crisis_message()
        tags = list(dict.fromkeys(tags + ["crisis_support"]))
        tone = "calm"
    timestamp = datetime.utcnow().isoformat()

    log_chat(
        text,
        emotion_label,
        emotion_prob,
        response_text,
        subject_id=subject_id,
        wellness=wellness_snapshot,
        recommendations=recommendations,
        tags=tags,
        tone=tone,
        escalate=escalate,
    )

    append_context(
        subject_id=subject_id,
        user_msg=text,
        bot_msg=response_text,
        metadata={
        "emotion": emotion_label,
            "probability": float(emotion_prob),
            "tags": tags,
            "tone": tone,
            "timestamp": timestamp,
        },
    )

    # Log complete chat interaction
    log_chat_interaction(
        subject_id,
        emotion_label,
        wellness_snapshot.get("pwi"),
        len(recommendations),
        escalate,
    )

    response = ChatResponse(
        text=response_text,
        emotion=emotion_label,
        probability=round(float(emotion_prob), 3),
        wellness=wellness_snapshot,
        recommendations=recommendations,
        timestamp=timestamp,
        tags=tags,
        tone=tone,
        escalate=escalate,
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

    history = get_context(subject_id)
    escalate, _ = check_safety(text, wellness_snapshot.get("status"), history)

    empathy_payload = generate_empathy_response(
        text=text,
        emotion=top_emotion,
        probability=top_prob,
        pwi_snapshot=wellness_snapshot,
        history=history,
    )

    response_text = empathy_payload["text"]
    tags = empathy_payload.get("tags", [])
    tone = empathy_payload.get("tone")

    if escalate or empathy_payload.get("escalate"):
        response_text = crisis_message()
        tags = list(dict.fromkeys(tags + ["crisis_support"]))
        tone = "calm"
    timestamp = datetime.utcnow().isoformat()

    log_chat(
        text,
        top_emotion,
        top_prob,
        response_text,
        subject_id=subject_id,
        wellness=wellness_snapshot,
        recommendations=recommendations,
        tags=tags,
        tone=tone,
        escalate=escalate,
    )

    append_context(
        subject_id=subject_id,
        user_msg=text,
        bot_msg=response_text,
        metadata={
        "emotion": top_emotion,
            "probability": float(top_prob),
            "tags": tags,
            "tone": tone,
            "timestamp": timestamp,
        },
    )

    response = ChatResponse(
        text=response_text,
        emotion=top_emotion,
        probability=round(float(top_prob), 3),
        wellness=wellness_snapshot,
        recommendations=recommendations,
        timestamp=timestamp,
        tags=tags,
        tone=tone,
        escalate=escalate,
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

