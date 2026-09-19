from fastapi import APIRouter
from pydantic import BaseModel
from core.camera import CameraDetector
from core.validator import FileValidator
import time
import shutil
import os
from core.job_manager import JobManager

router = APIRouter()

START_TIME = time.time()

@router.get("/health")
def health_check():
    from core.stitcher import VideoStitcher
    
    stitcher = VideoStitcher()
    codec_info = stitcher._detect_codec(0)
    
    gcs_connected = False
    try:
        from google.cloud import storage
        import logging
        logger = logging.getLogger("insta360.health")
        GCS_BUCKET = os.getenv("GCS_BUCKET", "360-field-check-media-sgb")
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET)
        bucket.exists()
        gcs_connected = True
    except Exception as e:
        import logging
        logger = logging.getLogger("insta360.health")
        logger.warning(f"GCS connection failed: {str(e)}")
        gcs_connected = False
        
    jm = JobManager()
    active_jobs = sum(1 for j in jm.list_jobs(limit=100) if j.get("status") in ["queued", "running"])
    
    return {
        "status": "ok",
        "version": "1.0.0",
        "ffmpeg_available": codec_info["codec"] is not None,
        "available_codec": codec_info["codec"],
        "encode_method": codec_info["method"],
        "codec_reason": codec_info["reason"],
        "gcs_connected": gcs_connected,
        "active_jobs": active_jobs,
        "uptime_seconds": time.time() - START_TIME
    }

class ValidateRequest(BaseModel):
    source_dir: str

@router.post("/ingest/validate")
def validate_ingest(request: ValidateRequest):
    detector = CameraDetector()
    insv_files = detector.list_insv_files(request.source_dir)
    
    if not insv_files:
        return {
            "valid": False,
            "files_found": 0,
            "files_valid": 0,
            "files_invalid": 0,
            "details": []
        }
        
    validator = FileValidator()
    val_res = validator.validate_batch(insv_files)
    
    details = []
    for r in val_res["results"]:
        details.append({
            "file": r["filepath"],
            "valid": r["valid"],
            "reason": ", ".join(r["errors"]) if not r["valid"] else "ok"
        })
        
    return {
        "valid": val_res["invalid"] == 0,
        "files_found": len(insv_files),
        "files_valid": val_res["valid"],
        "files_invalid": val_res["invalid"],
        "details": details
    }

@router.get("/pipeline/schema")
def get_schema():
    return {
      "filepath": "str",
      "sidecar_path": "str",
      "extraction_status": "success | partial | failed",
      "metadata": {
        "camera": {
          "make": "str | null",
          "model": "str | null",
          "firmware": "str | null",
          "serial": "str | null"
        },
        "capture": {
          "timestamp_utc": "str | null",
          "duration_seconds": "float | null",
          "timezone": "str | null"
        },
        "video": {
          "width": "int | null",
          "height": "int | null",
          "frame_rate": "float | null",
          "bitrate_bps": "int | null",
          "codec": "str | null",
          "projection": "str | null"
        },
        "gps": {
          "available": "bool",
          "latitude": "float | null",
          "longitude": "float | null",
          "altitude_m": "float | null",
          "track_points": "int | null"
        },
        "imu": {
          "available": "bool",
          "source": "sdk | exiftool | none",
          "gyroscope": "null",
          "accelerometer": "null"
        },
        "file": {
          "filename": "str",
          "size_bytes": "int",
          "format": ".insv"
        }
      },
      "stitch": {
        "status": "success | failed",
        "engine": "ffmpeg",
        "codec": "str",
        "encode_method": "nvenc | software",
        "stitch_duration_seconds": "float",
        "output_path": "str"
      },
      "upload": {
        "status": "success | failed",
        "mp4_gcs_uri": "str | null",
        "sidecar_gcs_uri": "str | null",
        "upload_duration_seconds": "float",
        "uploaded_at_utc": "str"
      },
      "warnings": "list",
      "errors": "list"
    }
