"""
Quick test script to verify login works with test user.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.auth import authenticate_user

def test_login():
    """Test login with test user credentials."""
    email = "test@pai.com"
    password = "123456"
    
    print(f"Testing login with:")
    print(f"  Email: {email}")
    print(f"  Password: {password}")
    print("=" * 50)
    
    user = authenticate_user(email, password)
    
    if user:
        print("[OK] Login successful!")
        print(f"  Email: {user['email']}")
        print(f"  Name: {user.get('name', 'N/A')}")
        print(f"  Subject ID: {user.get('subject_id', 'N/A')}")
    else:
        print("[ERROR] Login failed - Invalid email or password")
        print("\nPossible issues:")
        print("  1. Email typo (should be test@pai.com, not test@pai.co)")
        print("  2. Password incorrect")
        print("  3. User not in MongoDB - run: python backend/init_test_user.py")

if __name__ == "__main__":
    test_login()

