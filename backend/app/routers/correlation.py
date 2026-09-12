from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database import get_db
from app.auth import get_current_user
from app.models import FrameGpsCorrelation, Path
from app.schemas import CorrelationResponse, CorrelationDetailResponse
from app.services.correlation_worker import enqueue_correlation

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/correlations", tags=["correlation"])

@router.post("/{path_id}")
async def trigger_correlation(
    path_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user =  Depends(get_current_user)
):
    """
    Trigger timestamp correlation for a path.
    Correlates GPS waypoints with video frames.
    """
    path = db.query(Path).filter(
        Path.id == path_id,
        Path.user_id == current_user.id
    ).first()
    
    if not path:
        raise HTTPException(status_code=404, detail="Path not found")
    
    try:
        background_tasks.add_task(enqueue_correlation, path_id)
        return {"status": "processing", "path_id": path_id}
    except Exception as e:
        logger.error(f"Failed to enqueue correlation: {e}")
        raise HTTPException(status_code=500, detail="Failed to start correlation")

@router.get("/{path_id}", response_model=CorrelationDetailResponse)
async def get_correlations(
    path_id: str,
    db: Session = Depends(get_db),
    current_user =  Depends(get_current_user)
):
    """
    Get all correlations for a path (GPS waypoint → video frame mappings).
    """
    path = db.query(Path).filter(
        Path.id == path_id,
        Path.user_id == current_user.id
    ).first()
    
    if not path:
        raise HTTPException(status_code=404, detail="Path not found")
    
    correlations = db.query(FrameGpsCorrelation).filter(
        FrameGpsCorrelation.path_id == path_id
    ).order_by(FrameGpsCorrelation.created_at).all()
    
    return {
        "path_id": path_id,
        "correlation_count": len(correlations),
        "correlations": [CorrelationResponse.model_validate(c) for c in correlations]
    }
