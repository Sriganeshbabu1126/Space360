import os
import httpx
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

router = APIRouter(prefix="/videos", tags=["insta360"])
MODULE_URL = os.getenv("INSTA360_MODULE_URL", "https://insta360-module-1046334946412.asia-southeast1.run.app")

@router.post("/ingest")
async def ingest_video(site_id: str = Form(...), file: UploadFile = File(...)):
    async with httpx.AsyncClient() as client:
        # Proxy to Cloud Run module which expects a source_dir
        payload = {"source_dir": "/"}
        response = await client.post(f"{MODULE_URL}/ingest", json=payload)
        if response.status_code != 202:
            raise HTTPException(status_code=response.status_code, detail=response.text)
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
