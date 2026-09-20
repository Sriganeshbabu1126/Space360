import pytest
from fastapi.testclient import TestClient
from main import app
from app.auth import get_current_user
from app.database import get_db
from app.models import Site, FloorPlan, InspectionPath, InspectionPathPoint, generate_uuid

client = TestClient(app)

def mock_get_current_user():
    return {"uid": "test_user"}

app.dependency_overrides[get_current_user] = mock_get_current_user

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    from app.database import SessionLocal
    db = SessionLocal()
    
    # Create test site and floor plan
    site_id = "test-site-" + generate_uuid()
    fp_id = "test-fp-" + generate_uuid()
    
    test_site = Site(id=site_id, name="Test Site", created_by="test_user")
    db.add(test_site)
    db.commit()
    
    test_fp = FloorPlan(id=fp_id, site_id=site_id, label="Test FP")
    db.add(test_fp)
    db.commit()
    
    # Pass IDs to tests
    pytest.site_id = site_id
    pytest.fp_id = fp_id
    
    yield
    
    # Cleanup
    paths = db.query(InspectionPath).filter(InspectionPath.site_id == site_id).all()
    for p in paths:
        db.query(InspectionPathPoint).filter(InspectionPathPoint.path_id == p.id).delete()
        db.delete(p)
    db.commit()
    
    db.delete(test_fp)
    db.delete(test_site)
    db.commit()
    db.close()

def test_create_path():
    payload = {
        "name": "Test Path",
        "site_id": pytest.site_id,
        "floor_plan_id": pytest.fp_id,
        "points": [
            {
                "sequence_order": 1,
                "x_percent": 10.5,
                "y_percent": 20.5,
                "label": "Start"
            }
        ]
    }
    response = client.post("/api/paths/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Path"
    assert len(data["points"]) == 1

def test_list_paths():
    response = client.get(f"/api/paths/?floor_plan_id={pytest.fp_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

def test_add_point_to_path():
    payload = {
        "name": "Test Path 2",
        "site_id": pytest.site_id,
        "floor_plan_id": pytest.fp_id,
        "points": []
    }
    response = client.post("/api/paths/", json=payload)
    path_id = response.json()["id"]
    
    pt_payload = {
        "sequence_order": 2,
        "x_percent": 30.0,
        "y_percent": 40.0,
        "label": "End"
    }
    pt_resp = client.post(f"/api/paths/{path_id}/points", json=pt_payload)
    assert pt_resp.status_code == 201
    pt_data = pt_resp.json()
    assert pt_data["label"] == "End"

def test_delete_path():
    payload = {
        "name": "Test Path 3",
        "site_id": pytest.site_id,
        "floor_plan_id": pytest.fp_id,
        "points": []
    }
    response = client.post("/api/paths/", json=payload)
    path_id = response.json()["id"]
    
    del_resp = client.delete(f"/api/paths/{path_id}")
    assert del_resp.status_code == 204
    
    get_resp = client.get(f"/api/paths/{path_id}")
    assert get_resp.status_code == 404
