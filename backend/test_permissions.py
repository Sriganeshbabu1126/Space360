import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fastapi.testclient import TestClient
from app.auth import get_current_user
from main import app
from app.database import SessionLocal
from app.models import LocationPoint

client = TestClient(app)

def mock_get_current_user_admin():
    return {"email": "wincadsg@gmail.com"}

def mock_get_current_user_contractor():
    return {"email": "some.contractor@test.com"}

def test_permissions():
    db = SessionLocal()
    loc = db.query(LocationPoint).first()
    location_id = loc.id if loc else "test-loc"

    # 1. Create a test issue as admin
    app.dependency_overrides[get_current_user] = mock_get_current_user_admin
    payload = {
        "title": "Test Critical Issue",
        "description": "Testing permissions for critical status.",
        "location_id": location_id
    }
    
    resp = client.post("/issues/", json=payload)
    if resp.status_code != 201:
        print("Failed to create issue:", resp.text)
        return
        
    issue_id = resp.json()['id']
    print(f"Created issue {issue_id}")
    
    # 2. Try updating to 'critical' as non-admin
    app.dependency_overrides[get_current_user] = mock_get_current_user_contractor
    update_payload = {"status": "critical"}
    resp = client.put(f"/issues/{issue_id}", json=update_payload)
    print(f"Status Code: {resp.status_code}")
    print(f"Response: {resp.text}")
    assert resp.status_code == 403
    assert "Only admins can set status to pending/closed/critical" in resp.text
    print("✓ Non-admin test passed")
    
    # 3. Try updating to 'critical' as admin
    app.dependency_overrides[get_current_user] = mock_get_current_user_admin
    resp = client.put(f"/issues/{issue_id}", json=update_payload)
    print(f"Status Code: {resp.status_code}")
    if resp.status_code == 200:
        print(f"Response Status: {resp.json()['status']}")
        assert resp.json()['status'] == 'critical'
        print("✓ Admin test passed")
    else:
        print(f"Failed: {resp.text}")

if __name__ == "__main__":
    test_permissions()
