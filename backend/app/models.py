import uuid
from datetime import datetime
from sqlalchemy import (Column, String, Float, Boolean, 
                        DateTime, Text, JSON, ForeignKey, Enum)
from sqlalchemy.orm import relationship
from app.database import Base
import enum

def generate_uuid():
    return str(uuid.uuid4())

class StatusEnum(str, enum.Enum):
    active = "active"
    archived = "archived"

class AIStatusEnum(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    done = "done"
    error = "error"

class SeverityEnum(str, enum.Enum):
    info = "info"
    warning = "warning"
    critical = "critical"

class AccessLevelEnum(str, enum.Enum):
    view_only = "view_only"
    comment_and_change_status = "comment_and_change_status"
    create_issue = "create_issue"
    close_and_review = "close_and_review"

class IssueStatusEnum(str, enum.Enum):
    open = "open"
    in_review = "in_review"
    pending = "pending"
    closed = "closed"
    critical = "critical"

class IssueTypeEnum(str, enum.Enum):
    defect = "defect"
    safety_issue = "safety_issue"
    quality_issue = "quality_issue"
    incomplete_work = "incomplete_work"
    rework_required = "rework_required"

class Site(Base):
    __tablename__ = "sites"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    address = Column(String)
    gps_bounds = Column(JSON)
    org_id = Column(String)
    created_by = Column(String, nullable=False)
    status = Column(Enum(StatusEnum), default=StatusEnum.active)
    description = Column(Text, nullable=True)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    floor_plans = relationship("FloorPlan", back_populates="site",
                               cascade="all, delete-orphan")


class FloorPlan(Base):
    __tablename__ = "floor_plans"

    id = Column(String, primary_key=True, default=generate_uuid)
    site_id = Column(String, ForeignKey("sites.id"), nullable=False)
    label = Column(String, nullable=False)
    image_url = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    site = relationship("Site", back_populates="floor_plans")
    location_points = relationship("LocationPoint", 
                                   back_populates="floor_plan",
                                   cascade="all, delete-orphan")


class LocationPoint(Base):
    __tablename__ = "location_points"

    id = Column(String, primary_key=True, default=generate_uuid)
    floor_plan_id = Column(String, ForeignKey("floor_plans.id"), 
                           nullable=False)
    label = Column(String, nullable=False)
    pin_x = Column(Float)
    pin_y = Column(Float)
    gps_lat = Column(Float)
    gps_lng = Column(Float)
    heading = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    floor_plan = relationship("FloorPlan", 
                              back_populates="location_points")
    capture_sessions = relationship("CaptureSession", 
                                    back_populates="location_point",
                                    cascade="all, delete-orphan")


class CaptureSession(Base):
    __tablename__ = "capture_sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    location_point_id = Column(String, 
                               ForeignKey("location_points.id"), 
                               nullable=False)
    captured_at = Column(DateTime, default=datetime.utcnow)
    image_url = Column(String)
    thumbnail_url = Column(String)
    captured_by = Column(String, nullable=False)
    device_model = Column(String)
    gps_lat = Column(Float)
    gps_lng = Column(Float)
    ai_status = Column(Enum(AIStatusEnum), 
                       default=AIStatusEnum.pending)
    ai_summary = Column(Text)
    ai_changes = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    location_point = relationship("LocationPoint", 
                                  back_populates="capture_sessions")
    voice_notes = relationship("VoiceNote", 
                               back_populates="session",
                               cascade="all, delete-orphan")
    annotations = relationship("Annotation", 
                               back_populates="session",
                               cascade="all, delete-orphan")

    @property
    def location_label(self):
        return self.location_point.label if self.location_point else "Unknown Location"

    @property
    def site_name(self):
        if self.location_point and self.location_point.floor_plan and self.location_point.floor_plan.site:
            return self.location_point.floor_plan.site.name
        return "Unknown Site"


class VoiceNote(Base):
    __tablename__ = "voice_notes"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("capture_sessions.id"), 
                        nullable=False)
    audio_url = Column(String)
    transcript = Column(Text)
    ai_tags = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("CaptureSession", 
                           back_populates="voice_notes")


