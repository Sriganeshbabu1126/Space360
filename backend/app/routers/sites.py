from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Site
from app.schemas import SiteCreate, SiteUpdate, SiteResponse
from app.auth import require_admin
import uuid

router = APIRouter()

def generate_uuid():
    return str(uuid.uuid4())

@router.get("/", response_model=List[SiteResponse])
def list_sites(db: Session = Depends(get_db)):
    return db.query(Site).all()

@router.post("/", response_model=SiteResponse, 
             status_code=status.HTTP_201_CREATED)
def create_site(payload: SiteCreate, db: Session = Depends(get_db),
                current_user: dict = Depends(require_admin)):
    site = Site(
        id=generate_uuid(),
        name=payload.name,
        address=payload.address,
        gps_bounds=payload.gps_bounds,
        org_id=payload.org_id,
        created_by=current_user.get("email", "system"),
    )
    db.add(site)
    db.commit()
    db.refresh(site)
    return site

@router.get("/{site_id}", response_model=SiteResponse)
def get_site(site_id: str, db: Session = Depends(get_db)):
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site

@router.patch("/{site_id}", response_model=SiteResponse)
def update_site(site_id: str, payload: SiteUpdate, 
                db: Session = Depends(get_db)):
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(site, field, value)
    db.commit()
    db.refresh(site)
    return site

@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_site(site_id: str, db: Session = Depends(get_db)):
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    db.delete(site)
    db.commit()
