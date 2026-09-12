import asyncio
import subprocess
import logging
import tempfile
import os
from pathlib import Path
from uuid import UUID
import json
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import VideoUpload, VideoFrame
from app.services.gcs_service import upload_private_file, get_signed_url, download_file

logger = logging.getLogger(__name__)

class VideoFrameExtractionWorker:
    
    @staticmethod
    def extract_frames(gcs_video_path: str, video_id: str) -> dict:
        """
        Download video from GCS, extract frames at 2fps, upload to GCS.
        Returns metadata: {frame_count, duration, fps, resolution, codec}
        """
        db = SessionLocal()
        temp_video_path = None
        video_upload = None
        try:
            logger.info(f"Downloading video {video_id} from GCS...")
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_video:
                temp_video_path = tmp_video.name
            
            download_file(gcs_video_path, temp_video_path)
            logger.info(f"Downloaded to {temp_video_path}")
            
            logger.info(f"Probing video metadata...")
            metadata = VideoFrameExtractionWorker._probe_video(temp_video_path)
            duration_seconds = metadata['duration']
            fps = 2  # Target 2fps extraction
            expected_frames = int(duration_seconds * fps)
            
            logger.info(f"Video: duration={duration_seconds}s, " +
                       f"fps_in={metadata['fps']}, resolution={metadata['resolution']}, " +
                       f"expected_frames={expected_frames}")
            
            video_upload = db.query(VideoUpload).filter(VideoUpload.id == str(UUID(video_id))).first()
            if video_upload:
                video_upload.duration_seconds = duration_seconds
                video_upload.fps = metadata['fps']
                video_upload.resolution = metadata['resolution']
                video_upload.codec = metadata['codec']
                video_upload.upload_status = 'processing'
                db.commit()
            
            with tempfile.TemporaryDirectory() as temp_dir:
                logger.info(f"Extracting frames at 2fps...")
                output_pattern = os.path.join(temp_dir, 'frame_%04d.jpg')
                
                ffmpeg_cmd = [
                    'ffmpeg',
                    '-i', temp_video_path,
                    '-vf', 'fps=2',
                    '-q:v', '5',  
                    output_pattern
                ]
                
                result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    raise Exception(f"FFmpeg failed: {result.stderr}")
                
                logger.info(f"Uploading frames to GCS...")
                frame_files = sorted(Path(temp_dir).glob('frame_*.jpg'))
                
                for frame_num, frame_file in enumerate(frame_files):
                    timestamp_seconds = frame_num / fps
                    
                    with open(frame_file, 'rb') as f:
                        frame_content = f.read()
                    
                    gcs_frame_path = f"frames/{video_id}/frame_{frame_num:04d}.jpg"
                    upload_private_file(
                        file_bytes=frame_content,
                        destination_path=gcs_frame_path,
                        content_type="image/jpeg"
                    )
                    
                    signed_url = get_signed_url(gcs_frame_path, expiration_hours=24)
                    
                    video_frame = VideoFrame(
                        video_id=str(UUID(video_id)),
                        frame_number=frame_num,
                        timestamp_seconds=timestamp_seconds,
                        thumbnail_url=signed_url,
                        metadata_json={
                            'size_bytes': os.path.getsize(frame_file),
                            'format': 'jpeg',
                            'quality': 5,
                            'gcs_path': gcs_frame_path
                        }
                    )
                    db.add(video_frame)
                    
                    if frame_num % 10 == 0:
                        logger.info(f"Processed {frame_num} frames...")
                
                db.commit()
                logger.info(f"Uploaded {len(frame_files)} frames to GCS")
            
            if video_upload:
                video_upload.upload_status = 'complete'
                db.commit()
            
            logger.info(f"Frame extraction complete for video {video_id}: {len(frame_files)} frames")
            return {
                'frame_count': len(frame_files),
                'duration_seconds': duration_seconds,
                'fps': metadata['fps'],
                'resolution': metadata['resolution'],
                'codec': metadata['codec']
            }
        
        except Exception as e:
            logger.error(f"Frame extraction failed for video {video_id}: {e}", exc_info=True)
            if video_upload:
                video_upload.upload_status = 'failed'
                video_upload.error_message = str(e)
                db.commit()
            raise
        
        finally:
            db.close()
            if temp_video_path and os.path.exists(temp_video_path):
                os.remove(temp_video_path)
    
    @staticmethod
    def _probe_video(video_path: str) -> dict:
        ffprobe_cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=duration,r_frame_rate,codec_name,width,height',
            '-of', 'json',
            video_path
        ]
        
        result = subprocess.run(ffprobe_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"ffprobe failed: {result.stderr}")
        
        data = json.loads(result.stdout)
        stream = data['streams'][0]
        
        fps_str = stream.get('r_frame_rate', '30/1')
        if '/' in fps_str:
            num, denom = map(float, fps_str.split('/'))
            fps = num / denom
        else:
            fps = float(fps_str)
        
        duration = float(stream.get('duration', 0))
        width = stream.get('width', 1920)
        height = stream.get('height', 1080)
        codec = stream.get('codec_name', 'h264')
        
        return {
            'duration': duration,
            'fps': int(round(fps)),
            'resolution': f"{width}x{height}",
            'codec': codec
        }
