from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Annotation, CaptureSession
from app.schemas import AnnotationCreate, AnnotationResponse
import uuid

router = APIRouter()

@router.get("/session/{session_id}",
            response_model=List[AnnotationResponse])
def list_annotations(session_id: str, 
                     db: Session = Depends(get_db)):
    session = db.query(CaptureSession).filter(
        CaptureSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, 
                            detail="Session not found")
    return db.query(Annotation).filter(
        Annotation.session_id == session_id).all()

@router.post("/session/{session_id}",
             response_model=AnnotationResponse, status_code=201)
def create_annotation(
    session_id: str,
    payload: AnnotationCreate,
    db: Session = Depends(get_db)
):
    session = db.query(CaptureSession).filter(
        CaptureSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, 
                            detail="Session not found")
    annotation = Annotation(
        id=str(uuid.uuid4()),
        session_id=session_id,
        created_by="system",  # replaced by auth later
        **payload.model_dump()
    )
    db.add(annotation)
    db.commit()
    db.refresh(annotation)
    return annotation

@router.patch("/{annotation_id}/resolve",
              response_model=AnnotationResponse)
def resolve_annotation(annotation_id: str, 
                       db: Session = Depends(get_db)):
    ann = db.query(Annotation).filter(
        Annotation.id == annotation_id).first()
    if not ann:
        raise HTTPException(status_code=404, 
                            detail="Annotation not found")
    ann.resolved = True
    db.commit()
    db.refresh(ann)
    return ann

@router.delete("/{annotation_id}", status_code=204)
def delete_annotation(annotation_id: str, 
                      db: Session = Depends(get_db)):
    ann = db.query(Annotation).filter(
        Annotation.id == annotation_id).first()
    if not ann:
        raise HTTPException(status_code=404, 
                            detail="Annotation not found")
    db.delete(ann)
    db.commit()
