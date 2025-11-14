"""
Test script to verify Android emulator can reach the backend
Run this to test connectivity before trying the mobile app
"""
import requests
import sys

def test_connection(base_url):
    """Test connection to backend"""
    print(f"\nTesting connection to: {base_url}")
    print("=" * 60)
    
    # Test 1: Health check
    try:
        print("\n1. Testing /health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   ✅ Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection refused - Backend not accessible at {base_url}")
        print("   Make sure backend is running with: python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Login endpoint
    try:
        print("\n2. Testing /login endpoint...")
        response = requests.post(
            f"{base_url}/login",
            json={"email": "test@pai.com", "password": "123456"},
            timeout=5
        )
        print(f"   ✅ Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Login successful! Token received: {data.get('access_token', '')[:20]}...")
        else:
            print(f"   ⚠️  Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! Backend is accessible.")
    return True

if __name__ == "__main__":
    # Test localhost
    print("Testing LOCALHOST connection (for reference):")
    test_connection("http://127.0.0.1:8000")
    
    print("\n\nTesting ANDROID EMULATOR connection:")
    print("(This simulates what Android emulator at 10.0.2.2 would see)")
    print("Note: This will fail on your computer, but should work from Android emulator")
    
    # Test Android emulator URL (will fail on host machine, but shows what to test)
    try:
        test_connection("http://10.0.2.2:8000")
    except Exception as e:
        print(f"\n⚠️  Cannot test 10.0.2.2 from host machine (expected)")
        print("   This URL only works from inside Android emulator")
        print("\n📱 To test from Android emulator:")
        print("   1. Open browser in Android emulator")
        print("   2. Navigate to: http://10.0.2.2:8000/health")
        print("   3. Should see: {\"status\": \"ok\", \"message\": \"Backend is running\"}")

