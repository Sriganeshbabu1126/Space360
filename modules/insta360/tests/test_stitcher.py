"""
Tests for core/stitcher.py.
"""
import os
import json
from unittest.mock import patch, mock_open, call
from core.stitcher import VideoStitcher

@patch("core.stitcher.subprocess.run")
def test_detect_codec_hevc(mock_run):
    mock_run.return_value.returncode = 0
    stitcher = VideoStitcher()
    res = stitcher._detect_codec(0)
    assert res["codec"] == "libx265"
    assert res["method"] == "software"
    
@patch("core.stitcher.subprocess.run")
def test_detect_codec_h264_fallback(mock_run):
    def side_effect(cmd, **kwargs):
        class Result:
            def __init__(self, code):
                self.returncode = code
        cmd_str = " ".join(cmd)
        if "libx265" in cmd_str:
            return Result(1)
        if "libx264" in cmd_str:
            return Result(0)
        return Result(1)
    mock_run.side_effect = side_effect
    
    stitcher = VideoStitcher()
    res = stitcher._detect_codec(0)
    assert res["codec"] == "libx264"
    assert res["method"] == "software"

@patch("core.stitcher.VideoStitcher._get_duration")
@patch("core.stitcher.VideoStitcher._run_ffmpeg")
@patch("core.stitcher.VideoStitcher._detect_codec")
@patch("core.stitcher.VideoStitcher._update_sidecar")
@patch("os.path.getsize")
@patch("os.path.exists")
@patch("os.makedirs")
def test_stitch_success(mock_makedirs, mock_exists, mock_getsize, mock_update_sidecar, mock_detect, mock_run, mock_duration):
    mock_exists.return_value = True
    mock_getsize.return_value = 12345
    mock_detect.return_value = {"codec": "hevc_nvenc", "method": "nvenc", "reason": "ok"}
    mock_run.return_value = (True, "", 1.2)
    mock_duration.return_value = 10.5
    
    stitcher = VideoStitcher()
    res = stitcher.stitch("C:\\vid.insv", "C:\\out")
    
    assert res["success"] is True
    assert res["stitch"]["status"] == "success"
    assert res["stitch"]["codec"] == "hevc_nvenc"
    assert res["duration_seconds"] == 10.5
    assert res["output_size_bytes"] == 12345
    assert res["error"] is None
    assert res["dst"] == "C:\\out\\vid_stitched.mp4"

@patch("core.stitcher.VideoStitcher._get_duration")
@patch("core.stitcher.VideoStitcher._run_ffmpeg")
@patch("core.stitcher.VideoStitcher._detect_codec")
@patch("os.path.getsize")
@patch("os.path.exists")
@patch("os.makedirs")
def test_stitch_ffmpeg_failure(mock_makedirs, mock_exists, mock_getsize, mock_detect, mock_run, mock_duration):
    def exists_side_effect(path):
        return path == "C:\\vid.insv"
    mock_exists.side_effect = exists_side_effect
    mock_getsize.return_value = 12345
    
    mock_detect.return_value = {"codec": "hevc_nvenc", "method": "nvenc", "reason": "ok"}
    mock_run.return_value = (False, "ffmpeg crash", 1.2)
    mock_duration.return_value = 10.5
    
    stitcher = VideoStitcher()
    res = stitcher.stitch("C:\\vid.insv", "C:\\out")
    
    assert res["success"] is False
    assert res["stitch"]["status"] == "failed"
    assert res["error"] == "ffmpeg crash"

@patch("builtins.open", new_callable=mock_open, read_data='{"video": {"codec": "old"}}')
def test_update_sidecar(mock_file):
    stitcher = VideoStitcher()
    stitch_res = {
        "duration_seconds": 10.0,
        "output_size_bytes": 1000000,
        "stitch": {
            "codec": "hevc_nvenc",
            "encode_method": "nvenc",
            "status": "success",
            "engine": "ffmpeg",
            "stitch_duration_seconds": 1.2,
            "output_path": "C:\\out.mp4"
        }
    }
    
    stitcher._update_sidecar("C:\\sidecar.json", stitch_res)
    
    mock_file.assert_called_with("C:\\sidecar.json", "w", encoding="utf-8")
    
    handle = mock_file()
    written_args = [call_arg[0][0] for call_arg in handle.write.call_args_list]
    written_content = "".join(written_args)
    parsed = json.loads(written_content)
    
    assert parsed["video"]["codec"] == "hevc_nvenc"
    assert parsed["video"]["bitrate_bps"] == 800000
    assert parsed["stitch"]["status"] == "success"
    assert parsed["stitch"]["engine"] == "ffmpeg"

@patch("core.stitcher.VideoStitcher.stitch")
def test_stitch_batch(mock_stitch):
    mock_stitch.side_effect = [{"success": True}, {"success": False}]
    
    stitcher = VideoStitcher()
    res = stitcher.stitch_batch(["a.insv", "b.insv"], "out")
    
    assert len(res) == 2
    assert res[0]["success"] is True
    assert res[1]["success"] is False

@patch("core.stitcher.subprocess.run")
def test_detect_codec_first_works(mock_run):
    def side_effect(cmd, **kwargs):
        class Result:
            def __init__(self, code):
                self.returncode = code
        cmd_str = " ".join(cmd)
        if "libx265" in cmd_str:
            return Result(1)
        if "libx264" in cmd_str:
            return Result(0)
        return Result(1)
    mock_run.side_effect = side_effect
    
    stitcher = VideoStitcher()
    res = stitcher._detect_codec(0)
    
    assert res["codec"] == "libx264"
    assert res["method"] == "software"

def test_detect_codec_large_file():
    stitcher = VideoStitcher()
    res = stitcher._detect_codec(300 * 1024 * 1024)  # 300MB
    assert res["codec"] == "libx264"
    assert res["reason"] == "Large file (>200MB): using H.264 for speed"

@patch("core.stitcher.subprocess.run")
def test_run_ffmpeg_timeout(mock_run):
    import subprocess
    mock_run.side_effect = subprocess.TimeoutExpired(cmd="ffmpeg", timeout=600)
    
    stitcher = VideoStitcher()
    success, err, duration = stitcher._run_ffmpeg("in.insv", "out.mp4", {"codec": "libx264", "method": "software"})
    
    assert success is False
    assert "timeout after" in err
    assert duration >= 0
