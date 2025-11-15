# backend/main.py
"""
Main FastAPI application for Personalized Mental Health Companion.
Upgraded to support empathetic chatbot with user registration.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr

# Local imports
from backend.emotion_service import predict_emotions
from backend.empathy_engine import (
    generate_response as generate_empathy_response,
    generate_empathetic_reply,
)
from backend.context_memory import append_context, get_context
from backend.safety_guard import detect_crisis, CRISIS_RESPONSE
from backend.relevance_checker import is_relevant
from database.chat_logger import log_chat
from database.fetch_chat_api import router as history_router
from backend.utils.emotion_fallback import detect_fallback_emotion
from backend.wellness_fusion import compute_pwi
from backend.recommendations import generate_recommendations
from backend.auth import (
    authenticate_user,
    register_user,
    create_access_token,
    get_current_user,
)
from mlops.log_inference import (
    log_emotion_prediction,
    log_wellness_snapshot,
    log_recommendation_triggered,
    log_chat_interaction,
)

app = FastAPI(title="Mental Health Companion API", version="2.0.0")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise

# Configure CORS to allow mobile app requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include history router (protected)
app.include_router(history_router, dependencies=[Depends(get_current_user)])

# -----------------------------
# Models
# -----------------------------
class TextInput(BaseModel):
    text: str
    subject_id: Optional[str] = None


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
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    subject_id: Optional[str] = None


class RegisterResponse(BaseModel):
    message: str
    subject_id: str


# -----------------------------
# Health endpoint
# -----------------------------
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend is running"}


# -----------------------------
# Auth endpoints
# -----------------------------
@app.post("/register", response_model=RegisterResponse)
def register(data: RegisterRequest):
    """
    Register a new user.
    
    Fields:
    - name: Full name
    - email: Email address (must be unique)
    - password: Plain text password (will be hashed)
    - subject_id: Optional (auto-generated if not provided)
    
    Returns:
    - message: Success message
    - subject_id: Generated or provided subject_id
    """
    logger.info(f"Registration attempt for email: {data.email}")
    try:
        user = register_user(
            name=data.name,
            email=data.email,
            password=data.password,
            subject_id=data.subject_id,
        )
        logger.info(f"User registered successfully: {data.email} with subject_id {user['subject_id']}")
        return RegisterResponse(
            message="User registered successfully",
            subject_id=user["subject_id"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@app.post("/login")
def login(data: LoginRequest):
    """
    Login endpoint - authenticates user and returns JWT token.
    """
    logger.info(f"Login attempt for email: {data.email}")
    user = authenticate_user(data.email, data.password)
    if not user:
        logger.warning(f"Login failed for email: {data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    access_token = create_access_token(data.email)
    logger.info(f"Login successful for email: {data.email}")
    return {"access_token": access_token, "token_type": "bearer"}


# -----------------------------
# Chat endpoints
# -----------------------------
@app.get("/chat")
def chat(current_user: dict = Depends(get_current_user)):
    """General greeting route (protected)."""
    return {"response": "Hello! How are you feeling today?"}


@app.post("/chat", response_model=ChatResponse)
def chat_with_emotion(
    data: TextInput,
    current_user: dict = Depends(get_current_user),
):
    """
    Main chat endpoint with emotion detection and empathetic responses.
    
    Features:
    - Crisis detection (highest priority)
    - Greeting handling
    - Irrelevant question filtering
    - Emotion prediction
    - Empathetic response generation
    - Wellness tracking (internal only, not shown in chat)
    """
    if not data.text or not data.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chat text cannot be empty",
        )

    text = data.text.strip()
    subject_id = data.subject_id or current_user.get("subject_id", "S10")
    timestamp = datetime.utcnow().isoformat()

    # 1) CRISIS DETECTION - Highest priority
    if detect_crisis(text):
        logger.warning(f"Crisis detected for subject {subject_id}")
        # Compute wellness internally (for logging) but don't show in response
        wellness_snapshot = compute_pwi(subject_id) or {
            "subject_id": subject_id,
            "pwi": None,
            "status": "Crisis Detected",
        }
        
        response = ChatResponse(
            text=CRISIS_RESPONSE,  # Use exact crisis response
            emotion="crisis",
            probability=1.0,
            wellness=wellness_snapshot,  # Internal only
            recommendations=[],  # No recommendations in crisis mode
            timestamp=timestamp,
            tags=["crisis_support", "emergency"],
            tone="calm",
            escalate=True,
        )
        # Log crisis event
        try:
            log_chat(
                text,
                response.emotion,
                response.probability,
                response.text,
                subject_id=subject_id,
                wellness=response.wellness,
                recommendations=[],
                tags=response.tags,
                tone=response.tone,
                escalate=True,
            )
        except Exception:
            logger.exception("Failed to log crisis event")
        
        return response

    # 2) IRRELEVANT QUESTION CHECK
    if not is_relevant(text):
        logger.info(f"Irrelevant question detected: {text[:50]}...")
        # Compute wellness internally but don't show wearable messages
        wellness_snapshot = compute_pwi(subject_id) or {
            "subject_id": subject_id,
            "pwi": None,
            "status": "No Wearable Data",
        }
        
        response_text = (
            "I can only support conversations about your emotions or well-being. "
            "Tell me how you're feeling — I'm here for you."
        )
        
        try:
            log_chat(
                text,
                "irrelevant",
                0.0,
                response_text,
                subject_id=subject_id,
                wellness=wellness_snapshot,
                recommendations=[],
            )
        except Exception:
            logger.exception("Failed to log irrelevant question")
        
        return ChatResponse(
            text=response_text,
            emotion="irrelevant",
            probability=0.0,
            wellness=wellness_snapshot,  # Internal only
            recommendations=[],
            timestamp=timestamp,
            tags=["redirect"],
            tone="gentle",
            escalate=False,
        )

    # 3) PREDICT EMOTION (with fallback)
    try:
        logger.info(f"Predicting emotion for text: {text[:80]}")
        labels, probabilities = predict_emotions(text, top_n=3)
    except Exception as e:
        logger.error(f"Emotion prediction failed, using fallback: {e}", exc_info=True)
        fallback_emotion, sentiment = detect_fallback_emotion(text)
        labels = [fallback_emotion]
        probabilities = [abs(sentiment)]

    emotion_label = labels[0] if labels else "neutral"
    emotion_prob = probabilities[0] if probabilities else 0.0

    # If low confidence or generic label, use fallback
    if emotion_prob < 0.2 or emotion_label in ["neutral", "curiosity", "approval"]:
        logger.info(f"Low confidence ({emotion_prob:.3f}) or generic label; applying fallback")
        fallback_emotion, sentiment = detect_fallback_emotion(text)
        emotion_label = fallback_emotion
        emotion_prob = abs(sentiment)

    # 4) COMPUTE WELLNESS SNAPSHOT (INTERNAL ONLY - NOT SHOWN IN CHAT)
    wellness_snapshot = compute_pwi(subject_id) or {
        "subject_id": subject_id,
        "pwi": None,
        "status": "No Wearable Data",
    }
    
    # Generate recommendations internally (for dashboard, not chat)
    recommendations = generate_recommendations(
        emotion_label,
        wellness_snapshot.get("status"),
    )

    # 5) LOG ML METRICS (internal tracking)
    try:
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
    except Exception:
        logger.exception("Failed to log ML metrics (continuing)")

    # 6) GET CONVERSATION HISTORY
    history = get_context(subject_id)

    # 7) GENERATE EMPATHETIC RESPONSE (this is what user sees in chat)
    # Wellness status is used internally for context, but NOT shown in response text
    try:
        response_text = generate_empathetic_reply(
            text,
            emotion_label,
            wellness_snapshot.get("status"),  # Internal context only
        )
    except Exception as e:
        logger.error(f"Empathetic reply generation failed: {e}", exc_info=True)
        # Fallback responses
        response_text = {
            "sadness": "I'm really sorry you're going through this. Do you want to talk about what made you feel this way?",
            "anger": "I'm sorry something upset you. What happened?",
            "joy": "That's wonderful to hear! What's making you feel happy today?",
            "fear": "I hear you. What's making you feel afraid?",
            "stress": "That sounds overwhelming. What's causing the most stress right now?",
            "neutral": "Thanks for sharing. Sometimes being neutral can hide deeper feelings. How has your day been so far?",
        }.get(emotion_label, "I'm here to listen. How are you feeling right now?")

    # 8) GET METADATA FROM EMPATHY ENGINE (tags, tone)
    empathy_payload = {}
    try:
        empathy_payload = generate_empathy_response(
            text=text,
            emotion=emotion_label,
            probability=emotion_prob,
            pwi_snapshot=wellness_snapshot,
            history=history,
        )
    except Exception:
        logger.exception("generate_empathy_response failed; continuing")

    tags = empathy_payload.get("tags", ["empathetic", emotion_label])
    tone = empathy_payload.get("tone", "gentle")
    escalate_flag = empathy_payload.get("escalate", False)

    # 9) PERSIST CHAT RECORD (store wellness & recommendations in DB, not in chat text)
    try:
        log_chat(
            text,
            emotion_label,
            float(emotion_prob),
            response_text,
            subject_id=subject_id,
            wellness=wellness_snapshot,  # Stored in DB
            recommendations=recommendations,  # Stored in DB
            tags=tags,
            tone=tone,
            escalate=escalate_flag,
        )
    except Exception:
        logger.exception("Failed to log chat to DB")

    # Append to context memory
    try:
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
    except Exception:
        logger.exception("Failed to append context")

    # 10) FINAL RESPONSE
    # IMPORTANT: Wellness data is included in response for frontend dashboard,
    # but the chat text itself NEVER mentions wearable/PWI/health scores
    response = ChatResponse(
        text=response_text,  # Pure empathetic text, no wearable references
        emotion=emotion_label,
        probability=round(float(emotion_prob), 3),
        wellness=wellness_snapshot,  # For dashboard only
        recommendations=[],  # Empty - frontend should call /recommendations if needed
        timestamp=timestamp,
        tags=tags,
        tone=tone,
        escalate=escalate_flag,
    )

    # Log high-level interaction
    try:
        log_chat_interaction(
            subject_id,
            emotion_label,
            wellness_snapshot.get("pwi"),
            len(recommendations),
            escalate_flag,
        )
    except Exception:
        logger.exception("Failed to log chat interaction")

    return response


# Emotion-only endpoint (protected)
@app.post("/emotion", response_model=ChatResponse)
def emotion_analysis(
    data: TextInput,
    current_user: dict = Depends(get_current_user),
):
    """
    Emotion analysis endpoint - returns emotion prediction without full chat response.
    """
    if not data.text or not data.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chat text cannot be empty",
        )

    text = data.text.strip()
    subject_id = data.subject_id or current_user.get("subject_id", "S10")
    timestamp = datetime.utcnow().isoformat()

    # Crisis check
    if detect_crisis(text):
        wellness_snapshot = compute_pwi(subject_id) or {
            "subject_id": subject_id,
            "pwi": None,
            "status": "Crisis Detected",
        }
        return ChatResponse(
            text=CRISIS_RESPONSE,
            emotion="crisis",
            probability=1.0,
            wellness=wellness_snapshot,
            recommendations=[],
            timestamp=timestamp,
            tags=["crisis_support", "emergency"],
            tone="calm",
            escalate=True,
        )

    # Predict emotion
    labels, probabilities = [], []
    try:
        labels, probabilities = predict_emotions(text, top_n=3)
    except Exception:
        fallback_emotion, sentiment = detect_fallback_emotion(text)
        labels = [fallback_emotion]
        probabilities = [abs(sentiment)]

    top_emotion = labels[0] if labels else "neutral"
    top_prob = probabilities[0] if probabilities else 0.0

    wellness_snapshot = compute_pwi(subject_id) or {
        "subject_id": subject_id,
        "pwi": None,
        "status": "No Wearable Data",
    }
    recommendations = generate_recommendations(
        top_emotion,
        wellness_snapshot.get("status"),
    )

    # Generate empathetic response
    history = get_context(subject_id)
    response_text = generate_empathetic_reply(
        text,
        top_emotion,
        wellness_snapshot.get("status"),
    )
    
    empathy_payload = {}
    try:
        empathy_payload = generate_empathy_response(
            text=text,
            emotion=top_emotion,
            probability=top_prob,
            pwi_snapshot=wellness_snapshot,
            history=history,
        )
    except Exception:
        logger.exception("generate_empathy_response failed (emotion endpoint)")

    tags = empathy_payload.get("tags", [])
    tone = empathy_payload.get("tone", "gentle")
    escalate_flag = empathy_payload.get("escalate", False)

    # Log
    try:
        log_chat(
            text,
            top_emotion,
            float(top_prob),
            response_text,
            subject_id=subject_id,
            wellness=wellness_snapshot,
            recommendations=recommendations,
            tags=tags,
            tone=tone,
            escalate=escalate_flag,
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
    except Exception:
        logger.exception("Failed to log emotion endpoint chat")

    return ChatResponse(
        text=response_text,
        emotion=top_emotion,
        probability=round(float(top_prob), 3),
        wellness=wellness_snapshot,
        recommendations=[],
        timestamp=timestamp,
        tags=tags,
        tone=tone,
        escalate=escalate_flag,
    )


# Wellness & recommendations endpoints (protected)
@app.get("/wellness/{subject_id}")
def get_wellness(subject_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get wellness data for a subject (for dashboard, not chat).
    """
    result = compute_pwi(subject_id)
    if not result:
        return {"subject_id": subject_id, "status": "no data"}
    return result


@app.get("/recommendations")
def get_recommendations(
    emotion: str,
    wellness_status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """
    Get recommendations based on emotion and wellness status.
    """
    recs = generate_recommendations(emotion, wellness_status)
    return {
        "emotion": emotion,
        "wellness_status": wellness_status,
        "recommendations": recs,
    }
