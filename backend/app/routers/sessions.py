from fastapi import (APIRouter, Depends, HTTPException, 
                     UploadFile, File, Query, Form)
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models import CaptureSession, LocationPoint
from app.schemas import CaptureSessionResponse
from app.services.gcs_service import upload_private_file, get_signed_url
import uuid
import io
from PIL import Image

router = APIRouter()

@router.get("/", response_model=List[CaptureSessionResponse])
def get_all_sessions(
    db: Session = Depends(get_db),
    site_id: Optional[str] = Query(None, description="Filter captures by site ID"),
    limit: int = Query(50, le=100),
    offset: int = Query(0)
):
    query = db.query(CaptureSession)
    if site_id:
        query = query.join(LocationPoint).join(LocationPoint.floor_plan).filter(
            LocationPoint.floor_plan.has(site_id=site_id)
        )
    return (query.order_by(CaptureSession.captured_at.desc())
              .offset(offset).limit(limit).all())

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
        raise HTTPException(status_code=404, 
                            detail="Location not found")

    # Get site_id by traversing the relationship
    site_id = loc.floor_plan.site_id
    session_id = str(uuid.uuid4())
    file_bytes = await file.read()

    # Define paths
    image_path = f"sites/{site_id}/locations/{location_id}/sessions/{session_id}/image.jpg"
    thumb_path = f"sites/{site_id}/locations/{location_id}/sessions/{session_id}/thumbnail.jpg"

    # Upload full image
    upload_private_file(file_bytes, image_path, "image/jpeg")

    # Generate and upload thumbnail
    img = Image.open(io.BytesIO(file_bytes))
    img.thumbnail((800, 400))
    thumb_bytes = io.BytesIO()
    img.save(thumb_bytes, format="JPEG", quality=75)
    upload_private_file(thumb_bytes.getvalue(), thumb_path, "image/jpeg")

    # Generate signed URLs
    image_url = get_signed_url(image_path)
    thumbnail_url = get_signed_url(thumb_path)

    session = CaptureSession(
        id=session_id,
        location_point_id=location_id,
        image_url=image_url,
        thumbnail_url=thumbnail_url,
        captured_by="system",  # replaced by auth later
        device_model=device_model,
        gps_lat=gps_lat,
        gps_lng=gps_lng,
        captured_at=captured_at if captured_at else datetime.utcnow(),
    )
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
def delete_session(session_id: str, db: Session = Depends(get_db)):
    s = db.query(CaptureSession).filter(
        CaptureSession.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(s)
    db.commit()
