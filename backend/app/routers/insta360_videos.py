import tempfile, shutil, os
import httpx
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

router = APIRouter(prefix="/videos", tags=["insta360"])
MODULE_URL = os.getenv("INSTA360_MODULE_URL", "https://insta360-module-1046334946412.asia-southeast1.run.app")

from google.cloud import storage as gcs
import uuid

def upload_to_gcs(file_bytes: bytes, filename: str, site_id: str) -> str:
    client = gcs.Client()
    bucket = client.bucket("360-field-check-media-sgb")
    # Store in uploads/ folder (separate from processed videos/)
    blob_path = f"uploads/{site_id}/{uuid.uuid4()}/{filename}"
    blob = bucket.blob(blob_path)
    blob.upload_from_string(file_bytes, content_type="video/mp4")
    return f"gs://360-field-check-media-sgb/{blob_path}"

@router.post("/ingest")
async def ingest_video(
    site_id: str = Form(...),
    pin_id: str = Form(None),
    file: UploadFile = File(...)
):
    # Step 1: Read file bytes
    file_bytes = await file.read()
    
    # Step 2: Upload to GCS
    try:
        gcs_uri = upload_to_gcs(file_bytes, file.filename, site_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload to GCS: {str(e)}")
        
    # Step 3: Trigger Cloud Run module
    MODULE_URL = os.getenv("MODULE_URL", "https://insta360-module-1046334946412.asia-southeast1.run.app")
    async with httpx.AsyncClient(timeout=60) as client:
        payload = {"gcs_uri": gcs_uri, "pin_id": pin_id}
        response = await client.post(
            f"{MODULE_URL}/ingest",
            json=payload
        )
        if response.status_code not in [200, 202]:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )
        return response.json()

@router.get("/{job_id}/status")
async def get_job_status(job_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{MODULE_URL}/ingest-status/{job_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

@router.get("/")
async def list_videos():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{MODULE_URL}/jobs")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()
