from pymongo import MongoClient
from datetime import datetime

def get_mongo_client():
    try:
        client = MongoClient("mongodb://localhost:27017/")
        print("✅ MongoDB connection established!")
        return client
    except Exception as e:
        print("❌ Error connecting to MongoDB:", e)
        return None

def fetch_chat_history():
    client = get_mongo_client()
    if not client:
        return

    db = client["pai_mhc_db"]
    collection = db["chat_logs"]

    try:
        # Sort chats by timestamp (latest first)
        chats = collection.find().sort("timestamp", -1)

        print("\n📖 Chat History:")
        print("="*60)
        for chat in chats:
            ts = chat.get("timestamp", datetime.now()).strftime("%Y-%m-%d %H:%M:%S") if isinstance(chat.get("timestamp"), datetime) else chat.get("timestamp")
            print(f"[{ts}]")
            print(f"🧑 User: {chat.get('user_input')}")
            print(f"🤖 Bot: {chat.get('bot_response')}")
            print(f"💭 Emotion: {chat.get('predicted_emotion')} ({chat.get('probability'):.3f})")
            print("-"*60)

    except Exception as e:
        print("❌ Error fetching chat history:", e)
    finally:
        client.close()

if __name__ == "__main__":
    fetch_chat_history()
