import os
from pymongo import MongoClient

def get_database():
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("MONGODB_DB", "pai_mhc_db")
    client = MongoClient(mongodb_uri)
    db = client[db_name]
    return db

db = get_database()
chat_logs_collection = db["chat_logs"]
print("✅ MongoDB connected successfully!")
