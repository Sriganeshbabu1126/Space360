from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid
from pydantic import BaseModel

from app.database import get_db
from app.auth import get_current_user
from app.models import InspectionPath, InspectionPathPoint

router = APIRouter(prefix="/paths", tags=["paths"])

def generate_uuid():
    return str(uuid.uuid4())

class PointBase(BaseModel):
    sequence_order: int
    x_percent: float
    y_percent: float
    label: Optional[str] = None
    capture_id: Optional[str] = None
    video_job_id: Optional[str] = None
    timestamp_seconds: Optional[float] = None

class PointCreate(PointBase):
    pass

class PointResponse(PointBase):
    id: str
    path_id: str
    created_at: datetime

    class Config:
        orm_mode = True

class PathBase(BaseModel):
    name: str
    site_id: str
    floor_plan_id: str

class PathCreate(PathBase):
    points: Optional[List[PointCreate]] = []

class PathResponse(PathBase):
    id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    points: List[PointResponse] = []

    class Config:
        orm_mode = True

@router.post("/", response_model=PathResponse, status_code=status.HTTP_201_CREATED)
def create_path(
    payload: PathCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    path_id = generate_uuid()
    new_path = InspectionPath(
        id=path_id,
        name=payload.name,
        site_id=payload.site_id,
        floor_plan_id=payload.floor_plan_id,
        created_by=current_user.get("uid", "test_user")
    )
    db.add(new_path)
    
    for pt in payload.points:
        new_pt = InspectionPathPoint(
            id=generate_uuid(),
            path_id=path_id,
            sequence_order=pt.sequence_order,
            x_percent=pt.x_percent,
            y_percent=pt.y_percent,
            label=pt.label,
            capture_id=pt.capture_id,
            video_job_id=pt.video_job_id,
            timestamp_seconds=pt.timestamp_seconds
        )
        db.add(new_pt)
        
    db.commit()
    db.refresh(new_path)
    return new_path

@router.get("/", response_model=List[PathResponse])
def get_paths(
    floor_plan_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(InspectionPath)
    if floor_plan_id:
        query = query.filter(InspectionPath.floor_plan_id == floor_plan_id)
    return query.all()

@router.get("/{path_id}", response_model=PathResponse)
def get_path(
    path_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    path = db.query(InspectionPath).filter(InspectionPath.id == path_id).first()
    if not path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Path not found")
    return path

@router.post("/{path_id}/points", response_model=PointResponse, status_code=status.HTTP_201_CREATED)
def add_point_to_path(
    path_id: str,
    payload: PointCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    path = db.query(InspectionPath).filter(InspectionPath.id == path_id).first()
    if not path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Path not found")
        
    new_pt = InspectionPathPoint(
        id=generate_uuid(),
        path_id=path_id,
        sequence_order=payload.sequence_order,
        x_percent=payload.x_percent,
        y_percent=payload.y_percent,
        label=payload.label,
        capture_id=payload.capture_id,
        video_job_id=payload.video_job_id,
        timestamp_seconds=payload.timestamp_seconds
    )
    db.add(new_pt)
    db.commit()
    db.refresh(new_pt)
    return new_pt

@router.put("/{path_id}/points/{point_id}", response_model=PointResponse)
def update_point(
    path_id: str,
    point_id: str,
    payload: PointCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    pt = db.query(InspectionPathPoint).filter(
        InspectionPathPoint.id == point_id,
        InspectionPathPoint.path_id == path_id
    ).first()
    if not pt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Point not found")
        
    pt.sequence_order = payload.sequence_order
    pt.x_percent = payload.x_percent
    pt.y_percent = payload.y_percent
    pt.label = payload.label
    pt.capture_id = payload.capture_id
    pt.video_job_id = payload.video_job_id
    pt.timestamp_seconds = payload.timestamp_seconds
    
    db.commit()
    db.refresh(pt)
    return pt

@router.delete("/{path_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_path(
    path_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    path = db.query(InspectionPath).filter(InspectionPath.id == path_id).first()
    if not path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Path not found")
    
    db.query(InspectionPathPoint).filter(InspectionPathPoint.path_id == path_id).delete()
    db.delete(path)
    db.commit()
    return None
