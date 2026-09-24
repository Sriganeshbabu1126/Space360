from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form
from pydantic import BaseModel
import tempfile
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
    ffmpeg_path = os.getenv("FFMPEG_PATH", "ffmpeg")
    if not os.path.exists(ffmpeg_path) and ffmpeg_path != "ffmpeg":
        print(f"WARNING: ffmpeg not found at {ffmpeg_path}")
        logger.warning(f"ffmpeg not found at {ffmpeg_path}. Stitching will fail.")
    else:
        print(f"✅ ffmpeg found at {ffmpeg_path}")
        
    try:
        extractor = MetadataExtractor()
        print("✅ MetadataExtractor initialized successfully")
    except Exception as e:
        print(f"❌ MetadataExtractor failed to initialize: {e}")
        
    exiftool_path = os.getenv("EXIFTOOL_PATH", "exiftool")
    if not os.path.exists(exiftool_path) and exiftool_path != "exiftool":
        print(f"WARNING: exiftool not found at {exiftool_path}")
    else:
        print(f"✅ exiftool found at {exiftool_path}")

app.include_router(integration.router)

class IngestAsyncRequest(BaseModel):
    source_dir: str = None
    gcs_uri: str = None

from fastapi import Request
from google.cloud import storage

@app.post("/ingest", status_code=202)
async def ingest_async(request: Request):
    actual_source_dir = None
    gcs_uri = None
    file = None
    is_temp = False
    
    site_id = None
    try:
        body = await request.json()
        actual_source_dir = body.get("source_dir")
        gcs_uri = body.get("gcs_uri")
        site_id = body.get("site_id")
    except Exception:
        form = await request.form()
        actual_source_dir = form.get("source_dir")
        gcs_uri = form.get("gcs_uri")
        file = form.get("file")
        site_id = form.get("site_id")

    if gcs_uri:
        tmp_dir = tempfile.mkdtemp()
        is_temp = True
        try:
            client = storage.Client()
            uri = gcs_uri.replace("gs://", "")
            bucket_name = uri.split("/")[0]
            blob_path = "/".join(uri.split("/")[1:])
            filename = blob_path.split("/")[-1]
            
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_path)
            # Must place in DCIM folder for CameraDetector.list_insv_files to find it
            dcim_dir = os.path.join(tmp_dir, "DCIM")
            os.makedirs(dcim_dir, exist_ok=True)
            local_path = os.path.join(dcim_dir, filename)
            blob.download_to_filename(local_path)
            
            actual_source_dir = tmp_dir
        except Exception as e:
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)
            raise HTTPException(status_code=400, detail=f"GCS download failed: {e}")
            
    elif file and hasattr(file, "filename"):
        tmp_dir = tempfile.mkdtemp()
        is_temp = True
        dcim_dir = os.path.join(tmp_dir, "DCIM")
        os.makedirs(dcim_dir, exist_ok=True)
        file_path = os.path.join(dcim_dir, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        actual_source_dir = tmp_dir
            
    if not actual_source_dir:
        raise HTTPException(status_code=400, detail="Either gcs_uri, file or source_dir required")
        
    if not os.path.exists(actual_source_dir):
        raise HTTPException(status_code=404, detail="source_dir does not exist")
        
    job_id = job_manager.create(actual_source_dir, site_id)
    pipeline_runner.run(job_id, actual_source_dir, cleanup=is_temp)
    
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
