from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class StatusEnum(str, Enum):
    active = "active"
    archived = "archived"

class AIStatusEnum(str, Enum):
    pending = "pending"
    processing = "processing"
    done = "done"
    error = "error"

class SeverityEnum(str, Enum):
    info = "info"
    warning = "warning"
    critical = "critical"

# --- Site Schemas ---
class SiteCreate(BaseModel):
    name: str
    address: Optional[str] = None
    gps_bounds: Optional[dict] = None
    org_id: Optional[str] = None

class SiteUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    status: Optional[StatusEnum] = None

class SiteResponse(BaseModel):
    id: str
    name: str
    address: Optional[str]
    gps_bounds: Optional[dict]
    org_id: Optional[str]
    created_by: str
    status: StatusEnum
    created_at: datetime

    class Config:
        from_attributes = True

# --- FloorPlan Schemas ---
class FloorPlanCreate(BaseModel):
    label: str

class FloorPlanResponse(BaseModel):
    id: str
    site_id: str
    label: str
    image_url: Optional[str]
    uploaded_at: datetime

    class Config:
        from_attributes = True

# --- LocationPoint Schemas ---
class LocationPointCreate(BaseModel):
    label: str
    pin_x: Optional[float] = None
    pin_y: Optional[float] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    heading: Optional[float] = 0.0

class LocationPointResponse(BaseModel):
    id: str
    floor_plan_id: str
    label: str
    pin_x: Optional[float]
    pin_y: Optional[float]
    gps_lat: Optional[float]
    gps_lng: Optional[float]
    heading: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True

# --- CaptureSession Schemas ---
class CaptureSessionResponse(BaseModel):
    id: str
    location_point_id: str
    captured_at: datetime
    image_url: Optional[str]
    thumbnail_url: Optional[str]
    captured_by: str
    device_model: Optional[str]
    gps_lat: Optional[float]
    gps_lng: Optional[float]
    ai_status: AIStatusEnum
    ai_summary: Optional[str]
    ai_changes: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True

# --- VoiceNote Schemas ---
class VoiceNoteResponse(BaseModel):
    id: str
    session_id: str
    audio_url: Optional[str]
    transcript: Optional[str]
    ai_tags: Optional[list]
    created_at: datetime

    class Config:
        from_attributes = True

# --- Annotation Schemas ---
class AnnotationCreate(BaseModel):
    yaw: Optional[float] = None
    pitch: Optional[float] = None
    comment: str
    severity: Optional[SeverityEnum] = SeverityEnum.info

class AnnotationResponse(BaseModel):
    id: str
    session_id: str
    created_by: str
    yaw: Optional[float]
    pitch: Optional[float]
    comment: str
    severity: SeverityEnum
    resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True
