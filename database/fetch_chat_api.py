from fastapi import APIRouter
from database.db_connection import get_database

router = APIRouter()

@router.get("/history")
def get_chat_history():
    """Fetch all chat logs from MongoDB."""
    db = get_database()
    collection = db["chat_logs"]

    chat_history = []
    for chat in collection.find().sort("timestamp", -1):  # newest first
        chat_history.append({
            "timestamp": chat.get("timestamp"),
            "user_input": chat.get("user_input"),
            "predicted_emotion": chat.get("predicted_emotion"),
            "probability": chat.get("probability"),
            "bot_response": chat.get("bot_response"),
        })

    return {"count": len(chat_history), "history": chat_history}
