from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Contractor, IssueAssignment
from app.schemas import ContractorCreate, ContractorUpdate, ContractorResponse
from app.auth import get_current_user, require_admin
import uuid

router = APIRouter()

def generate_uuid():
    return str(uuid.uuid4())

@router.post("/", response_model=ContractorResponse, status_code=status.HTTP_201_CREATED)
def create_contractor(
    payload: ContractorCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    contractor = Contractor(
        id=generate_uuid(),
        name=payload.name,
        company=payload.company,
        trade=payload.trade,
        designation=payload.designation,
        contact=payload.contact,
        access_level=payload.access_level,
        created_by=current_user.get("email", "system")
    )
    db.add(contractor)
    db.commit()
    db.refresh(contractor)
    return contractor

@router.get("/", response_model=List[ContractorResponse])
def list_contractors(db: Session = Depends(get_db)):
    return db.query(Contractor).order_by(Contractor.created_at.desc()).all()

@router.get("/{id}", response_model=ContractorResponse)
def get_contractor(id: str, db: Session = Depends(get_db)):
    contractor = db.query(Contractor).filter(Contractor.id == id).first()
    if not contractor:
        raise HTTPException(status_code=404, detail="Contractor not found")
    return contractor

@router.put("/{id}", response_model=ContractorResponse)
def update_contractor(
    id: str,
    payload: ContractorUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    contractor = db.query(Contractor).filter(Contractor.id == id).first()
    if not contractor:
        raise HTTPException(status_code=404, detail="Contractor not found")
    
    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(contractor, key, value)
        
    db.commit()
    db.refresh(contractor)
    return contractor

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contractor(
    id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    contractor = db.query(Contractor).filter(Contractor.id == id).first()
    if not contractor:
        raise HTTPException(status_code=404, detail="Contractor not found")
    
    db.delete(contractor)
    db.commit()
    return
