from pydantic import BaseModel
from typing import Optional, List, Any
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

class AccessLevelEnum(str, Enum):
    view_only = "view_only"
    comment_and_change_status = "comment_and_change_status"
    create_issue = "create_issue"
    close_and_review = "close_and_review"

class IssueStatusEnum(str, Enum):
    open = "open"
    in_review = "in_review"
    pending = "pending"
    closed = "closed"
    critical = "critical"

class IssueTypeEnum(str, Enum):
    defect = "defect"
    safety_issue = "safety_issue"
    quality_issue = "quality_issue"
    incomplete_work = "incomplete_work"
    rework_required = "rework_required"

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
    open_issues_count: int = 0

    class Config:
        from_attributes = True

# --- Project Schemas (wraps Site) ---
class ProjectStats(BaseModel):
    total_issues: int = 0
    open_issues: int = 0
    critical_issues: int = 0
    closed_issues: int = 0
    total_floor_plans: int = 0
    total_captures: int = 0
    assigned_contractors: int = 0

class ProjectResponse(BaseModel):
    id: str
    name: str
    location: Optional[str] = None # Maps to address
    status: StatusEnum
    description: Optional[str] = None
    stats: Optional[ProjectStats] = None
    last_activity_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    status: Optional[StatusEnum] = None

class ProjectCreate(BaseModel):
    name: str
    location: Optional[str] = None
    description: Optional[str] = None
    org_id: Optional[str] = None

class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]

class ProjectDetailResponse(ProjectResponse):
    floor_plans: List['FloorPlanResponse'] = []
    recent_issues: List['IssueResponse'] = []
    contractors: List['ContractorResponse'] = []

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

# --- CaptureFrame Schemas ---
class CaptureFrameResponse(BaseModel):
    id: str
    session_id: str
    frame_number: int
    timestamp_seconds: float
    frame_url: str
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
    
    # Video sequence fields
    video_url: Optional[str] = None
    fps: Optional[int] = 2
    total_frames: Optional[int] = None
    processing_status: Optional[str] = "pending"
    error_message: Optional[str] = None
    processing_completed_at: Optional[datetime] = None
    frames: List[CaptureFrameResponse] = []
    
    created_at: datetime
    location_label: Optional[str] = None
    site_name: Optional[str] = None

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


# --- Contractor Schemas ---
class ContractorCreate(BaseModel):
    name: str
    company: Optional[str] = None
    trade: Optional[str] = None
    designation: Optional[str] = None
    contact: Optional[str] = None
    access_level: Optional[AccessLevelEnum] = AccessLevelEnum.view_only
    site_ids: Optional[List[str]] = []

class ContractorUpdate(BaseModel):
    name: Optional[str] = None
    company: Optional[str] = None
    trade: Optional[str] = None
    designation: Optional[str] = None
    contact: Optional[str] = None
    access_level: Optional[AccessLevelEnum] = None
    site_ids: Optional[List[str]] = None

class ContractorResponse(BaseModel):
    id: str
    name: str
    company: Optional[str]
    trade: Optional[str]
    designation: Optional[str]
    contact: Optional[str]
    access_level: AccessLevelEnum
    created_by: str
    created_at: datetime
    sites: List[SiteResponse] = []

    class Config:
        from_attributes = True


# --- Issue Assignment Schemas ---
class IssueAssignmentResponse(BaseModel):
    id: str
    issue_id: str
    contractor_id: str
    assigned_by: str
    assigned_at: datetime
    contractor: Optional[ContractorResponse] = None

    class Config:
        from_attributes = True


# --- Issue Comment Schemas ---
class IssueCommentCreate(BaseModel):
    comment_text: str

class IssueCommentResponse(BaseModel):
    id: str
    issue_id: str
    author: str
    comment_text: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Issue Photo Schemas ---
class IssuePhotoResponse(BaseModel):
    id: str
    issue_id: str
    photo_url: str
    uploaded_by: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Issue Schemas ---
class IssueCreate(BaseModel):
    title: str
    description: Optional[str] = None
    issue_type: Optional[IssueTypeEnum] = IssueTypeEnum.defect
    location_id: str
    session_a_id: Optional[str] = None
    session_b_id: Optional[str] = None
    frame_a_id: Optional[str] = None
    frame_b_id: Optional[str] = None
    contractor_ids: Optional[List[str]] = []

class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[IssueStatusEnum] = None
    issue_type: Optional[IssueTypeEnum] = None
    frame_a_id: Optional[str] = None
    frame_b_id: Optional[str] = None

class IssueResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: IssueStatusEnum
    issue_type: IssueTypeEnum
    location_id: str
    location_name: Optional[str] = None
    session_a_id: Optional[str]
    session_b_id: Optional[str]
    frame_a_id: Optional[str] = None
    frame_b_id: Optional[str] = None
    frame_a: Optional[CaptureFrameResponse] = None
    frame_b: Optional[CaptureFrameResponse] = None
    created_by: str
    created_at: datetime
    updated_at: datetime
    assignments: List[IssueAssignmentResponse] = []
    photos: List[IssuePhotoResponse] = []

    class Config:
        from_attributes = True

# --- Issue Notification Schemas ---
class IssueNotificationResponse(BaseModel):
    id: str
    issue_id: str
    sent_to: str
    sent_at: datetime
    status: str

    class Config:
        from_attributes = True

ProjectDetailResponse.model_rebuild()
