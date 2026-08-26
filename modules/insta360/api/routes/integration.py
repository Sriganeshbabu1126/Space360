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
    ffmpeg_available = shutil.which("ffmpeg") is not None
    gcs_connected = False
    try:
        from core.uploader import GCSUploader
        uploader = GCSUploader()
        if uploader.bucket:
            gcs_connected = True
    except Exception:
        pass
        
    jm = JobManager()
    active_jobs = sum(1 for j in jm._jobs.values() if j["status"] in ["queued", "running"])
    
    return {
        "status": "ok",
        "version": os.getenv("MODULE_VERSION", "1.0.0"),
        "ffmpeg_available": ffmpeg_available,
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
