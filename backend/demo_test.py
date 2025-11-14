"""
Demo test script for PAI-MHC system.
Tests login, chat, wellness, and recommendations endpoints.
"""
import requests
import json
from datetime import datetime

API_BASE = "http://127.0.0.1:8000"
LOGIN_URL = f"{API_BASE}/login"
CHAT_URL = f"{API_BASE}/chat"
WELLNESS_URL = f"{API_BASE}/wellness"
RECS_URL = f"{API_BASE}/recommendations"
HISTORY_URL = f"{API_BASE}/history"

# Test credentials
EMAIL = "test@pai.com"
PASSWORD = "123456"
SUBJECT_ID = "S10"


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_login():
    """Test login and get JWT token."""
    print_section("1. Testing Login")
    try:
        response = requests.post(
            LOGIN_URL,
            json={"email": EMAIL, "password": PASSWORD},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        token = data.get("access_token")
        if token:
            print(f"✅ Login successful!")
            print(f"   Token: {token[:50]}...")
            return token
        else:
            print("❌ No token in response")
            return None
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None


def test_chat(token, subject_id):
    """Test chat endpoint with emotion detection."""
    print_section("2. Testing Chat Endpoint")
    headers = {"Authorization": f"Bearer {token}"}
    
    test_messages = [
        "I'm feeling really sad today",
        "I'm so happy about my exam results!",
        "I'm anxious about the presentation tomorrow",
    ]
    
    for msg in test_messages:
        try:
            print(f"\n📝 Sending: '{msg}'")
            response = requests.post(
                CHAT_URL,
                headers=headers,
                json={"text": msg, "subject_id": subject_id},
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            
            print(f"   ✅ Response received")
            print(f"   🎭 Emotion: {data.get('emotion', 'N/A')}")
            print(f"   📊 Probability: {data.get('probability', 0):.3f}")
            print(f"   💬 Bot: {data.get('text', 'N/A')[:80]}...")
            
            wellness = data.get("wellness", {})
            if wellness.get("pwi") is not None:
                print(f"   🩺 PWI: {wellness.get('pwi', 0):.1f} ({wellness.get('status', 'N/A')})")
            
            recs = data.get("recommendations", [])
            if recs:
                print(f"   💡 Recommendations: {len(recs)} items")
                for i, rec in enumerate(recs[:2], 1):
                    print(f"      {i}. {rec[:60]}...")
            
            if data.get("escalate"):
                print(f"   ⚠️  Crisis escalation triggered")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")


def test_wellness(token, subject_id):
    """Test wellness endpoint."""
    print_section("3. Testing Wellness Endpoint")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{WELLNESS_URL}/{subject_id}",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Wellness data retrieved")
        print(f"   Subject ID: {data.get('subject_id', 'N/A')}")
        
        pwi = data.get("pwi")
        if pwi is not None:
            print(f"   🩺 PWI Score: {pwi:.1f}")
            print(f"   📊 Status: {data.get('status', 'N/A')}")
            
            features = data.get("features", {})
            if features:
                print(f"   📈 Features:")
                for key, value in list(features.items())[:5]:
                    if value is not None:
                        print(f"      - {key}: {value:.2f}")
        else:
            print(f"   ⚠️  No PWI data available")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def test_recommendations(token):
    """Test recommendations endpoint."""
    print_section("4. Testing Recommendations Endpoint")
    headers = {"Authorization": f"Bearer {token}"}
    
    test_cases = [
        ("sadness", "Stressed"),
        ("joy", "Calm"),
        ("anxiety", None),
    ]
    
    for emotion, wellness_status in test_cases:
        try:
            params = {"emotion": emotion}
            if wellness_status:
                params["wellness_status"] = wellness_status
            
            print(f"\n📋 Testing: emotion={emotion}, wellness={wellness_status or 'N/A'}")
            response = requests.get(
                RECS_URL,
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            recs = data.get("recommendations", [])
            print(f"   ✅ Received {len(recs)} recommendations:")
            for i, rec in enumerate(recs, 1):
                print(f"      {i}. {rec}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")


def test_history(token):
    """Test chat history endpoint."""
    print_section("5. Testing Chat History Endpoint")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            HISTORY_URL,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        history = data if isinstance(data, list) else data.get("history", [])
        print(f"✅ Retrieved {len(history)} chat history entries")
        
        if history:
            print(f"\n   Recent entries:")
            for entry in history[:3]:
                print(f"   - {entry.get('text', 'N/A')[:50]}...")
                print(f"     Emotion: {entry.get('emotion', 'N/A')}, "
                      f"Timestamp: {entry.get('timestamp', 'N/A')[:19]}")
        else:
            print("   No history entries found")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all demo tests."""
    print("\n" + "🧠" * 30)
    print("  PAI-MHC System Demo Test Script")
    print("🧠" * 30)
    print(f"\n⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 API Base: {API_BASE}")
    print(f"👤 Test User: {EMAIL}")
    print(f"🆔 Subject ID: {SUBJECT_ID}")
    
    # Step 1: Login
    token = test_login()
    if not token:
        print("\n❌ Cannot proceed without authentication token.")
        return
    
    # Step 2: Test Chat
    test_chat(token, SUBJECT_ID)
    
    # Step 3: Test Wellness
    test_wellness(token, SUBJECT_ID)
    
    # Step 4: Test Recommendations
    test_recommendations(token)
    
    # Step 5: Test History
    test_history(token)
    
    # Summary
    print_section("Summary")
    print("✅ Demo test completed!")
    print("\n📝 Next steps:")
    print("   1. Check MLflow UI for logged predictions")
    print("   2. Verify MongoDB for stored chat logs")
    print("   3. Test Streamlit frontend: streamlit run frontend_streamlit/app.py")
    print("   4. Test React Native app: cd mobile_app_new && npx expo start")
    print(f"\n⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


if __name__ == "__main__":
    main()

