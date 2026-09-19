import pytest
from unittest.mock import patch, MagicMock
from core.job_manager import JobManager

@pytest.fixture
def mock_firestore():
    with patch("core.job_manager.firestore.Client") as mock_client:
        mock_db = MagicMock()
        mock_client.return_value = mock_db
        yield mock_db

def test_create_job(mock_firestore):
    jm = JobManager()
    
    mock_doc_ref = MagicMock()
    mock_firestore.collection.return_value.document.return_value = mock_doc_ref
    
    job_id = jm.create("C:\\test\\dir")
    
    assert job_id is not None
    mock_firestore.collection.assert_called_with("jobs")
    mock_firestore.collection.return_value.document.assert_called_with(job_id)
    
    # Check that set was called with the job data
    mock_doc_ref.set.assert_called_once()
    args, _ = mock_doc_ref.set.call_args
    job_data = args[0]
    
    assert job_data["job_id"] == job_id
    assert job_data["source_dir"] == "C:\\test\\dir"
    assert job_data["status"] == "queued"
    assert "detect" in job_data["steps"]

def test_update_job(mock_firestore):
    jm = JobManager()
    mock_doc_ref = MagicMock()
    mock_firestore.collection.return_value.document.return_value = mock_doc_ref
    
    # Mock the existing document
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "job_id": "123",
        "status": "queued",
        "steps": {
            "detect": {"status": "pending", "result": None}
        }
    }
    mock_doc_ref.get.return_value = mock_doc
    
    jm.update("123", "detect", "running", {"files": 5})
    
    # Check that set was called with updated data
    mock_doc_ref.set.assert_called_once()
    args, _ = mock_doc_ref.set.call_args
    updated_data = args[0]
    
    assert updated_data["status"] == "running"
    assert updated_data["current_step"] == "detect"
    assert updated_data["steps"]["detect"]["status"] == "running"
    assert updated_data["steps"]["detect"]["result"] == {"files": 5}

def test_complete_job(mock_firestore):
    jm = JobManager()
    mock_doc_ref = MagicMock()
    mock_firestore.collection.return_value.document.return_value = mock_doc_ref
    
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "job_id": "123",
        "status": "running"
    }
    mock_doc_ref.get.return_value = mock_doc
    
    jm.complete("123", {"total_files": 10})
    
    mock_doc_ref.set.assert_called_once()
    args, _ = mock_doc_ref.set.call_args
    updated_data = args[0]
    
    assert updated_data["status"] == "complete"
    assert updated_data["current_step"] is None
    assert updated_data["summary"] == {"total_files": 10}

def test_fail_job(mock_firestore):
    jm = JobManager()
    mock_doc_ref = MagicMock()
    mock_firestore.collection.return_value.document.return_value = mock_doc_ref
    
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "job_id": "123",
        "status": "running",
        "steps": {
            "extract": {"status": "running", "result": None}
        }
    }
    mock_doc_ref.get.return_value = mock_doc
    
    jm.fail("123", "extract", "Error occurred")
    
    mock_doc_ref.set.assert_called_once()
    args, _ = mock_doc_ref.set.call_args
    updated_data = args[0]
    
    assert updated_data["status"] == "failed"
    assert updated_data["error"] == "Error occurred"
    assert updated_data["steps"]["extract"]["status"] == "failed"
    assert updated_data["steps"]["extract"]["result"] == {"error": "Error occurred"}

def test_get_job(mock_firestore):
    jm = JobManager()
    mock_doc_ref = MagicMock()
    mock_firestore.collection.return_value.document.return_value = mock_doc_ref
    
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {"job_id": "123", "status": "queued"}
    mock_doc_ref.get.return_value = mock_doc
    
    job = jm.get("123")
    
    assert job == {"job_id": "123", "status": "queued"}

def test_list_jobs(mock_firestore):
    jm = JobManager()
    
    mock_query = MagicMock()
    mock_firestore.collection.return_value.order_by.return_value.limit.return_value = mock_query
    
    mock_doc1 = MagicMock()
    mock_doc1.to_dict.return_value = {"job_id": "1", "status": "complete", "created_at_utc": "time1", "summary": {}}
    mock_doc2 = MagicMock()
    mock_doc2.to_dict.return_value = {"job_id": "2", "status": "queued", "created_at_utc": "time2", "summary": None}
    
    mock_query.stream.return_value = [mock_doc1, mock_doc2]
    
    jobs = jm.list_jobs(limit=2)
    
    assert len(jobs) == 2
    assert jobs[0]["job_id"] == "1"
    assert jobs[1]["job_id"] == "2"

def test_delete_job(mock_firestore):
    jm = JobManager()
    mock_doc_ref = MagicMock()
    mock_firestore.collection.return_value.document.return_value = mock_doc_ref
    
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc_ref.get.return_value = mock_doc
    
    result = jm.delete("123")
    
    assert result is True
    mock_doc_ref.delete.assert_called_once()
