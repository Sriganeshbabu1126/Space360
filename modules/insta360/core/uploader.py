"""
Responsible for GCS upload to space360-insta360-output/insta360/
"""
import os
import time
import json
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("insta360.uploader")

try:
    from google.cloud import storage
    from google.oauth2 import service_account
except ImportError:
    storage = None
    service_account = None

class GCSUploader:
    def __init__(self):
        self.key_path = os.getenv("GCS_KEY_PATH")
        self.bucket_name = os.getenv("GCS_BUCKET_NAME")
        self.project_id = os.getenv("GCS_PROJECT_ID")
        self.client = None
        self.bucket = None
        
        if storage is None:
            logger.warning("google-cloud-storage not installed")
            return

        try:
            if self.key_path and os.path.exists(self.key_path):
                credentials = service_account.Credentials.from_service_account_file(self.key_path)
                self.client = storage.Client(credentials=credentials, project=self.project_id)
            else:
                self.client = storage.Client(project=self.project_id)
                
            if self.bucket_name:
                self.bucket = self.client.bucket(self.bucket_name)
                # Validation check
                if not self.bucket.exists():
                    logger.warning(f"Bucket {self.bucket_name} does not exist or is unreachable")
        except Exception as e:
            logger.warning(f"Failed to initialize GCS client: {e}")

    def _get_gcs_path(self, date_str: str, filename: str) -> str:
        return f"insta360/{date_str}/{filename}"

    def upload(self, local_path: str, date_str: str) -> dict:
        filename = os.path.basename(local_path)
        gcs_path = self._get_gcs_path(date_str, filename)
        gcs_uri = f"gs://{self.bucket_name}/{gcs_path}"
        
        result = {
            "local_path": local_path,
            "gcs_path": gcs_path,
            "gcs_uri": gcs_uri,
            "success": False,
            "size_bytes": None,
            "upload_duration_seconds": None,
            "error": None
        }

        if not os.path.exists(local_path):
            result["error"] = "Local file does not exist"
            return result

        result["size_bytes"] = os.path.getsize(local_path)
        
        if self.bucket is None:
            result["error"] = "GCS client not initialized"
            return result

        try:
            blob = self.bucket.blob(gcs_path)
            blob.chunk_size = 8 * 1024 * 1024
            
            if blob.exists():
                logger.warning(f"File {gcs_path} already exists in GCS, skipping.")
                result["success"] = True
                result["upload_duration_seconds"] = 0.0
                return result
                
            logger.info(f"Starting upload for {local_path} ({result['size_bytes']} bytes)")
            start_time = time.time()
            blob.upload_from_filename(local_path, timeout=3600)
            duration = time.time() - start_time
            
            result["success"] = True
            result["upload_duration_seconds"] = duration
            logger.info(f"Upload complete for {local_path} in {duration:.2f}s")
            
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Failed to upload {local_path}: {e}")
            
        return result

    def upload_pair(self, mp4_path: str, sidecar_path: str, date_str: str) -> dict:
        result = {
            "mp4": None,
            "sidecar": None,
            "pair_success": False,
            "date_str": date_str
        }
        
        logger.info(f"Uploading pair: {mp4_path} and {sidecar_path}")
        mp4_res = self.upload(mp4_path, date_str)
        result["mp4"] = mp4_res
        
        if not mp4_res["success"]:
            logger.warning(f"MP4 upload failed, aborting sidecar upload for {sidecar_path}")
            result["sidecar"] = {
                "local_path": sidecar_path,
                "gcs_path": self._get_gcs_path(date_str, os.path.basename(sidecar_path)),
                "gcs_uri": f"gs://{self.bucket_name}/{self._get_gcs_path(date_str, os.path.basename(sidecar_path))}",
                "success": False,
                "size_bytes": os.path.getsize(sidecar_path) if os.path.exists(sidecar_path) else None,
                "upload_duration_seconds": None,
                "error": "Aborted due to MP4 upload failure"
            }
            return result
            
        sidecar_res = self.upload(sidecar_path, date_str)
        result["sidecar"] = sidecar_res
        
        if mp4_res["success"] and sidecar_res["success"]:
            result["pair_success"] = True
            
        return result

    def upload_batch(self, pairs: list[dict], date_str: str) -> list[dict]:
        results = []
        for pair in pairs:
            res = self.upload_pair(pair["mp4"], pair["sidecar"], date_str)
            results.append(res)
        return results

    def _update_sidecar(self, sidecar_path: str, upload_result: dict) -> None:
        try:
            with open(sidecar_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            data["upload"] = {
                "status": "success" if upload_result["pair_success"] else "failed",
                "mp4_gcs_uri": upload_result["mp4"]["gcs_uri"] if upload_result["mp4"] else None,
                "sidecar_gcs_uri": upload_result["sidecar"]["gcs_uri"] if upload_result["sidecar"] else None,
                "upload_duration_seconds": (upload_result["mp4"].get("upload_duration_seconds", 0) or 0) + (upload_result["sidecar"].get("upload_duration_seconds", 0) or 0),
                "uploaded_at_utc": datetime.now(timezone.utc).isoformat()
            }
            
            with open(sidecar_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to update sidecar {sidecar_path}: {e}")
