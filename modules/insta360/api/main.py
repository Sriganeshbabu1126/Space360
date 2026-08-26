from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from api.routes import integration
from core.job_manager import JobManager
from core.pipeline_runner import PipelineRunner
from core.camera import CameraDetector
from core.metadata import MetadataExtractor
from core.stitcher import VideoStitcher
from core.uploader import GCSUploader
import os
import shutil
import logging

logger = logging.getLogger("insta360.api")

app = FastAPI(title="Insta360 X4 Video Handling Module")
job_manager = JobManager()
pipeline_runner = PipelineRunner(job_manager)

@app.on_event("startup")
def startup_event():
    if not shutil.which("ffmpeg"):
        logger.warning("ffmpeg is not found on PATH. Stitching will fail.")

app.include_router(integration.router)

class IngestAsyncRequest(BaseModel):
    source_dir: str

@app.post("/ingest", status_code=202)
def ingest_async(request: IngestAsyncRequest):
    if not os.path.exists(request.source_dir):
        raise HTTPException(status_code=404, detail="source_dir does not exist")
        
    job_id = job_manager.create(request.source_dir)
    pipeline_runner.run(job_id, request.source_dir)
    
    return {
        "job_id": job_id,
        "status": "queued",
        "status_url": f"/ingest-status/{job_id}"
    }

@app.get("/ingest-status/{job_id}")
def get_ingest_status(job_id: str):
    job = job_manager.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/ingest-status/{job_id}/summary")
def get_ingest_summary(job_id: str):
    job = job_manager.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if job["status"] in ["queued", "running"]:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=202,
            content={"status": job["status"], "current_step": job["current_step"]}
        )
        
    return job["summary"]

@app.get("/jobs")
def list_jobs(limit: int = Query(20)):
    return job_manager.list_jobs(limit)

@app.delete("/jobs/{job_id}")
def delete_job(job_id: str):
    success = job_manager.delete(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"status": "deleted"}

@app.get("/metadata")
def get_metadata(filepath: str):
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File does not exist")
    if not filepath.lower().endswith(".insv"):
        raise HTTPException(status_code=422, detail="File must be a .insv file")
        
    extractor = MetadataExtractor()
    return extractor.extract(filepath)

class StitchRequest(BaseModel):
    filepath: str
    out_dir: str

@app.post("/stitch")
def stitch_video(request: StitchRequest):
    if not os.path.exists(request.filepath):
        raise HTTPException(status_code=404, detail="File does not exist")
    if not request.filepath.lower().endswith(".insv"):
        raise HTTPException(status_code=422, detail="File must be a .insv file")
        
    stitcher = VideoStitcher()
    return stitcher.stitch(request.filepath, request.out_dir)

class UploadRequest(BaseModel):
    mp4_path: str
    sidecar_path: str
    date_str: str

@app.post("/upload")
def upload_files(request: UploadRequest):
    if not os.path.exists(request.mp4_path) or not os.path.exists(request.sidecar_path):
        raise HTTPException(status_code=404, detail="One or both files do not exist")
    if not request.mp4_path.endswith("_stitched.mp4") or not request.sidecar_path.endswith("_metadata.json"):
        raise HTTPException(status_code=422, detail="Invalid file extensions for upload")
        
    uploader = GCSUploader()
    return uploader.upload_pair(request.mp4_path, request.sidecar_path, request.date_str)

@app.get("/upload-status/{gcs_path:path}")
def check_upload_status(gcs_path: str):
    uploader = GCSUploader()
    if not uploader.bucket:
        raise HTTPException(status_code=500, detail="GCS client not initialized")
        
    blob = uploader.bucket.blob(gcs_path)
    exists = blob.exists()
    return {
        "exists": exists,
        "gcs_uri": f"gs://{uploader.bucket_name}/{gcs_path}",
        "size_bytes": blob.size if exists else None
    }
