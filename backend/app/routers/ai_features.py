from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import CaptureSession, VoiceNote
from app.config import settings
import google.generativeai as genai
import httpx
import base64
import json
from app.auth import require_google_ai_pro, get_current_user
from fastapi import Security, Request

async def optional_auth(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return {"uid": "test_user", "ai_pro": True}
    try:
        from app.auth import get_current_user
        from fastapi.security import HTTPAuthorizationCredentials
        token = auth_header.split(" ")[1]
        cred = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        return get_current_user(cred)
    except Exception:
        return {"uid": "test_user", "ai_pro": True}


router = APIRouter()

has_api_key = bool(settings.GEMINI_API_KEY)
print(f"Gemini API key loaded: {'YES' if has_api_key else 'NO'}", flush=True)

if has_api_key:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")
else:
    model = None

def check_api_key():
    if not has_api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")

def fetch_local_image_as_base64(session_id: str) -> str:
    import os
    path = os.path.join("static", "test-captures", f"{session_id}.jpg")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Image file not found for session {session_id}")
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# --- 1. Change Detection ---
@router.post("/change-detection")
async def detect_changes(
    session_a_id: str,
    session_b_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(optional_auth)
):
    check_api_key()
    session_a = db.query(CaptureSession).filter(
        CaptureSession.id == session_a_id).first()
    session_b = db.query(CaptureSession).filter(
        CaptureSession.id == session_b_id).first()

    if not session_a or not session_b:
        raise HTTPException(status_code=404,
                            detail="One or both sessions not found")

    img_a = fetch_local_image_as_base64(session_a_id)
    img_b = fetch_local_image_as_base64(session_b_id)

    prompt = """You are a construction site inspector. Compare these two 360° site photos taken at different times. List all visible changes, new construction work, materials added or removed, and estimate overall progress percentage. Be specific and concise.

Return ONLY a valid JSON object in this exact format:
{
  "changes": ["list of changes..."],
  "progress_percentage": 50,
  "summary": "brief summary..."
}"""

    response = model.generate_content([
        prompt,
        {"mime_type": "image/jpeg", "data": img_a},
        {"mime_type": "image/jpeg", "data": img_b},
    ], generation_config=genai.types.GenerationConfig(response_mime_type="application/json"))

    try:
        result = json.loads(response.text)
    except json.JSONDecodeError:
        result = {"summary": "Failed to parse AI response.", "changes": [], "progress_percentage": 0}

    session_b.ai_changes = result
    session_b.ai_status = "done"
    db.commit()

    return result


# --- 2. Progress Estimation ---
@router.post("/progress-estimation/{session_id}")
async def estimate_progress(
    session_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(optional_auth)
):
    check_api_key()
    session = db.query(CaptureSession).filter(
        CaptureSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404,
                            detail="Session not found")

    img = fetch_local_image_as_base64(session_id)

    prompt = """You are a construction site inspector. Analyse this 360° site photo and estimate the construction progress percentage. Identify completed work, work in progress, and pending areas. Return a structured analysis.

Return ONLY a valid JSON object in this exact format:
{
  "progress_percentage": 45,
  "completed": ["list of completed items..."],
  "in_progress": ["list of items in progress..."],
  "pending": ["list of pending items..."]
}"""

    response = model.generate_content([
        prompt,
        {"mime_type": "image/jpeg", "data": img},
    ], generation_config=genai.types.GenerationConfig(response_mime_type="application/json"))

    try:
        result = json.loads(response.text)
    except json.JSONDecodeError:
        result = {"progress_percentage": 0, "completed": [], "in_progress": [], "pending": []}
        
    session.ai_summary = f"Progress: {result.get('progress_percentage', 0)}%"
    session.ai_status = "done"
    db.commit()

    return result


# --- 3. Voice Note Transcription ---
@router.post("/transcribe/{voice_note_id}")
async def transcribe_voice_note(
    voice_note_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(optional_auth)
):
    check_api_key()
    note = db.query(VoiceNote).filter(
        VoiceNote.id == voice_note_id).first()
    if not note:
        raise HTTPException(status_code=404,
                            detail="Voice note not found")

    audio_bytes = httpx.get(note.audio_url).content
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

    prompt = """Transcribe this construction site voice note accurately.
Then extract key information.

Return ONLY a valid JSON object in this exact format:
{
  "transcript": "full transcription text",
  "issues": ["list of issues or problems mentioned"],
  "materials": ["list of materials mentioned"],
  "trades": ["list of trades mentioned e.g. plumbing, electrical"],
  "action_items": ["list of action items or follow-ups mentioned"]
}"""

    response = model.generate_content([
        prompt,
        {"mime_type": "audio/webm", "data": audio_b64},
    ])

    result = json.loads(response.text)

    note.transcript = result.get("transcript", "")
    note.ai_tags = {
        "issues": result.get("issues", []),
        "materials": result.get("materials", []),
        "trades": result.get("trades", []),
        "action_items": result.get("action_items", []),
    }
    db.commit()

    return result


# --- 4. Natural Language Site Q&A ---
@router.post("/ask/{site_id}")
async def ask_site(
    site_id: str,
    question: str,
    db: Session = Depends(get_db),
    user: dict = Depends(optional_auth)
):
    check_api_key()
    # Gather all AI summaries and transcripts for this site
    sessions = (
        db.query(CaptureSession)
        .join(CaptureSession.location_point)
        .join(CaptureSession.location_point
              .property.mapper.class_.floor_plan)
        .filter_by(site_id=site_id)
        .all()
    )

    if not sessions:
        raise HTTPException(status_code=404,
                            detail="No sessions found for this site")

    context_lines = []
    for s in sessions:
        line = (f"[{s.captured_at.date()}] "
                f"Location: {s.location_point.label} | "
                f"Summary: {s.ai_summary or 'not analysed'}")
        context_lines.append(line)

        for note in s.voice_notes:
            if note.transcript:
                context_lines.append(
                    f"  Voice note: {note.transcript[:200]}"
                )

    context = "\n".join(context_lines)

    prompt = f"""You are an AI assistant for a construction site.
Use the following site capture records to answer the question.

SITE RECORDS:
{context}

QUESTION: {question}

Return ONLY a valid JSON object in this exact format:
{{
  "answer": "your answer to the question",
  "relevant_sessions": ["list of relevant session IDs or dates"],
  "confidence": "high|medium|low"
}}"""

    text_model = genai.GenerativeModel("gemini-2.0-flash")
    response = text_model.generate_content(prompt)
    return json.loads(response.text)
