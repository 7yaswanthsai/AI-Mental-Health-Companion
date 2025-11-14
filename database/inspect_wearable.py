from database.db_connection import get_database

# Connect to MongoDB
db = get_database()
wearable_data = db["wearable_data"]

print("✅ Connected to MongoDB\n")

# Fetch and display a few documents
for doc in wearable_data.find({}, {"_id": 0, "subject_id": 1, "eda": 1, "temp": 1}).limit(5):
    print("📍 Subject:", doc.get("subject_id"))
    eda_keys = list(doc.get("eda", {}).keys()) if isinstance(doc.get("eda"), dict) else []
    temp_keys = list(doc.get("temp", {}).keys()) if isinstance(doc.get("temp"), dict) else []
    print("EDA keys:", eda_keys)
    print("TEMP keys:", temp_keys)
    print("-" * 50)
