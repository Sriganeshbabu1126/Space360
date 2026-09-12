from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
import uuid
import logging
from datetime import datetime

from app.database import get_db
from app.auth import get_current_user
from app.models import VideoUpload, Path, VideoFrame
from app.schemas import VideoUploadRequest, VideoUploadResponse, VideoDetailResponse, VideoFrameResponse
from app.services.video_worker import VideoFrameExtractionWorker
from app.services.gcs_service import upload_private_file, get_signed_url

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/video-uploads", tags=["video"])

@router.post("/", response_model=VideoUploadResponse)
async def upload_video(
    background_tasks: BackgroundTasks,
    path_id: str = Form(...),
    video_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user =  Depends(get_current_user)
):
    """
    Upload video for a recorded path.
    """
    try:
        path_uuid = str(uuid.UUID(path_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid path_id format")
    
    path = db.query(Path).filter(
        Path.id == path_uuid,
        Path.user_id == current_user.id
    ).first()
    
    if not path:
        raise HTTPException(status_code=404, detail="Path not found or unauthorized")
    
    existing = db.query(VideoUpload).filter(
        VideoUpload.path_id == path_uuid
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Video already uploaded for this path")
    
    video_content = await video_file.read()
    file_size = len(video_content)
    
    if file_size > 2_000_000_000:
        raise HTTPException(status_code=413, detail="File too large (max 2GB)")
    
    video_id = str(uuid.uuid4())
    video_upload = VideoUpload(
        id=video_id,
        path_id=path_uuid,
        user_id=current_user.id,
        file_size_bytes=file_size,
        upload_status='pending'
    )
    db.add(video_upload)
    db.commit()
    db.refresh(video_upload)
    
    logger.info(f"Created video record: {video_id} for path {path_uuid}, size={file_size} bytes")
    
    try:
        gcs_destination_path = f"videos/{path_uuid}/{video_id}/original.mp4"
        upload_private_file(
            file_bytes=video_content,
            destination_path=gcs_destination_path,
            content_type="video/mp4"
        )
        temp_gcs_url = get_signed_url(gcs_destination_path, expiration_hours=24)
        video_upload.gcs_url = temp_gcs_url
        db.commit()
    except Exception as e:
        logger.error(f"Failed to upload video to GCS: {e}")
        video_upload.upload_status = 'failed'
        video_upload.error_message = f"GCS upload failed: {str(e)}"
        db.commit()
        raise HTTPException(status_code=500, detail="Video upload to storage failed")
    
    try:
        background_tasks.add_task(
            VideoFrameExtractionWorker.extract_frames,
            gcs_destination_path,
            video_id
        )
        logger.info(f"Enqueued frame extraction for video {video_id}")
    except Exception as e:
        logger.error(f"Failed to enqueue frame extraction: {e}")
        video_upload.upload_status = 'failed'
        video_upload.error_message = f"Job enqueue failed: {str(e)}"
        db.commit()
        raise HTTPException(status_code=500, detail="Failed to start processing")
    
    return VideoUploadResponse.model_validate(video_upload)

@router.get("/{video_id}", response_model=VideoDetailResponse)
async def get_video_detail(
    video_id: str,
    db: Session = Depends(get_db),
    current_user =  Depends(get_current_user)
):
    """
    Get video details including extracted frames.
    """
    try:
        video_uuid = str(uuid.UUID(video_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid video_id format")
    
    video = db.query(VideoUpload).filter(
        VideoUpload.id == video_uuid,
        VideoUpload.user_id == current_user.id
    ).first()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    frames = db.query(VideoFrame).filter(
        VideoFrame.video_id == video_uuid
    ).order_by(VideoFrame.frame_number).all()
    
    # We need to build a new VideoDetailResponse
    video_detail = VideoDetailResponse.model_validate(video)
    video_detail.frames = [VideoFrameResponse.model_validate(f) for f in frames]
    
    return video_detail

@router.get("/", response_model=list[VideoUploadResponse])
async def list_videos(
    db: Session = Depends(get_db),
    current_user =  Depends(get_current_user)
):
    """
    List all videos uploaded by current user.
    """
    videos = db.query(VideoUpload).filter(
        VideoUpload.user_id == current_user.id
    ).order_by(VideoUpload.created_at.desc()).all()
    
    return [VideoUploadResponse.model_validate(v) for v in videos]
