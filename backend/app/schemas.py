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

class ContractorUpdate(BaseModel):
    name: Optional[str] = None
    company: Optional[str] = None
    trade: Optional[str] = None
    designation: Optional[str] = None
    contact: Optional[str] = None
    access_level: Optional[AccessLevelEnum] = None

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
    contractor_ids: Optional[List[str]] = []

class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[IssueStatusEnum] = None
    issue_type: Optional[IssueTypeEnum] = None

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
    created_by: str
    created_at: datetime
    updated_at: datetime
    assignments: List[IssueAssignmentResponse] = []
    photos: List[IssuePhotoResponse] = []

    class Config:
        from_attributes = True
