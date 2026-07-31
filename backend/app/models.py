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


class Site(Base):
    __tablename__ = "sites"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    address = Column(String)
    gps_bounds = Column(JSON)
    org_id = Column(String)
    created_by = Column(String, nullable=False)
    status = Column(Enum(StatusEnum), default=StatusEnum.active)
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
