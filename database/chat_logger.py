# database/chat_logger.py

from datetime import datetime
from .db_connection import get_database
from database.db_connection import chat_logs_collection  # ✅ absolute import works


# Connect to MongoDB
db = get_database()
chat_collection = db["chat_logs"]

def log_chat(
    user_input: str,
    emotion: str,
    probability: float,
    response: str,
    subject_id: str | None = None,
    wellness: dict | None = None,
    recommendations: list[str] | None = None,
    tags: list[str] | None = None,
    tone: str | None = None,
    escalate: bool | None = None,
):
    """Insert a chat log into MongoDB."""
    chat_data = {
        "timestamp": datetime.utcnow(),
        "user_input": user_input,
        "predicted_emotion": emotion,
        "probability": probability,
        "bot_response": response,
    }
    if subject_id:
        chat_data["subject_id"] = subject_id
    if wellness:
        chat_data["wellness"] = wellness
    if recommendations:
        chat_data["recommendations"] = recommendations
    if tags:
        chat_data["tags"] = tags
    if tone:
        chat_data["tone"] = tone
    if escalate is not None:
        chat_data["escalate"] = escalate
    chat_collection.insert_one(chat_data)
    return {"status": "success"}

def get_all_chats(limit: int = 10):
    """Retrieve recent chat logs."""
    chats = list(chat_collection.find().sort("timestamp", -1).limit(limit))
    for chat in chats:
        chat["_id"] = str(chat["_id"])  # convert ObjectId to string
    return chats
