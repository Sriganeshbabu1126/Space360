"""
Tests for core/camera.py and core/validator.py.
"""
import os
import subprocess
from unittest.mock import patch, MagicMock, mock_open
from core.camera import CameraDetector
from core.validator import FileValidator

@patch("core.camera.subprocess.check_output")
def test_detect_no_drives(mock_check_output):
    mock_check_output.return_value = "DeviceID  \n\n"
    detector = CameraDetector()
    result = detector.detect()
    assert result["mode"] == "not_connected"
    assert result["file_count"] == 0
    assert result["drive"] is None

@patch("core.camera.os.walk")
@patch("core.camera.os.path.isdir")
@patch("core.camera.subprocess.check_output")
def test_detect_usb_storage(mock_check_output, mock_isdir, mock_walk):
    mock_check_output.return_value = "DeviceID  \nD:  \n\n"
    def isdir_side_effect(path):
        return path.endswith("DCIM")
    mock_isdir.side_effect = isdir_side_effect
    mock_walk.return_value = [
        ("D:\\DCIM\\Camera", [], ["VID_001.insv", "VID_002.insv", "ignore.txt"])
    ]
    detector = CameraDetector()
    result = detector.detect()
    assert result["mode"] == "usb_storage"
    assert result["drive"] == "D:\\"
    assert result["file_count"] == 2

@patch("core.camera.os.walk")
@patch("core.camera.os.path.isdir")
@patch("core.camera.subprocess.check_output")
def test_detect_no_insv_files(mock_check_output, mock_isdir, mock_walk):
    mock_check_output.return_value = "DeviceID  \nD:  \n\n"
    def isdir_side_effect(path):
        return path.endswith("DCIM")
    mock_isdir.side_effect = isdir_side_effect
    mock_walk.return_value = [
        ("D:\\DCIM\\Camera", [], ["pic.jpg", "other.txt"])
    ]
    detector = CameraDetector()
    result = detector.detect()
    assert result["mode"] == "not_connected"
    assert result["file_count"] == 0

@patch("core.camera.shutil.copy2")
@patch("core.camera.os.path.getsize")
@patch("core.camera.os.path.exists")
@patch("core.camera.os.makedirs")
@patch("builtins.open", new_callable=mock_open)
def test_transfer_copies_files(mock_open_file, mock_makedirs, mock_exists, mock_getsize, mock_copy2):
    mock_exists.return_value = False
    mock_getsize.return_value = 1024
    
    detector = CameraDetector()
    result = detector.transfer_files(["D:\\VID_20260826_001.insv"], "C:\\out")
    
    assert result["total"] == 1
    assert result["copied"] == 1
    assert result["files"][0]["status"] == "copied"
    assert result["files"][0]["integrity"] == "ok"

@patch("core.camera.os.path.getsize")
@patch("core.camera.os.path.exists")
@patch("core.camera.os.makedirs")
@patch("builtins.open", new_callable=mock_open)
def test_transfer_skips_duplicate(mock_open_file, mock_makedirs, mock_exists, mock_getsize):
    mock_exists.return_value = True
    mock_getsize.return_value = 1024
    
    detector = CameraDetector()
    result = detector.transfer_files(["D:\\VID_20260826_001.insv"], "C:\\out")
    
    assert result["total"] == 1
    assert result["skipped"] == 1
    assert result["files"][0]["status"] == "skipped"
    assert result["files"][0]["integrity"] == "skipped"

@patch("core.camera.shutil.copy2")
@patch("core.camera.os.path.getsize")
@patch("core.camera.os.path.exists")
@patch("core.camera.os.makedirs")
@patch("builtins.open", new_callable=mock_open)
def test_transfer_handles_failure(mock_open_file, mock_makedirs, mock_exists, mock_getsize, mock_copy2):
    mock_exists.return_value = False
    mock_getsize.return_value = 1024
    mock_copy2.side_effect = OSError("Disk full")
    
    detector = CameraDetector()
    result = detector.transfer_files(["D:\\VID_20260826_001.insv"], "C:\\out")
    
    assert result["total"] == 1
    assert result["failed"] == 1
    assert result["files"][0]["status"] == "failed"
    assert result["files"][0]["error"] == "Disk full"

@patch("core.validator.os.access")
@patch("core.validator.os.path.getsize")
@patch("core.validator.os.path.exists")
@patch("builtins.open", new_callable=mock_open)
def test_validate_valid_file(mock_open_file, mock_exists, mock_getsize, mock_access):
    mock_exists.return_value = True
    mock_access.return_value = True
    mock_getsize.return_value = 2 * 1024 * 1024 # 2MB
    
    validator = FileValidator()
    res = validator.validate_insv("test.insv")
    
    assert res["valid"] is True
    assert all(res["checks"].values())

@patch("core.validator.os.path.exists")
def test_validate_missing_file(mock_exists):
    mock_exists.return_value = False
    
    validator = FileValidator()
    res = validator.validate_insv("missing.insv")
    
    assert res["valid"] is False
    assert res["checks"]["exists"] is False
