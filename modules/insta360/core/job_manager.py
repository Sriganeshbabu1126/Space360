import os
import json
import uuid
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("insta360.job_manager")

class JobManager:
    def __init__(self):
        self.jobs_dir = os.getenv("JOBS_DIR", r"F:\Space360\modules\insta360\logs\jobs")
        os.makedirs(self.jobs_dir, exist_ok=True)
        self._jobs = {}
        self._load_jobs()

    def _load_jobs(self):
        if not os.path.exists(self.jobs_dir):
            return
        for filename in os.listdir(self.jobs_dir):
            if filename.endswith(".json"):
                job_id = filename[:-5]
                filepath = os.path.join(self.jobs_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        self._jobs[job_id] = json.load(f)
                except Exception as e:
                    logger.error(f"Failed to load job {job_id}: {e}")

    def _save_job(self, job_id: str):
        filepath = os.path.join(self.jobs_dir, f"{job_id}.json")
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self._jobs[job_id], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save job {job_id}: {e}")

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
        self._jobs[job_id] = job
        self._save_job(job_id)
        return job_id

    def update(self, job_id: str, step: str, status: str, result: dict) -> None:
        if job_id not in self._jobs:
            return
        job = self._jobs[job_id]
        now = datetime.now(timezone.utc).isoformat()
        job["updated_at_utc"] = now
        
        if step in job["steps"]:
            job["steps"][step]["status"] = status
            job["steps"][step]["result"] = result
            if status == "running":
                job["current_step"] = step
                job["status"] = "running"
        self._save_job(job_id)

    def complete(self, job_id: str, summary: dict) -> None:
        if job_id not in self._jobs:
            return
        job = self._jobs[job_id]
        now = datetime.now(timezone.utc).isoformat()
        job["updated_at_utc"] = now
        job["status"] = "complete"
        job["current_step"] = None
        job["summary"] = summary
        self._save_job(job_id)

    def fail(self, job_id: str, step: str, error: str) -> None:
        if job_id not in self._jobs:
            return
        job = self._jobs[job_id]
        now = datetime.now(timezone.utc).isoformat()
        job["updated_at_utc"] = now
        job["status"] = "failed"
        job["current_step"] = None
        job["error"] = error
        if step and step in job["steps"]:
            job["steps"][step]["status"] = "failed"
            if not job["steps"][step]["result"]:
                job["steps"][step]["result"] = {"error": error}
        self._save_job(job_id)

    def get(self, job_id: str) -> dict:
        return self._jobs.get(job_id)

    def list_jobs(self, limit: int = 20) -> list:
        jobs_list = list(self._jobs.values())
        jobs_list.sort(key=lambda x: x["created_at_utc"], reverse=True)
        result = []
        for j in jobs_list[:limit]:
            result.append({
                "job_id": j["job_id"],
                "status": j["status"],
                "created_at_utc": j["created_at_utc"],
                "summary": j["summary"]
            })
        return result

    def delete(self, job_id: str) -> bool:
        if job_id in self._jobs:
            del self._jobs[job_id]
            filepath = os.path.join(self.jobs_dir, f"{job_id}.json")
            if os.path.exists(filepath):
                os.remove(filepath)
            return True
        return False
