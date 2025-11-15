"""
Script to initialize the test user in MongoDB.
Run this once to create the test@pai.com user with password 123456.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connection import get_database
from backend.utils.password_hasher import hash_password
import datetime

def init_test_user():
    """Create the test user in MongoDB if it doesn't exist."""
    db = get_database()
    users_collection = db["users"]
    
    test_email = "test@pai.com"
    test_password = "123456"
    test_name = "Test User"
    test_subject_id = "S10"
    
    # Check if user already exists
    existing = users_collection.find_one({"email": test_email.lower()})
    if existing:
        try:
            print(f"[OK] Test user '{test_email}' already exists in MongoDB.")
        except UnicodeEncodeError:
            print(f"[OK] Test user '{test_email}' already exists in MongoDB.")
        print(f"   Subject ID: {existing.get('subject_id', 'N/A')}")
        return
    
    # Hash password
    hashed_password = hash_password(test_password)
    
    # Create user document
    user_doc = {
        "name": test_name,
        "email": test_email.lower(),
        "hashed_password": hashed_password,
        "subject_id": test_subject_id,
        "created_at": datetime.datetime.utcnow(),
    }
    
    # Insert into MongoDB
    try:
        users_collection.insert_one(user_doc)
        try:
            print(f"[OK] Test user created successfully!")
        except UnicodeEncodeError:
            print(f"[OK] Test user created successfully!")
        print(f"   Email: {test_email}")
        print(f"   Password: {test_password}")
        print(f"   Subject ID: {test_subject_id}")
        print(f"\nYou can now login with these credentials.")
    except Exception as e:
        try:
            print(f"[ERROR] Error creating test user: {e}")
        except UnicodeEncodeError:
            print(f"[ERROR] Error creating test user: {e}")
        raise

if __name__ == "__main__":
    print("Initializing test user in MongoDB...")
    print("=" * 50)
    try:
        init_test_user()
    except Exception as e:
        try:
            print(f"\n[ERROR] Failed to initialize test user: {e}")
        except UnicodeEncodeError:
            print(f"\n[ERROR] Failed to initialize test user: {e}")
        print("\nMake sure MongoDB is running and accessible.")
        sys.exit(1)

