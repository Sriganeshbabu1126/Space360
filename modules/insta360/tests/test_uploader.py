"""
Tests for core/uploader.py.
"""
import os
import json
from unittest.mock import patch, MagicMock, mock_open, call
from core.uploader import GCSUploader

@patch("core.uploader.storage")
@patch("os.path.getsize")
@patch("os.path.exists")
def test_upload_success(mock_exists, mock_getsize, mock_storage):
    mock_exists.return_value = True
    mock_getsize.return_value = 1000
    
    uploader = GCSUploader()
    uploader.bucket = MagicMock()
    uploader.bucket_name = "test-bucket"
    mock_blob = MagicMock()
    mock_blob.exists.return_value = False
    uploader.bucket.blob.return_value = mock_blob
    
    res = uploader.upload("C:\\test.mp4", "20260826")
    
    assert res["success"] is True
    assert res["size_bytes"] == 1000
    assert res["gcs_path"] == "insta360/20260826/test.mp4"
    assert res["gcs_uri"] == "gs://test-bucket/insta360/20260826/test.mp4"
    assert res["error"] is None
    mock_blob.upload_from_filename.assert_called_once_with("C:\\test.mp4", timeout=3600)

@patch("core.uploader.storage")
@patch("os.path.getsize")
@patch("os.path.exists")
def test_upload_failure(mock_exists, mock_getsize, mock_storage):
    mock_exists.return_value = True
    mock_getsize.return_value = 1000
    
    uploader = GCSUploader()
    uploader.bucket = MagicMock()
    mock_blob = MagicMock()
    mock_blob.exists.return_value = False
    mock_blob.upload_from_filename.side_effect = Exception("Upload error")
    uploader.bucket.blob.return_value = mock_blob
    
    res = uploader.upload("C:\\test.mp4", "20260826")
    
    assert res["success"] is False
    assert res["error"] == "Upload error"

@patch("os.path.getsize")
@patch("os.path.exists")
@patch("core.uploader.storage")
@patch("core.uploader.GCSUploader.upload")
def test_upload_pair_aborts(mock_upload, mock_storage, mock_exists, mock_getsize):
    mock_exists.return_value = True
    mock_getsize.return_value = 500
    
    mock_upload.return_value = {"success": False, "error": "failed"}
    
    uploader = GCSUploader()
    uploader.bucket_name = "test-bucket"
    res = uploader.upload_pair("C:\\test.mp4", "C:\\test.json", "20260826")
    
    assert res["pair_success"] is False
    assert res["mp4"]["success"] is False
    assert res["sidecar"]["success"] is False
    assert res["sidecar"]["error"] == "Aborted due to MP4 upload failure"
    assert mock_upload.call_count == 1 

@patch("core.uploader.storage")
@patch("core.uploader.GCSUploader.upload_pair")
def test_upload_batch(mock_upload_pair, mock_storage):
    mock_upload_pair.side_effect = [
        {"pair_success": False},
        {"pair_success": True}
    ]
    
    uploader = GCSUploader()
    res = uploader.upload_batch([{"mp4": "1", "sidecar": "1"}, {"mp4": "2", "sidecar": "2"}], "20260826")
    
    assert len(res) == 2
    assert res[0]["pair_success"] is False
    assert res[1]["pair_success"] is True

def test_get_gcs_path():
    uploader = GCSUploader()
    path = uploader._get_gcs_path("20260826", "VID_001.mp4")
    assert path == "insta360/20260826/VID_001.mp4"

@patch("builtins.open", new_callable=mock_open, read_data='{"video": {"codec": "old"}}')
def test_update_sidecar(mock_file):
    uploader = GCSUploader()
    upload_res = {
        "pair_success": True,
        "mp4": {"gcs_uri": "gs://bucket/mp4", "upload_duration_seconds": 1.0},
        "sidecar": {"gcs_uri": "gs://bucket/json", "upload_duration_seconds": 0.5}
    }
    
    uploader._update_sidecar("C:\\sidecar.json", upload_res)
    
    mock_file.assert_called_with("C:\\sidecar.json", "w", encoding="utf-8")
    handle = mock_file()
    written_content = "".join(call_arg[0][0] for call_arg in handle.write.call_args_list)
    parsed = json.loads(written_content)
    
    assert parsed["upload"]["status"] == "success"
    assert parsed["upload"]["mp4_gcs_uri"] == "gs://bucket/mp4"
    assert parsed["upload"]["sidecar_gcs_uri"] == "gs://bucket/json"
    assert parsed["upload"]["upload_duration_seconds"] == 1.5
    assert "uploaded_at_utc" in parsed["upload"]
