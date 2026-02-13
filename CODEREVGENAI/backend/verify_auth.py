import requests
import sys

# Configuration
BASE_URL = "http://127.0.0.1:8000"

def verify_authentication():
    print("🚀 Starting Authentication Flow Verification...")
    
    # Test User Credentials
    test_user = {
        "username": "auth_verify_user",
        "email": "verify@example.com",
        "password": "StrongPassword123!"
    }
    
    # 1. Signup
    print(f"\n1️⃣  Testing Signup for '{test_user['username']}'...")
    try:
        response = requests.post(f"{BASE_URL}/api/signup", json=test_user)
        
        if response.status_code == 200:
            print("   ✅ Signup Successful")
        elif response.status_code == 400 and "exists" in response.text:
            print("   ⚠️  User already exists (Proceeding to login)")
        else:
            print(f"   ❌ Signup Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
        print("      Ensure the backend server is running (python backend/main.py)")
        return False

    # 2. Login
    print(f"\n2️⃣  Testing Login...")
    try:
        response = requests.post(f"{BASE_URL}/api/login", json={
            "username": test_user["username"],
            "password": test_user["password"]
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            print(f"   ✅ Login Successful")
            print(f"   🔑 Token received: {token[:15]}...")
        else:
            print(f"   ❌ Login Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
        return False

    # 3. Cleanup (Delete User)
    print(f"\n3️⃣  Cleaning up (Deleting test user)...")
    try:
        response = requests.delete(f"{BASE_URL}/api/profile/{test_user['username']}")
        if response.status_code == 200:
            print("   ✅ User deleted successfully")
        else:
            print(f"   ⚠️  Delete failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Cleanup Error: {e}")

    print("\n✨ Authentication Flow Verified Successfully!")
    return True

if __name__ == "__main__":
    verify_authentication()