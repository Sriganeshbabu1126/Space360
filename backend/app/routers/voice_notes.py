from fastapi import (APIRouter, Depends, HTTPException, 
                     UploadFile, File)
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import VoiceNote, CaptureSession
from app.schemas import VoiceNoteResponse
from app.services.gcs_service import upload_audio
import uuid

router = APIRouter()

@router.get("/session/{session_id}",
            response_model=List[VoiceNoteResponse])
def list_voice_notes(session_id: str, 
                     db: Session = Depends(get_db)):
    session = db.query(CaptureSession).filter(
        CaptureSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, 
                            detail="Session not found")
    return db.query(VoiceNote).filter(
        VoiceNote.session_id == session_id).all()

@router.post("/session/{session_id}",
             response_model=VoiceNoteResponse, status_code=201)
async def upload_voice_note(
    session_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    session = db.query(CaptureSession).filter(
        CaptureSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, 
                            detail="Session not found")

    # Get site_id by traversing the relationship
    site_id = (session.location_point
                      .floor_plan.site_id)

    file_bytes = await file.read()
    audio_url = upload_audio(file_bytes, site_id, session_id)

    note = VoiceNote(
        id=str(uuid.uuid4()),
        session_id=session_id,
        audio_url=audio_url,
        ai_status="pending",
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

@router.get("/{note_id}", response_model=VoiceNoteResponse)
def get_voice_note(note_id: str, db: Session = Depends(get_db)):
    note = db.query(VoiceNote).filter(
        VoiceNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, 
                            detail="Voice note not found")
    return note

@router.delete("/{note_id}", status_code=204)
def delete_voice_note(note_id: str, 
                      db: Session = Depends(get_db)):
    note = db.query(VoiceNote).filter(
        VoiceNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, 
                            detail="Voice note not found")
    db.delete(note)
    db.commit()
