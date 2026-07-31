from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import LocationPoint, FloorPlan
from app.schemas import LocationPointCreate, LocationPointResponse
import uuid

router = APIRouter()

@router.get("/floor-plan/{floor_plan_id}",
            response_model=List[LocationPointResponse])
def list_locations(floor_plan_id: str, 
                   db: Session = Depends(get_db)):
    fp = db.query(FloorPlan).filter(
        FloorPlan.id == floor_plan_id).first()
    if not fp:
        raise HTTPException(status_code=404, 
                            detail="Floor plan not found")
    return db.query(LocationPoint).filter(
        LocationPoint.floor_plan_id == floor_plan_id).all()

@router.post("/floor-plan/{floor_plan_id}",
             response_model=LocationPointResponse, status_code=201)
def create_location(floor_plan_id: str, 
                    payload: LocationPointCreate,
                    db: Session = Depends(get_db)):
    fp = db.query(FloorPlan).filter(
        FloorPlan.id == floor_plan_id).first()
    if not fp:
        raise HTTPException(status_code=404, 
                            detail="Floor plan not found")
    location = LocationPoint(
        id=str(uuid.uuid4()),
        floor_plan_id=floor_plan_id,
        **payload.model_dump()
    )
    db.add(location)
    db.commit()
    db.refresh(location)
    return location

@router.get("/{location_id}", 
            response_model=LocationPointResponse)
def get_location(location_id: str, db: Session = Depends(get_db)):
    loc = db.query(LocationPoint).filter(
        LocationPoint.id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, 
                            detail="Location not found")
    return loc

@router.patch("/{location_id}", 
              response_model=LocationPointResponse)
def update_location(location_id: str, 
                    payload: LocationPointCreate,
                    db: Session = Depends(get_db)):
    loc = db.query(LocationPoint).filter(
        LocationPoint.id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, 
                            detail="Location not found")
    for field, value in payload.model_dump(
            exclude_unset=True).items():
        setattr(loc, field, value)
    db.commit()
    db.refresh(loc)
    return loc

@router.delete("/{location_id}", status_code=204)
def delete_location(location_id: str, 
                    db: Session = Depends(get_db)):
    loc = db.query(LocationPoint).filter(
        LocationPoint.id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, 
                            detail="Location not found")
    db.delete(loc)
    db.commit()
