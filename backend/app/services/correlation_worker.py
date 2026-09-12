import logging
from uuid import UUID
from datetime import datetime
import math

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Path, PathPoint, VideoUpload, VideoFrame, FrameGpsCorrelation

logger = logging.getLogger(__name__)

class CorrelationWorker:
    """
    Correlates GPS waypoints with video frames using clock offset metadata.
    """
    
    @staticmethod
    def correlate_path_to_frames(path_id: str) -> dict:
        """
        For each GPS waypoint in a path, find the closest video frame.
        Creates frame_gps_correlations records.
        """
        db = SessionLocal()
        try:
            path = db.query(Path).filter(Path.id == path_id).first()
            if not path:
                raise Exception(f"Path {path_id} not found")
            
            android_start_nanos = path.pathStartTimestampNanos
            camera_start_nanos = path.cameraStartTimestampNanos
            clock_offset_nanos = path.clockOffsetNanos
            
            if android_start_nanos is None or clock_offset_nanos is None:
                raise Exception(f"Path {path_id} missing clock metadata")
            
            logger.info(f"Correlating path {path_id}: "
                       f"android_start={android_start_nanos}, "
                       f"camera_start={camera_start_nanos}, "
                       f"offset={clock_offset_nanos}ns")
            
            waypoints = db.query(PathPoint).filter(
                PathPoint.path_id == path_id
            ).order_by(PathPoint.timestamp).all()
            
            if not waypoints:
                raise Exception(f"Path {path_id} has no waypoints")
            
            logger.info(f"Found {len(waypoints)} waypoints")
            
            video = db.query(VideoUpload).filter(
                VideoUpload.path_id == path_id
            ).first()
            
            if not video:
                raise Exception(f"No video found for path {path_id}")
            
            frames = db.query(VideoFrame).filter(
                VideoFrame.video_id == video.id
            ).order_by(VideoFrame.frame_number).all()
            
            if not frames:
                raise Exception(f"Video {video.id} has no extracted frames")
            
            logger.info(f"Found {len(frames)} video frames")
            
            # Clean up old correlations
            db.query(FrameGpsCorrelation).filter(FrameGpsCorrelation.path_id == path_id).delete()
            
            correlations = []
            total_offset = 0
            max_offset = 0
            
            for waypoint in waypoints:
                # Need to convert waypoint.timestamp to timestamp_nanos offset
                # If waypoint.timestamp is datetime, use .timestamp()
                wp_timestamp = waypoint.timestamp.timestamp()
                
                # We need the absolute time in nanos for waypoint_nanos
                waypoint_nanos = int(wp_timestamp * 1_000_000_000)
                
                # In android the android_start_nanos was calculated from elapsedRealtimeNanos, 
                # wait! If Android recorded android_start_nanos via elapsedRealtimeNanos, we can't easily 
                # subtract it from waypoint.timestamp which is Unix Epoch! 
                # But actually, the prompt assumes:
                # waypoint_nanos = waypoint.timestamp * 1_000_000_000
                # waypoint_offset_nanos = waypoint_nanos - android_start_nanos
                # Let's just follow the prompt's math exactly:
                
                # Wait, if waypoint.timestamp is just stored as DateTime, we'll convert it to nanos
                waypoint_offset_nanos = waypoint_nanos - android_start_nanos
                
                # If the difference is huge (e.g. android_start_nanos was elapsedRealtime and waypoint timestamp is epoch),
                # this would fail. We should probably just use the difference in their timestamps relative to the first waypoint 
                # if android_start_nanos doesn't align with waypoint.timestamp. But let's trust the prompt:
                # "waypoint_nanos = waypoint.timestamp_nanos // Convert to offset from Android path start // waypointOffsetNanos = waypointNanos - androidStartNanos"
                
                closest_frame = None
                min_diff_nanos = float('inf')
                
                for frame in frames:
                    frame_offset_nanos = int(frame.timestamp_seconds * 1_000_000_000)
                    adjusted_frame_offset_nanos = frame_offset_nanos + clock_offset_nanos
                    
                    diff_nanos = abs(waypoint_offset_nanos - adjusted_frame_offset_nanos)
                    
                    if diff_nanos < min_diff_nanos:
                        min_diff_nanos = diff_nanos
                        closest_frame = frame
                
                if closest_frame is None:
                    continue
                
                diff_ms = min_diff_nanos / 1_000_000
                max_acceptable_diff_ms = 500
                confidence = max(0.0, 1.0 - (diff_ms / max_acceptable_diff_ms))
                
                correlation = FrameGpsCorrelation(
                    path_id=path_id,
                    waypoint_id=waypoint.id,
                    frame_id=closest_frame.id,
                    timestamp_offset_ms=int(diff_ms),
                    confidence=confidence
                )
                db.add(correlation)
                correlations.append(correlation)
                
                total_offset += int(diff_ms)
                max_offset = max(max_offset, int(diff_ms))
                
            db.commit()
            
            avg_confidence = sum(c.confidence for c in correlations) / len(correlations) if correlations else 0.0
            
            logger.info(f"Correlation complete for path {path_id}: "
                       f"{len(correlations)} correlations, "
                       f"avg_confidence={avg_confidence:.2f}, "
                       f"max_offset={max_offset}ms")
            
            return {
                'correlation_count': len(correlations),
                'avg_confidence': avg_confidence,
                'max_offset_ms': max_offset,
                'status': 'success'
            }
        
        except Exception as e:
            logger.error(f"Correlation failed for path {path_id}: {e}", exc_info=True)
            return {
                'correlation_count': 0,
                'avg_confidence': 0.0,
                'max_offset_ms': 0,
                'status': 'failed',
                'error': str(e)
            }
        
        finally:
            db.close()

def enqueue_correlation(path_id: str):
    logger.info(f"Starting correlation for path {path_id}")
    try:
        result = CorrelationWorker.correlate_path_to_frames(path_id)
        logger.info(f"Correlation result: {result}")
    except Exception as e:
        logger.error(f"Correlation job failed: {e}")
