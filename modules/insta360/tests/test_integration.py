"""
Tests for Space360 integration endpoints and JobManager.
"""
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from api.main import app
import os

client = TestClient(app)

def test_ingest_immediate_response():
    with patch("api.main.os.path.exists", return_value=True), \
         patch("api.main.job_manager.create", return_value="1234-uuid"), \
         patch("api.main.pipeline_runner.run"):
        response = client.post("/ingest", json={"source_dir": "D:\\"})
        assert response.status_code == 202
        data = response.json()
        assert data["job_id"] == "1234-uuid"
        assert data["status"] == "queued"
        assert data["status_url"] == "/ingest-status/1234-uuid"

def test_get_ingest_status():
    with patch("api.main.job_manager.get", return_value={"job_id": "test", "status": "running"}):
        response = client.get("/ingest-status/test")
        assert response.status_code == 200
        assert response.json()["status"] == "running"

def test_get_ingest_summary_running():
    with patch("api.main.job_manager.get", return_value={"job_id": "test", "status": "running", "current_step": "detect", "summary": None}):
        response = client.get("/ingest-status/test/summary")
        assert response.status_code == 202
        assert response.json()["status"] == "running"
        assert response.json()["current_step"] == "detect"
        
def test_get_ingest_summary_complete():
    summary_data = {"total_files": 1, "stitched": 1, "uploaded": 1, "failed": 0, "gcs_uris": [], "completed_at_utc": "2026-08-26T00:00:00Z"}
    with patch("api.main.job_manager.get", return_value={"job_id": "test", "status": "complete", "summary": summary_data}):
        response = client.get("/ingest-status/test/summary")
        assert response.status_code == 200
        assert response.json()["total_files"] == 1

def test_job_manager_create():
    from core.job_manager import JobManager
    with patch("core.job_manager.os.makedirs"), patch("core.job_manager.os.path.exists", return_value=False), \
         patch("core.job_manager.JobManager._save_job"):
        jm = JobManager()
        job_id = jm.create("D:\\")
        assert len(job_id) == 36 # uuid length
        job = jm.get(job_id)
        assert job["status"] == "queued"
        assert job["source_dir"] == "D:\\"
        assert "detect" in job["steps"]

def test_job_manager_fail():
    from core.job_manager import JobManager
    with patch("core.job_manager.os.makedirs"), patch("core.job_manager.os.path.exists", return_value=False), \
         patch("core.job_manager.JobManager._save_job"):
        jm = JobManager()
        job_id = jm.create("D:\\")
        jm.fail(job_id, "detect", "error msg")
        job = jm.get(job_id)
        assert job["status"] == "failed"
        assert job["error"] == "error msg"
        assert job["steps"]["detect"]["status"] == "failed"

def test_health():
    with patch("api.routes.integration.shutil.which", return_value=True), \
         patch("api.routes.integration.JobManager"):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "1.0.0"
        assert data["ffmpeg_available"] is True
        assert "uptime_seconds" in data
        assert "gcs_connected" in data

def test_validate_dry_run():
    with patch("api.routes.integration.CameraDetector") as mock_cam_cls, \
         patch("api.routes.integration.FileValidator") as mock_val_cls:
        
        mock_cam = mock_cam_cls.return_value
        mock_cam.list_insv_files.return_value = ["a.insv"]
        
        mock_val = mock_val_cls.return_value
        mock_val.validate_batch.return_value = {
            "valid": 1, "invalid": 0, "results": [{"filepath": "a.insv", "valid": True, "errors": []}]
        }
        
        response = client.post("/ingest/validate", json={"source_dir": "D:\\"})
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["files_found"] == 1
        assert data["files_valid"] == 1
        
def test_list_jobs():
    with patch("api.main.job_manager.list_jobs", return_value=[{"job_id": "test"}]):
        response = client.get("/jobs")
        assert response.status_code == 200
        assert response.json()[0]["job_id"] == "test"
