from fastapi import (APIRouter, Depends, HTTPException, 
                     UploadFile, File, Query, Form, BackgroundTasks)
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models import CaptureSession, LocationPoint, CaptureFrame, AIStatusEnum
from app.schemas import CaptureSessionResponse, CaptureFrameResponse
from app.services.gcs_service import upload_private_file, get_signed_url
from app.utils.video_processor import extract_frames_from_video
import uuid
import io
from PIL import Image

router = APIRouter()

import os
import httpx

@router.get("/", response_model=List[CaptureSessionResponse])
async def get_all_sessions(
    db: Session = Depends(get_db),
    site_id: Optional[str] = Query(None, description="Filter captures by site ID"),
    limit: int = Query(50, le=100),
    offset: int = Query(0)
):
    query = db.query(CaptureSession)
    if site_id:
        from app.models import FloorPlan
        query = query.join(LocationPoint).join(FloorPlan).filter(
            FloorPlan.site_id == site_id
        )
    sessions = query.order_by(CaptureSession.captured_at.desc()).offset(offset).limit(limit).all()
    
    video_jobs = []
    try:
        MODULE_URL = os.getenv("INSTA360_MODULE_URL", "https://insta360-module-1046334946412.asia-southeast1.run.app")
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{MODULE_URL}/jobs", timeout=3.0)
            if resp.status_code == 200:
                jobs = resp.json()
                for job in jobs:
                    if site_id:
                        job_site_id = job.get("site_id")
                        if not job_site_id or job_site_id != site_id:
                            continue
                        
                    created_dt = datetime.utcnow()
                    if job.get("created_at_utc"):
                        try:
                            time_str = job["created_at_utc"].replace("Z", "+00:00")
                            created_dt = datetime.fromisoformat(time_str).replace(tzinfo=None)
                        except:
                            pass
                    
                    status_val = job.get("status", "pending")
                    if status_val in ["queued", "processing"]:
                        status_val = "pending"
                        
                    summary = job.get("summary") or {}
                    gcs_uris = summary.get("gcs_uris", [])
                    
                    frames = []
                    for i, uri in enumerate(gcs_uris):
                        http_url = uri
                        if uri.startswith("gs://"):
                            import urllib.parse
                            parsed = urllib.parse.urlparse(uri)
                            blob_path = parsed.path.lstrip('/')
                            try:
                                http_url = get_signed_url(blob_path)
                            except Exception as ex:
                                print(f"Error signing url for {blob_path}: {ex}")
                                http_url = uri.replace(f"gs://{parsed.netloc}/", "https://storage.googleapis.com/")
                            
                        frames.append({
                            "id": f"frame_{i}",
                            "session_id": job["job_id"],
                            "frame_number": i,
                            "frame_url": http_url,
                            "timestamp_seconds": i * 0.5,
                            "created_at": created_dt
                        })
                        
                    first_img = frames[0]["frame_url"] if frames else None
                    is_mp4 = first_img and ".mp4" in first_img.lower()
                        
                    video_jobs.append({
                        "id": job["job_id"],
                        "location_point_id": None,
                        "floor_plan_id": job.get("floor_plan_id"),
                        "location_label": "360° Video Sequence",
                        "captured_at": created_dt,
                        "created_at": created_dt,
                        "image_url": None if is_mp4 else first_img,
                        "thumbnail_url": None if is_mp4 else first_img,
                        "captured_by": "system",
                        "device_model": "Insta360",
                        "gps_lat": None,
                        "gps_lng": None,
                        "ai_status": AIStatusEnum.pending,
                        "ai_summary": None,
                        "ai_changes": None,
                        "video_url": first_img if is_mp4 else None,
                        "fps": 2,
                        "total_frames": len(frames) if frames else None,
                        "processing_status": status_val,
                        "error_message": None,
                        "frames": frames
                    })
    except Exception as e:
        print(f"Failed to fetch video jobs: {e}")

    # Combine and sort
    all_captures = list(sessions) + video_jobs
    
    def get_date(x):
        d = x.get("captured_at") if isinstance(x, dict) else getattr(x, "captured_at", None)
        return d if d is not None else datetime.min

    all_captures.sort(key=get_date, reverse=True)
    return all_captures

@router.get("/location/{location_id}",
            response_model=List[CaptureSessionResponse])
