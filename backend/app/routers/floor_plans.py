from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import FloorPlan, Site
from app.schemas import FloorPlanCreate, FloorPlanResponse
from app.services.gcs_service import upload_floor_plan
import uuid

router = APIRouter()

@router.get("/", response_model=List[FloorPlanResponse])
def get_all_floor_plans(db: Session = Depends(get_db)):
    return db.query(FloorPlan).all()

@router.get("/site/{site_id}", response_model=List[FloorPlanResponse])
def list_floor_plans(site_id: str, db: Session = Depends(get_db)):
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return db.query(FloorPlan).filter(
        FloorPlan.site_id == site_id).all()

@router.post("/site/{site_id}", response_model=FloorPlanResponse,
             status_code=201)
async def create_floor_plan(
    site_id: str,
    label: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    floor_plan_id = str(uuid.uuid4())
    file_bytes = await file.read()
    content_type = file.content_type or "image/png"

    try:
        image_url = upload_floor_plan(
            file_bytes, site_id, floor_plan_id, content_type
        )
    except Exception as e:
        print("GCS Upload Failed:", e)
        import os
        os.makedirs("static/floor-plans", exist_ok=True)
        extension = ".png"
        if "jpeg" in content_type.lower() or "jpg" in content_type.lower():
            extension = ".jpg"
        elif "pdf" in content_type.lower():
            extension = ".pdf"
        local_filename = f"{floor_plan_id}{extension}"
        local_path = os.path.join("static", "floor-plans", local_filename)
        with open(local_path, "wb") as f:
            f.write(file_bytes)
        image_url = f"http://localhost:8000/static/floor-plans/{local_filename}"

    floor_plan = FloorPlan(
        id=floor_plan_id,
        site_id=site_id,
        label=label,
        image_url=image_url,
    )
    db.add(floor_plan)
    db.commit()
    db.refresh(floor_plan)
    return floor_plan

@router.get("/{floor_plan_id}", response_model=FloorPlanResponse)
def get_floor_plan(floor_plan_id: str, 
                   db: Session = Depends(get_db)):
    fp = db.query(FloorPlan).filter(
        FloorPlan.id == floor_plan_id).first()
    if not fp:
        raise HTTPException(status_code=404, 
                            detail="Floor plan not found")
    return fp

@router.delete("/{floor_plan_id}", status_code=204)
def delete_floor_plan(floor_plan_id: str, 
                      db: Session = Depends(get_db)):
    fp = db.query(FloorPlan).filter(
        FloorPlan.id == floor_plan_id).first()
    if not fp:
        raise HTTPException(status_code=404, 
                            detail="Floor plan not found")
    db.delete(fp)
    db.commit()
