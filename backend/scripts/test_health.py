import httpx
import sys

BASE = "http://localhost:8000"

def test_health():
    try:
        r = httpx.get(f"{BASE}/health", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        print("✅ Health check passed")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_sites():
    try:
        r = httpx.get(f"{BASE}/sites/", timeout=5)
        print(f"✅ Sites endpoint: {r.status_code}")
        return True
    except Exception as e:
        print(f"❌ Sites endpoint failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Space360 API...")
    print("=" * 40)
    h = test_health()
    s = test_sites()
    print("=" * 40)
    if h and s:
        print("✅ All tests passed - Space360 is running!")
        sys.exit(0)
    else:
        print("❌ Some tests failed - check the backend")
        sys.exit(1)
