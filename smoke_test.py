import requests
import sys

BASE_URL = "https://space360-backend-1046334946412.asia-southeast1.run.app"

def test_health():
    print("Testing /sites endpoint (health check)...")
    try:
        response = requests.get(f"{BASE_URL}/sites/")
        if response.status_code == 200:
            print(f"✅ Success: /sites returned {len(response.json())} items.")
            return True
        else:
            print(f"❌ Failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_cors():
    print("Testing CORS headers...")
    headers = {"Origin": "https://space360.sgbapps.com"}
    try:
        response = requests.options(f"{BASE_URL}/sites/", headers=headers)
        if "access-control-allow-origin" in response.headers:
            print(f"✅ Success: CORS headers present for Origin https://space360.sgbapps.com")
            return True
        else:
            print("❌ Failed: No CORS headers found.")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    health_ok = test_health()
    cors_ok = test_cors()
    if health_ok and cors_ok:
        print("\n🎉 All production smoke tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️ Some smoke tests failed.")
        sys.exit(1)