class Annotation(Base):
    __tablename__ = "annotations"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("capture_sessions.id"), 
                        nullable=False)
    created_by = Column(String, nullable=False)
    yaw = Column(Float)
    pitch = Column(Float)
    comment = Column(Text)
    severity = Column(Enum(SeverityEnum), default=SeverityEnum.info)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("CaptureSession", 
                           back_populates="annotations")


class ContractorSiteAssignment(Base):
    __tablename__ = "contractor_site_assignments"

    id = Column(String, primary_key=True, default=generate_uuid)
    contractor_id = Column(String, ForeignKey("contractors.id", ondelete="CASCADE"), nullable=False)
    site_id = Column(String, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
    assigned_by = Column(String, nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)

    contractor = relationship("Contractor", back_populates="site_assignments")
    site = relationship("Site")


class Contractor(Base):
    __tablename__ = "contractors"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    company = Column(String)
    trade = Column(String)
    designation = Column(String)
    contact = Column(String)
    access_level = Column(Enum(AccessLevelEnum), default=AccessLevelEnum.view_only)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    assignments = relationship("IssueAssignment", back_populates="contractor", cascade="all, delete-orphan")
    site_assignments = relationship("ContractorSiteAssignment", back_populates="contractor", cascade="all, delete-orphan")

    @property
    def sites(self):
        return [assignment.site for assignment in self.site_assignments if assignment.site]


class Issue(Base):
    __tablename__ = "issues"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(Enum(IssueStatusEnum), default=IssueStatusEnum.open)
    issue_type = Column(Enum(IssueTypeEnum), default=IssueTypeEnum.defect)
    location_id = Column(String, ForeignKey("location_points.id"), nullable=False)
    session_a_id = Column(String, ForeignKey("capture_sessions.id"), nullable=True)
    session_b_id = Column(String, ForeignKey("capture_sessions.id"), nullable=True)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    location = relationship("LocationPoint")
    session_a = relationship("CaptureSession", foreign_keys=[session_a_id])
    session_b = relationship("CaptureSession", foreign_keys=[session_b_id])
    assignments = relationship("IssueAssignment", back_populates="issue", cascade="all, delete-orphan")
    comments = relationship("IssueComment", back_populates="issue", cascade="all, delete-orphan", order_by="IssueComment.created_at")
    photos = relationship("IssuePhoto", back_populates="issue", cascade="all, delete-orphan", order_by="IssuePhoto.created_at")

    @property
    def location_name(self):
        if self.location and self.location.floor_plan:
            return f"{self.location.floor_plan.label} - {self.location.label}"
        elif self.location:
            return self.location.label
        return "Unknown Location"


class IssueAssignment(Base):
    __tablename__ = "issue_assignments"

    id = Column(String, primary_key=True, default=generate_uuid)
    issue_id = Column(String, ForeignKey("issues.id"), nullable=False)
    contractor_id = Column(String, ForeignKey("contractors.id"), nullable=False)
    assigned_by = Column(String, nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)

    issue = relationship("Issue", back_populates="assignments")
    contractor = relationship("Contractor", back_populates="assignments")

class IssueComment(Base):
    __tablename__ = "issue_comments"

    id = Column(String, primary_key=True, default=generate_uuid)
    issue_id = Column(String, ForeignKey("issues.id"), nullable=False)
    author = Column(String, nullable=False)
    comment_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    issue = relationship("Issue", back_populates="comments")

class IssuePhoto(Base):
    __tablename__ = "issue_photos"

    id = Column(String, primary_key=True, default=generate_uuid)
    issue_id = Column(String, ForeignKey("issues.id"), nullable=False)
    photo_url = Column(String, nullable=False)
    uploaded_by = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    issue = relationship("Issue", back_populates="photos")

class IssueNotification(Base):
    __tablename__ = "issue_notifications"

    id = Column(String, primary_key=True, default=generate_uuid)
    issue_id = Column(String, ForeignKey("issues.id"), nullable=False)
    sent_to = Column(String, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False, default="success")

    issue = relationship("Issue")
