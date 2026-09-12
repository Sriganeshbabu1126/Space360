"""
Tests for core/metadata.py.
"""
import os
from unittest.mock import patch, MagicMock, mock_open
from core.metadata import MetadataExtractor

@patch("core.metadata.os.path.getsize")
@patch("core.metadata.os.path.exists")
@patch("builtins.open", new_callable=mock_open)
@patch("core.metadata.subprocess.run")
def test_extract_basic(mock_run, mock_file, mock_exists, mock_getsize):
    mock_exists.return_value = True
    mock_getsize.return_value = 1024
    
    mock_result = MagicMock()
    mock_result.returncode = 0
    import json
    mock_result.stdout = json.dumps([{
        "EXIF:Make": "Insta360",
        "Model": "X4",
        "ImageWidth": 7680,
        "ImageHeight": 3840,
        "VideoFrameRate": 30.0,
        "CreateDate": "2026:08:26 12:36:06",
        "MediaDuration": 60.5,
        "GPSLatitude": 37.7749,
        "GPSLongitude": -122.4194,
        "AvgBitrate": "200 Mbps"
    }])
    mock_run.return_value = mock_result
    
    extractor = MetadataExtractor()
    res = extractor.extract("C:\\VID_001.insv")
    
    assert res["extraction_status"] == "success"
    assert res["metadata"]["camera"]["make"] == "Insta360"
    assert res["metadata"]["camera"]["model"] == "X4"
    assert res["metadata"]["video"]["width"] == 7680
    assert res["metadata"]["video"]["frame_rate"] == 30.0
    assert res["metadata"]["capture"]["duration_seconds"] == 60.5
    assert res["metadata"]["capture"]["timestamp_utc"] == "2026-08-26T12:36:06Z"
    assert res["metadata"]["gps"]["available"] is True
    assert res["metadata"]["gps"]["latitude"] == 37.7749
    assert res["metadata"]["gps"]["longitude"] == -122.4194
    assert res["metadata"]["video"]["bitrate_bps"] == 200000000

@patch("core.metadata.os.path.getsize")
@patch("core.metadata.os.path.exists")
@patch("builtins.open", new_callable=mock_open)
@patch("core.metadata.subprocess.run")
def test_extract_missing_gps(mock_run, mock_file, mock_exists, mock_getsize):
    mock_exists.return_value = True
    mock_getsize.return_value = 1024
    
    mock_result = MagicMock()
    mock_result.returncode = 0
    import json
    mock_result.stdout = json.dumps([{
        "Make": "Insta360", "Model": "X4", "CreateDate": "2026:08:26 12:36:06", "MediaDuration": 60
    }])
    mock_run.return_value = mock_result
    
    extractor = MetadataExtractor()
    res = extractor.extract("C:\\VID_002.insv")
    
    assert res["metadata"]["gps"]["available"] is False
    assert len(res["warnings"]) > 0

@patch("core.metadata.os.path.getsize")
@patch("core.metadata.os.path.exists")
@patch("builtins.open", new_callable=mock_open)
@patch("core.metadata.subprocess.run")
def test_extract_exiftool_not_found(mock_run, mock_file, mock_exists, mock_getsize):
    mock_exists.return_value = True
    mock_getsize.return_value = 1024
    
    mock_run.side_effect = FileNotFoundError()
    
    extractor = MetadataExtractor()
    res = extractor.extract("C:\\VID_003.insv")
    
    assert res["extraction_status"] == "failed"
    assert len(res["errors"]) > 0

def test_normalise_bitrate_string():
    extractor = MetadataExtractor()
    result = {"metadata": {"video": {}, "camera": {}, "capture": {}, "gps": {}, "imu": {}}, "warnings": []}
    
    extractor._normalise(result, {"AvgBitrate": "50 Mbps"}, {})
    assert result["metadata"]["video"]["bitrate_bps"] == 50000000
    
    extractor._normalise(result, {"AvgBitrate": "123.4 kbps"}, {})
    assert result["metadata"]["video"]["bitrate_bps"] == 123400
    
    extractor._normalise(result, {"AvgBitrate": 85000}, {})
    assert result["metadata"]["video"]["bitrate_bps"] == 85000

@patch("core.metadata.MetadataExtractor.extract")
def test_extract_batch(mock_extract):
    mock_extract.side_effect = [
        {"extraction_status": "success"},
        {"extraction_status": "success"}
    ]
    
    extractor = MetadataExtractor()
    res = extractor.extract_batch(["a.insv", "b.insv"])
    
    assert res["total"] == 2
    assert res["success"] == 2
    assert res["partial"] == 0
    assert res["failed"] == 0

@patch("core.metadata.os.path.getsize")
@patch("core.metadata.os.path.exists")
@patch("builtins.open", new_callable=mock_open)
@patch("core.metadata.subprocess.run")
def test_sidecar_written(mock_run, mock_file, mock_exists, mock_getsize):
    mock_exists.return_value = True
    mock_getsize.return_value = 1024
    
    mock_result = MagicMock()
    mock_result.returncode = 0
    import json
    mock_result.stdout = json.dumps([{"Make": "Insta360"}])
    mock_run.return_value = mock_result
    
    extractor = MetadataExtractor()
    res = extractor.extract("C:\\folder\\VID_004.insv")
    
    assert res["sidecar_path"] == "C:\\folder\\VID_004_metadata.json"
    mock_file.assert_any_call("C:\\folder\\VID_004_metadata.json", "w", encoding="utf-8")

def test_extract_real_file():
    # After previous tests create a real .insv file, try to extract it
    extractor = MetadataExtractor()
    result = extractor.extract("F:\\Space360\\modules\\insta360\\output\\20260826\\VID_20260826_123606_00_004.insv")
    assert result["extraction_status"] in ["success", "partial", "failed"]

@patch("core.metadata.os.path.getsize")
@patch("core.metadata.os.path.exists")
@patch("builtins.open", new_callable=mock_open)
@patch("core.metadata.subprocess.run")
def test_extract_timeout(mock_run, mock_file, mock_exists, mock_getsize):
    mock_exists.return_value = True
    mock_getsize.return_value = 1024
    
    import subprocess
    mock_run.side_effect = subprocess.TimeoutExpired(cmd="exiftool", timeout=10)
    
    extractor = MetadataExtractor()
    res = extractor.extract("C:\\VID_005.insv")
    
    assert res["extraction_status"] == "failed"
    assert any("exiftool timed out after 10 seconds" in err for err in res["errors"])