def list_sessions(
    location_id: str,
    db: Session = Depends(get_db),
    limit: int = Query(50, le=100),
    offset: int = Query(0)
):
    loc = db.query(LocationPoint).filter(
        LocationPoint.id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, 
                            detail="Location not found")
    return (db.query(CaptureSession)
              .filter(CaptureSession.location_point_id == location_id)
              .order_by(CaptureSession.captured_at.desc())
              .offset(offset).limit(limit).all())

@router.post("/location/{location_id}",
             response_model=CaptureSessionResponse, status_code=201)
async def create_session(
    location_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    device_model: Optional[str] = Form(None),
    gps_lat: Optional[float] = Form(None),
    gps_lng: Optional[float] = Form(None),
    captured_at: Optional[datetime] = Form(None),
    db: Session = Depends(get_db)
):
    loc = db.query(LocationPoint).filter(
        LocationPoint.id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")

    site_id = loc.floor_plan.site_id
    session_id = str(uuid.uuid4())
    file_bytes = await file.read()

    is_video = file.content_type and file.content_type.startswith("video/")

    session = CaptureSession(
        id=session_id,
        location_point_id=location_id,
        captured_by="system",  # replaced by auth later
        device_model=device_model,
        gps_lat=gps_lat,
        gps_lng=gps_lng,
        captured_at=captured_at if captured_at else datetime.utcnow(),
    )

    if is_video:
        video_path = f"sites/{site_id}/locations/{location_id}/sessions/{session_id}/video.mp4"
        upload_private_file(file_bytes, video_path, file.content_type)
        session.video_url = get_signed_url(video_path)
        session.processing_status = "pending"
        db.add(session)
        db.commit()
        db.refresh(session)
        
        background_tasks.add_task(
            extract_frames_from_video,
            video_bytes=file_bytes,
            session_id=session_id,
            site_id=site_id,
            location_id=location_id,
            db=Session(bind=db.get_bind()),
            fps=2
        )
    else:
        # Upload full image
        image_path = f"sites/{site_id}/locations/{location_id}/sessions/{session_id}/image.jpg"
        thumb_path = f"sites/{site_id}/locations/{location_id}/sessions/{session_id}/thumbnail.jpg"
        
        upload_private_file(file_bytes, image_path, "image/jpeg")
        
        img = Image.open(io.BytesIO(file_bytes))
        img.thumbnail((800, 400))
        thumb_bytes = io.BytesIO()
        img.save(thumb_bytes, format="JPEG", quality=75)
        upload_private_file(thumb_bytes.getvalue(), thumb_path, "image/jpeg")
        
        session.image_url = get_signed_url(image_path)
        session.thumbnail_url = get_signed_url(thumb_path)
        session.processing_status = "complete"
        db.add(session)
        db.commit()
        db.refresh(session)

    return session

@router.get("/compare", response_model=List[CaptureSessionResponse])
def compare_sessions(
    session_a: str = Query(..., description="First session ID"),
    session_b: str = Query(..., description="Second session ID"),
    db: Session = Depends(get_db)
):
    """Return two capture sessions side by side for comparison."""
    results = []
    for sid in [session_a, session_b]:
        s = db.query(CaptureSession).filter(
            CaptureSession.id == sid).first()
        if not s:
            raise HTTPException(
                status_code=404, 
                detail=f"Session {sid} not found"
            )
        results.append(s)
    return results

@router.get("/{session_id}", 
            response_model=CaptureSessionResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    s = db.query(CaptureSession).filter(
        CaptureSession.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, 
                            detail="Session not found")
    return s

@router.delete("/{session_id}", status_code=204)
async def delete_session(session_id: str, db: Session = Depends(get_db)):
    s = db.query(CaptureSession).filter(
        CaptureSession.id == session_id).first()
    if not s:
        # Try deleting from Cloud Run
        MODULE_URL = os.getenv("INSTA360_MODULE_URL", "https://insta360-module-1046334946412.asia-southeast1.run.app")
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.delete(f"{MODULE_URL}/jobs/{session_id}", timeout=3.0)
                if resp.status_code in [200, 204]:
                    return
        except Exception:
            pass
        raise HTTPException(status_code=404, detail="Session not found")
        
    db.delete(s)
    db.commit()
