import cv2
import os
import io
import uuid
from PIL import Image
from sqlalchemy.orm import Session
from app.models import CaptureSession, CaptureFrame
from app.services.gcs_service import upload_private_file, get_signed_url

def extract_frames_from_video(
    video_bytes: bytes,
    session_id: str,
    site_id: str,
    location_id: str,
    db: Session,
    fps: int = 2
) -> None:
    """
    Extract frames from video bytes, upload to GCS, and save to DB.
    """
    session = db.query(CaptureSession).filter_by(id=session_id).first()
    if not session:
        return
        
    temp_dir = f"temp_videos"
    os.makedirs(temp_dir, exist_ok=True)
    
    video_filename = f"{uuid.uuid4()}.mp4"
    video_path = os.path.join(temp_dir, video_filename)
    
    try:
        with open(video_path, "wb") as f:
            f.write(video_bytes)
            
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("Failed to open video file")
            
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(video_fps / fps) if video_fps > 0 else 15
        
        frames_extracted = 0
        frame_idx = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_idx % frame_interval == 0:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb_frame)
                img.thumbnail((2048, 1024))
                
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG', quality=85)
                img_bytes = img_byte_arr.getvalue()
                
                frame_gcs_path = f"sites/{site_id}/locations/{location_id}/sessions/{session_id}/frames/frame_{frames_extracted:03d}.jpg"
                upload_private_file(img_bytes, frame_gcs_path, "image/jpeg")
                
                timestamp = frame_idx / video_fps
                db_frame = CaptureFrame(
                    id=str(uuid.uuid4()),
                    session_id=session_id,
                    frame_number=frames_extracted,
                    timestamp_seconds=round(timestamp, 2),
                    frame_url=get_signed_url(frame_gcs_path)
                )
                db.add(db_frame)
                
                if frames_extracted == 0:
                    thumb = img.copy()
                    thumb.thumbnail((800, 400))
                    thumb_byte_arr = io.BytesIO()
                    thumb.save(thumb_byte_arr, format='JPEG', quality=75)
                    thumb_path = f"sites/{site_id}/locations/{location_id}/sessions/{session_id}/thumbnail.jpg"
                    upload_private_file(thumb_byte_arr.getvalue(), thumb_path, "image/jpeg")
                    session.thumbnail_url = get_signed_url(thumb_path)
                
                frames_extracted += 1
                
            frame_idx += 1
            
        cap.release()
        
        session.total_frames = frames_extracted
        session.processing_status = "complete"
        db.commit()
        
    except Exception as e:
        session.processing_status = "failed"
        session.error_message = str(e)
        db.commit()
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)
