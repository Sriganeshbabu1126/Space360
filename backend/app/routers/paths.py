from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
from pydantic import BaseModel

from app.database import get_db
from app.auth import get_current_user
from app.models import Path, PathPoint

router = APIRouter(prefix="/paths", tags=["paths"])

def generate_uuid():
    return str(uuid.uuid4())

class WaypointCreate(BaseModel):
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    heading: Optional[float] = None
    accuracy: Optional[float] = None
    timestamp: datetime

class PathCreate(BaseModel):
    site_id: str
    user_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    waypoint_count: int
    waypoints: List[WaypointCreate]

class PathResponse(BaseModel):
    id: str
    site_id: str
    user_id: str
    started_at: datetime
    waypoint_count: int

    class Config:
        orm_mode = True

@router.post("/", response_model=PathResponse, status_code=status.HTTP_201_CREATED)
def create_path(
    payload: PathCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    path_id = generate_uuid()
    new_path = Path(
        id=path_id,
        site_id=payload.site_id,
        user_id=payload.user_id,
        started_at=payload.started_at,
        ended_at=payload.ended_at,
        waypoint_count=payload.waypoint_count
    )
    db.add(new_path)
    
    for wp in payload.waypoints:
        new_wp = PathPoint(
            id=generate_uuid(),
            path_id=path_id,
            latitude=wp.latitude,
            longitude=wp.longitude,
            altitude=wp.altitude,
            heading=wp.heading,
            accuracy=wp.accuracy,
            timestamp=wp.timestamp
        )
        db.add(new_wp)
        
    db.commit()
    db.refresh(new_path)
    return new_path

@router.delete("/cleanup")
def cleanup_old_paths(db: Session = Depends(get_db)):
    # 30-day retention cleanup
    cutoff = datetime.utcnow() - timedelta(days=30)
    old_paths = db.query(Path).filter(Path.created_at < cutoff).all()
    count = len(old_paths)
    for p in old_paths:
        db.query(PathPoint).filter(PathPoint.path_id == p.id).delete()
        db.delete(p)
    db.commit()
    return {"message": f"Deleted {count} old paths"}
