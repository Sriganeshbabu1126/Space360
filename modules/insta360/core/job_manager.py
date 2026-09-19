import os
import uuid
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv
from google.cloud import firestore

load_dotenv()

logger = logging.getLogger("insta360.job_manager")

class JobManager:
    def __init__(self):
        # Initialize Firestore client with the specified GCP project
        self.db = firestore.Client(project="space360-114433")
        self.collection_name = "jobs"

    def _get_doc_ref(self, job_id: str):
        return self.db.collection(self.collection_name).document(job_id)

    def create(self, source_dir: str) -> str:
        job_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        job = {
            "job_id": job_id,
            "status": "queued",
            "source_dir": source_dir,
            "created_at_utc": now,
            "updated_at_utc": now,
            "current_step": None,
            "steps": {
                "detect":   { "status": "pending", "result": None },
                "validate": { "status": "pending", "result": None },
                "transfer": { "status": "pending", "result": None },
                "extract":  { "status": "pending", "result": None },
                "stitch":   { "status": "pending", "result": None },
                "upload":   { "status": "pending", "result": None }
            },
            "files": [],
            "summary": None,
            "error": None
        }
        try:
            self._get_doc_ref(job_id).set(job)
        except Exception as e:
            logger.error(f"Firestore create failed for job {job_id}: {e}")
        return job_id

    def update(self, job_id: str, step: str, status: str, result: dict) -> None:
        doc_ref = self._get_doc_ref(job_id)
        try:
            doc = doc_ref.get()
            if not doc.exists:
                logger.warning(f"Attempted to update non-existent job {job_id}")
                return
            
            job = doc.to_dict()
            now = datetime.now(timezone.utc).isoformat()
            job["updated_at_utc"] = now
            
            if step in job["steps"]:
                job["steps"][step]["status"] = status
                job["steps"][step]["result"] = result
                if status == "running":
                    job["current_step"] = step
                    job["status"] = "running"
                    
            doc_ref.set(job)
        except Exception as e:
            logger.error(f"Firestore update failed for job {job_id}: {e}")

    def complete(self, job_id: str, summary: dict) -> None:
        doc_ref = self._get_doc_ref(job_id)
        try:
            doc = doc_ref.get()
            if not doc.exists:
                return
            
            job = doc.to_dict()
            now = datetime.now(timezone.utc).isoformat()
            job["updated_at_utc"] = now
            job["status"] = "complete"
            job["current_step"] = None
            job["summary"] = summary
            
            doc_ref.set(job)
        except Exception as e:
            logger.error(f"Firestore complete failed for job {job_id}: {e}")

    def fail(self, job_id: str, step: str, error: str) -> None:
        doc_ref = self._get_doc_ref(job_id)
        try:
            doc = doc_ref.get()
            if not doc.exists:
                return
            
            job = doc.to_dict()
            now = datetime.now(timezone.utc).isoformat()
            job["updated_at_utc"] = now
            job["status"] = "failed"
            job["current_step"] = None
            job["error"] = error
            
            if step and step in job["steps"]:
                job["steps"][step]["status"] = "failed"
                if not job["steps"][step]["result"]:
                    job["steps"][step]["result"] = {"error": error}
                    
            doc_ref.set(job)
        except Exception as e:
            logger.error(f"Firestore fail failed for job {job_id}: {e}")

    def get(self, job_id: str) -> dict:
        doc_ref = self._get_doc_ref(job_id)
        try:
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
        except Exception as e:
            logger.error(f"Firestore get failed for job {job_id}: {e}")
        return None

    def list_jobs(self, limit: int = 20) -> list:
        try:
            query = self.db.collection(self.collection_name).order_by(
                "created_at_utc", direction=firestore.Query.DESCENDING
            ).limit(limit)
            
            docs = query.stream()
            result = []
            for doc in docs:
                j = doc.to_dict()
                result.append({
                    "job_id": j.get("job_id"),
                    "status": j.get("status"),
                    "created_at_utc": j.get("created_at_utc"),
                    "summary": j.get("summary")
                })
            return result
        except Exception as e:
            logger.error(f"Firestore list_jobs failed: {e}")
            return []

    def delete(self, job_id: str) -> bool:
        doc_ref = self._get_doc_ref(job_id)
        try:
            doc = doc_ref.get()
            if doc.exists:
                doc_ref.delete()
                return True
        except Exception as e:
            logger.error(f"Firestore delete failed for job {job_id}: {e}")
        return False
