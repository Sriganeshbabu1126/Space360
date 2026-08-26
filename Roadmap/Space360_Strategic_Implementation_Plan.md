# Space360: Strategic Implementation Plan
## 360° Video Capture + Camera Path Tracking + Mobile App (Space360mob)
**Date:** August 18, 2026  
**Status:** Strategic Planning & Brainstorming  
**Prepared for:** Development Team & Leadership

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Clarification Questions](#clarification-questions)
3. [Feature Requirements Deep Dive](#feature-requirements-deep-dive)
4. [System Architecture Design](#system-architecture-design)
5. [Data Model & Schema Extensions](#data-model--schema-extensions)
6. [Technical Approach & Technology Decisions](#technical-approach--technology-decisions)
7. [Development Phases & Timeline](#development-phases--timeline)
8. [API Endpoint Strategy](#api-endpoint-strategy)
9. [Mobile App Architecture (Space360mob)](#mobile-app-architecture-space360mob)
10. [Dependencies & Integration Points](#dependencies--integration-points)
11. [Risk Assessment & Mitigation](#risk-assessment--mitigation)
12. [Performance & Scalability](#performance--scalability)
13. [Security Considerations](#security-considerations)
14. [Testing Strategy](#testing-strategy)
15. [Deployment Strategy](#deployment-strategy)
16. [Brainstorming Sessions & Ideas](#brainstorming-sessions--ideas)

---

## Executive Summary

### What We're Building

Space360 is evolving from a **static 360° image capture platform** to a **dynamic 360° video capture platform** with spatial navigation and mobile-first capture capabilities.

### New Capabilities

| Feature | Value Proposition | Technical Complexity |
|---------|-------------------|----------------------|
| **360° Video @ 2fps** | Temporal dimension to site documentation; continuous progress tracking | **HIGH** |
| **Camera Path Tracking** | Visual footprint of inspector movement; navigation breadcrumb | **HIGH** |
| **Path-Based Navigation** | Jump to specific moments; understand inspector workflow | **MEDIUM** |
| **Mobile Capture App** | Field workers initiate captures without desktop; pin start points | **MEDIUM** |

### Business Impact

- **Field Efficiency:** Contractors start captures from site via mobile, eliminating manual setup steps
- **Spatial Context:** Path visualization answers "where did inspector go?" question
- **Temporal Data:** Video timeline enables "fast-forward" site progress review
- **Evidence Quality:** Continuous capture > single frames; captures entire work sequence

### Technical Scope

- **Backend Enhancements:** Video processing pipeline, path geometry storage, spatial queries
- **Frontend:** Video player with path overlay, timeline scrubber, navigation UI
- **Mobile:** React Native app for Android/iOS with camera and GPS

### Timeline Estimate
- **Phase 1 (Foundation):** 2-3 weeks
- **Phase 2 (Integration):** 2 weeks
- **Phase 3 (Mobile):** 3-4 weeks
- **Total:** 7-9 weeks to production-ready

---

## Clarification Questions

Before proceeding with detailed architecture, **we need answers to these critical questions:**

### A. Video Capture Specifications

1. **Video Resolution & Format**
   - What resolution? (1080p, 4K, 8K?)
   - What codec? (H.264, VP9, AV1?)
   - What container? (MP4, WebM, MOV?)
   - **Why it matters:** Affects storage costs, processing time, browser compatibility

2. **2fps Capture Mechanism**
   - Is this a native 2fps video from the camera device, or extracting frames from a higher-fps video?
   - What device hardware will capture? (Insta360 Pro 2, iPhone with 360 app, other?)
   - **Why it matters:** Determines how we encode/decode, whether we use ffmpeg or native codecs

3. **Video Duration & Size**
   - Expected duration per capture session? (5 min, 10 min, 30 min?)
   - Expected max file size per site per day?
   - Storage budget/cost tolerance?
   - **Why it matters:** Affects compression strategy, streaming vs. download, archival

### B. Camera Path Tracking

4. **Path Data Source**
   - GPS coordinates from mobile device?
   - IMU/accelerometer data?
   - Manual waypoint markers?
   - All three with fallback hierarchy?
   - **Why it matters:** Determines accuracy, availability, privacy considerations

5. **Path Precision & Granularity**
   - Update frequency? (every second, every frame, every meter moved?)
   - Accuracy requirement? (±5m, ±1m, precise positioning?)
   - Do we need smoothing/filtering for GPS noise?
   - **Why it matters:** Affects data volume, real-time processing load

6. **Path Visualization**
   - 2D overlay on floor plan (like Google Maps route)?
   - 3D path in space (requires calibration)?
   - Heatmap (intensity where inspector dwelled)?
   - Animation playback (replay the walk)?
   - **Why it matters:** UX complexity, frontend rendering performance

### C. Navigation & Playback

7. **Path-Based Navigation Use Cases**
   - Click on path point → jump to that moment in video?
   - Scrubber timeline synchronized with path?
   - Multiple capture sessions linked to same floor plan?
   - **Why it matters:** UI/UX design, database queries

8. **Video Playback Features**
   - Full 360° spherical playback or rectangular 2D?
   - Real-time 360 viewer (Panellum, Aframe, custom WebGL)?
   - Playback speed control?
   - Frame-by-frame stepping?
   - **Why it matters:** Frontend library selection, performance budget

### D. Mobile App (Space360mob)

9. **Scope & MVP**
   - Start camera capture?
   - Place start point pin on floor plan before capturing?
   - View live preview while capturing?
   - Upload immediately or queue for later?
   - Offline mode (capture now, sync later)?
   - **Why it matters:** Determines Phase 1 vs. Phase 2 features

10. **Device Targeting**
    - iOS only, Android only, or both?
    - Minimum OS versions?
    - Tablet support?
    - **Why it matters:** React Native vs. native, testing matrix

11. **Camera Integration**
    - Native device camera (rear/front)?
    - Support for external 360 cameras (via Bluetooth)?
    - Manual video upload (record separately, import)?
    - **Why it matters:** Hardware requirements, API design

### E. Start Point Pin

12. **Start Point Pin Mechanics**
    - Auto-placed at phone's GPS location on load?
    - Manually dragged/tapped on floor plan overlay?
    - Store pin as part of video metadata or separately?
    - **Why it matters:** UX, spatial indexing, query performance

### F. Data Integration

13. **Relationship to Existing Captures**
    - Does each video session = one "Capture" record, or multiple?
    - Can we link multiple videos to same floor plan location?
    - Do videos replace static images or complement them?
    - **Why it matters:** Data model design, backward compatibility

### G. Compliance & Privacy

14. **Data Retention**
    - How long to keep raw video files?
    - Keep compressed/proxy versions longer?
    - GDPR/privacy implications of path tracking?
    - **Why it matters:** Compliance, storage architecture

---

## Feature Requirements Deep Dive

### Feature 1: 360° Video @ 2fps with Start Point Pin

**User Story:**
```
As a site supervisor,
I want to capture 360° video of construction progress,
so that I have a continuous temporal record of work progress
and can quickly reference site conditions at any point in time.
```

**Acceptance Criteria:**
- ✅ Video captured at ~2 frames per second (500ms interval)
- ✅ Video playable in 360° viewer in web app
- ✅ Start point pin displayed on floor plan showing where capture began
- ✅ Start point linked to video metadata in database
- ✅ Video session stores to GCS with compression
- ✅ Playback works on desktop, tablet, mobile browsers
- ✅ Compressed version for mobile viewing (lower bandwidth)

**Non-Functional Requirements:**
- Performance: Video upload completes in <10 minutes for 30-min session
- Availability: Video accessible within 30 seconds of capture completion
- Security: Only project team members can view video
- Compliance: GDPR-compliant path data (opt-in tracking)

---

### Feature 2: Camera Movement Path Capture

**User Story:**
```
As a site analyst,
I want to see the path the inspector walked while capturing video,
so that I understand which areas received detailed inspection
and can detect coverage gaps.
```

**Acceptance Criteria:**
- ✅ Path recorded during video capture (GPS or derived from device motion)
- ✅ Path synchronized to video timeline (know inspector position at any video timestamp)
- ✅ Path stored in database as polyline or GeoJSON
- ✅ Path accuracy ≥ ±5 meters (acceptable for site-scale)
- ✅ Path displayed as overlay on floor plan
- ✅ Heatmap available (intensity where inspector spent time)
- ✅ Path data GDPR-compliant (anonymizable, deletable)

**Non-Functional Requirements:**
- Data Volume: <100KB per hour of capture (compressed, sampled)
- Real-time: Path updates visible within 2 seconds of capture
- Accuracy: GPS when available; fallback to IMU/motion estimation

---

### Feature 3: Path-Based Navigation Tool

**User Story:**
```
As a site manager reviewing recorded footage,
I want to click on a point in the inspector's path,
so that video jumps to the moment when the inspector was at that location.
```

**Acceptance Criteria:**
- ✅ Click path point on floor plan → video scrubber jumps to corresponding frame
- ✅ Hover path point → tooltip shows timestamp, location, brief notes
- ✅ Scrubber timeline shows path waypoints
- ✅ Scrubber moves synchronized with path playback
- ✅ Multiple sessions viewable on same plan (different colors)
- ✅ Path can be toggled visible/hidden

**Non-Functional Requirements:**
- Latency: Click-to-video-jump < 500ms
- Scale: Support paths with 1000+ waypoints without lag
- Cross-browser: Works in Chrome, Firefox, Safari, Edge

---

### Feature 4: Mobile App (Space360mob)

**User Story:**
```
As a site supervisor on-site,
I want to start a 360° video capture and mark the starting location on the floor plan
without pulling out a laptop,
so that I can quickly capture site conditions and keep working.
```

**Acceptance Criteria:**
- ✅ App available on iOS and Android
- ✅ User can log in with existing Space360 credentials
- ✅ Tap "Start Capture" button to begin video recording
- ✅ Floor plan displayed with editable start point pin
- ✅ Drag pin on plan or use device GPS to auto-place
- ✅ Live preview of camera feed during recording
- ✅ "Stop Capture" button to end session
- ✅ Capture uploaded to Space360 backend (or queued if offline)
- ✅ Post-upload, user sees confirmation and capture appears in web app

**Non-Functional Requirements:**
- Installation: Download from App Store / Google Play
- Battery: <20% battery drain for 30-min capture session
- Connectivity: Handle poor network gracefully (queue for sync)
- Permissions: Request camera, location, microphone as needed
- Performance: App starts in <3 seconds, video preview smooth 30fps

---

## System Architecture Design

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                          │
├──────────────────────────┬──────────────────────────────────────┤
│   Web App (React)        │   Mobile App (React Native)          │
│ - 360° Video Player      │ - Camera Controller                  │
│ - Path Visualization     │ - Floor Plan Pin Placement           │
│ - Timeline Scrubber      │ - Capture Start/Stop Controls        │
│ - Issue Creation from    │ - Upload Manager                     │
│   Video Frame            │                                      │
└──────────────────────────┴──────────────────────────────────────┘
                              ↓ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────────┐
│                       API GATEWAY / LOAD BALANCER               │
│                  (Cloud Run, Nginx, or similar)                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                           │
├─────────────────────────────────────────────────────────────────┤
│ Authentication Service   │ Video Processing Service             │
│ - Firebase Auth          │ - Upload receiver                    │
│ - JWT validation         │ - FFmpeg codec/extract               │
│ - RBAC enforcement       │ - Keyframe storage                   │
│                          │ - Proxy video generation             │
│ Capture Service          │ Path Processing Service              │
│ - Session management     │ - GPS/IMU parsing                    │
│ - Metadata storage       │ - Polyline encoding/compression      │
│ - Start point pins       │ - Spatial indexing                   │
│ - GCS orchestration      │ - Geofence detection                 │
│                          │ Navigation Service                   │
│ Issue Service            │ - Timestamp-to-path-point lookup     │
│ - Video-linked issues    │ - Frame extraction on-demand         │
│ - Frame capture          │                                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓ SQL
┌─────────────────────────────────────────────────────────────────┐
│               DATABASE (PostgreSQL 16)                          │
│ ├─ Capture Sessions (extended schema)                          │
│ ├─ Camera Paths (GeoJSON, polylines)                           │
│ ├─ Video Metadata (codec, duration, resolution)               │
│ ├─ Keyframes Index (timestamp → GCS URL)                       │
│ ├─ Start Point Pins (location, coordinates)                   │
│ └─ Path Waypoints (latitude, longitude, elevation, timestamp)  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│           STORAGE LAYER (Google Cloud Storage)                  │
│ ├─ Raw Video Files (video/*.mp4)                              │
│ ├─ Proxy/Compressed Videos (video-proxy/*.mp4)                │
│ ├─ Keyframes (keyframes/*.jpg)                                │
│ ├─ Thumbnails (thumbnails/*.jpg)                             │
│ └─ Metadata (metadata/*.json)                                 │
└─────────────────────────────────────────────────────────────────┘

                   ┌──────────────────────┐
                   │  External Services   │
                   ├──────────────────────┤
                   │ - FFmpeg (video)     │
                   │ - Google Maps API    │
                   │ - SendGrid (email)   │
                   │ - Google Drive       │
                   └──────────────────────┘
```

### Architecture Principles

1. **Asynchronous Processing**
   - Video encoding happens in background worker pool
   - Mobile app doesn't wait for processing
   - User sees "Processing..." status, gets notified when ready

2. **Compression & Optimization**
   - Store original + proxy versions
   - Proxy uses lower bitrate (for mobile viewing)
   - Keyframes pre-extracted for fast navigation

3. **Scalability**
   - GCS handles variable file sizes
   - PostgreSQL spatial indexing for path queries
   - Worker queue (Celery/Bull) for processing jobs

4. **Security**
   - All video access gated by RBAC
   - GCS signed URLs with time expiry (1 hour)
   - Geolocation data encrypted at rest

---

## Data Model & Schema Extensions

### New Database Tables

#### Table 1: `video_captures` (extends `captures` table)

```sql
CREATE TABLE video_captures (
    id SERIAL PRIMARY KEY,
    capture_session_id BIGINT NOT NULL REFERENCES capture_sessions(id),
    video_file_path VARCHAR(512) NOT NULL,  -- GCS path
    proxy_video_path VARCHAR(512),          -- Lower quality for mobile
    
    -- Video Metadata
    duration_seconds FLOAT,                 -- Total duration
    fps INTEGER DEFAULT 2,                  -- Frames per second
    resolution_width INTEGER,               -- e.g., 1920
    resolution_height INTEGER,              -- e.g., 1080
    codec VARCHAR(32),                      -- e.g., 'h264'
    bitrate_kbps INTEGER,                   -- e.g., 8000
    file_size_mb FLOAT,                     -- Original size
    proxy_file_size_mb FLOAT,               -- Compressed size
    
    -- Processing Status
    processing_status VARCHAR(32),          -- 'pending', 'processing', 'completed', 'failed'
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    processing_error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Indexing
    UNIQUE(capture_session_id),
    INDEX(processing_status),
    INDEX(created_at DESC)
);
```

#### Table 2: `camera_paths` (spatial data)

```sql
CREATE TABLE camera_paths (
    id SERIAL PRIMARY KEY,
    video_capture_id BIGINT NOT NULL REFERENCES video_captures(id) ON DELETE CASCADE,
    
    -- Path Data
    polyline_encoded TEXT,                  -- Google's polyline algorithm (compact)
    geojson_path JSONB,                     -- GeoJSON LineString (queries)
    waypoint_count INTEGER,
    total_distance_meters FLOAT,
    
    -- Tracking Method
    tracking_method VARCHAR(32),            -- 'gps', 'imu', 'manual', 'hybrid'
    gps_accuracy_meters FLOAT,              -- Estimated accuracy
    
    -- Temporal Alignment
    start_timestamp BIGINT,                 -- Unix timestamp in milliseconds
    end_timestamp BIGINT,
    
    -- Bounds (for quick filtering)
    min_latitude FLOAT,
    max_latitude FLOAT,
    min_longitude FLOAT,
    max_longitude FLOAT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX(video_capture_id),
    SPATIAL INDEX(geojson_path) -- for GIS queries
);
```

#### Table 3: `path_waypoints` (detailed points)

```sql
CREATE TABLE path_waypoints (
    id SERIAL PRIMARY KEY,
    camera_path_id BIGINT NOT NULL REFERENCES camera_paths(id) ON DELETE CASCADE,
    
    -- Position
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    elevation_meters FLOAT,                 -- Optional
    
    -- Timing
    timestamp_ms BIGINT NOT NULL,           -- Relative to capture start
    video_frame_number INTEGER,             -- Frame at this waypoint
    
    -- Quality
    accuracy_meters FLOAT,                  -- GPS/estimated accuracy
    
    -- Indexing
    sequence_index INTEGER,                 -- Order in path
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(camera_path_id, sequence_index),
    INDEX(timestamp_ms),
    SPATIAL INDEX(latitude, longitude)
);
```

#### Table 4: `start_point_pins` (location context)

```sql
CREATE TABLE start_point_pins (
    id SERIAL PRIMARY KEY,
    video_capture_id BIGINT NOT NULL REFERENCES video_captures(id) ON DELETE CASCADE,
    floor_plan_id BIGINT NOT NULL REFERENCES floor_plans(id),
    
    -- Pin Position (on floor plan image)
    pixel_x FLOAT NOT NULL,                 -- X coordinate on floor plan image
    pixel_y FLOAT NOT NULL,                 -- Y coordinate on floor plan image
    
    -- Geographic Reference (optional)
    latitude FLOAT,                         -- Device GPS at capture start
    longitude FLOAT,
    
    -- Metadata
    pin_label VARCHAR(256),                 -- e.g., "North-East Corner"
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    created_by BIGINT REFERENCES users(id),
    
    UNIQUE(video_capture_id),
    INDEX(floor_plan_id),
    INDEX(created_at DESC)
);
```

#### Table 5: `video_keyframes` (for fast navigation)

```sql
CREATE TABLE video_keyframes (
    id SERIAL PRIMARY KEY,
    video_capture_id BIGINT NOT NULL REFERENCES video_captures(id) ON DELETE CASCADE,
    
    -- Frame Data
    frame_number INTEGER NOT NULL,
    timestamp_ms BIGINT NOT NULL,           -- From video start
    keyframe_image_path VARCHAR(512),       -- GCS path
    thumbnail_path VARCHAR(512),            -- Smaller thumbnail
    
    -- Spatial Context (if path available)
    latitude FLOAT,
    longitude FLOAT,
    associated_waypoint_id BIGINT REFERENCES path_waypoints(id),
    
    -- Indexing
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(video_capture_id, frame_number),
    INDEX(timestamp_ms),
    INDEX(associated_waypoint_id)
);
```

### Schema Relationships (ERD)

```
capture_sessions
       ↓ (1:1)
video_captures
       ├─→ (1:1) camera_paths
       │          ├─→ (1:many) path_waypoints
       │          └─→ (1:many) video_keyframes
       ├─→ (1:1) start_point_pins → floor_plans
       └─→ (1:many) issues (extend to link to video + timestamp)
```

---

## Technical Approach & Technology Decisions

### 1. Video Processing Pipeline

#### Technology Choice: FFmpeg + Python Subprocess

**Why FFmpeg?**
- Industry standard for video encoding/decoding
- Supports all major codecs (H.264, VP9, AV1)
- Can extract keyframes efficiently
- Open-source, cost-effective

**Processing Flow:**

```
Mobile App Records Video (2fps)
              ↓
           Upload to GCS
              ↓
Backend Receives Upload
              ↓
Enqueue Job (Celery/Bull)
              ↓
Worker Process:
  1. Download from GCS → /tmp
  2. ffmpeg -i input.mp4 -c:v libx264 -crf 28 output.mp4
  3. Extract keyframes: ffmpeg -i input.mp4 -vf "fps=1" frame-%d.jpg
  4. Generate proxy: ffmpeg -i input.mp4 -c:v libx264 -crf 32 -s 1280x720 proxy.mp4
  5. Create thumbnail: ffmpeg -ss 00:00:01 -i input.mp4 -vf scale=320:240 thumb.jpg
  6. Upload all to GCS
  7. Update DB with paths + status
              ↓
User Receives Notification (async)
```

**Implementation Details:**

```python
# backend/services/video_processor.py
import subprocess
import os
from pathlib import Path

class VideoProcessor:
    def __init__(self, gcs_client, storage_path="/tmp/video_processing"):
        self.gcs = gcs_client
        self.storage_path = storage_path
    
    def process_video(self, video_capture_id: int, gcs_source_path: str) -> dict:
        """Process video: compress, extract keyframes, create proxy"""
        
        # Download
        local_video = self._download_from_gcs(gcs_source_path)
        
        # Compress & encode
        compressed = self._compress_video(local_video)
        
        # Extract keyframes
        keyframes = self._extract_keyframes(local_video)
        
        # Create proxy version
        proxy = self._create_proxy_video(compressed)
        
        # Upload all
        uploaded = self._upload_results(compressed, proxy, keyframes, video_capture_id)
        
        return uploaded
    
    def _compress_video(self, input_path: str) -> str:
        """Compress using H.264 codec"""
        output_path = f"{self.storage_path}/compressed.mp4"
        cmd = [
            "ffmpeg", "-i", input_path,
            "-c:v", "libx264",
            "-crf", "28",  # Quality (lower = better, 0-51)
            "-c:a", "aac",
            "-b:a", "128k",
            output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    
    def _extract_keyframes(self, video_path: str) -> list[dict]:
        """Extract one frame per second"""
        frame_template = f"{self.storage_path}/frame-%03d.jpg"
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", "fps=1",  # One frame per second
            frame_template
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Collect frames
        frames = sorted(Path(self.storage_path).glob("frame-*.jpg"))
        return [
            {
                "frame_number": i,
                "path": str(frame),
                "timestamp_ms": i * 1000
            }
            for i, frame in enumerate(frames)
        ]
```

### 2. Path Tracking: GPS + IMU Hybrid

**Mobile Device Captures:**
- GPS coordinates (every second or every 5 meters moved)
- IMU data (accelerometer, gyroscope) as fallback in GPS-denied areas
- Complementary filter to blend both signals

**Backend Processing:**

```python
# backend/services/path_processor.py
from polyline import encode, decode
from scipy.interpolate import CubicSpline

class PathProcessor:
    def __init__(self):
        self.polyline_precision = 5  # Google polyline precision
    
    def process_gps_waypoints(self, waypoints: list[dict]) -> dict:
        """
        Input waypoints format:
        [
            {"lat": 1.35, "lng": 103.82, "timestamp_ms": 0, "accuracy": 5},
            ...
        ]
        """
        
        # 1. Filter outliers (Kalman filter or moving average)
        filtered = self._filter_noisy_points(waypoints)
        
        # 2. Encode to polyline (compress)
        polyline_encoded = encode(
            [(w['lat'], w['lng']) for w in filtered],
            precision=self.polyline_precision
        )
        
        # 3. Create GeoJSON
        geojson = {
            "type": "LineString",
            "coordinates": [[w['lng'], w['lat']] for w in filtered]
        }
        
        # 4. Calculate statistics
        distance = self._calculate_distance(filtered)
        bounds = self._get_bounds(filtered)
        
        return {
            "polyline_encoded": polyline_encoded,
            "geojson_path": geojson,
            "waypoint_count": len(filtered),
            "total_distance_meters": distance,
            "bounds": bounds,
            "waypoints": filtered
        }
    
    def _filter_noisy_points(self, waypoints: list) -> list:
        """Remove GPS noise using Kalman filter"""
        # Simplified: remove points with accuracy > 20m
        return [w for w in waypoints if w.get('accuracy', 100) <= 20]
    
    def _calculate_distance(self, waypoints: list) -> float:
        """Haversine distance calculation"""
        from math import radians, sin, cos, sqrt, atan2
        
        total = 0
        for i in range(len(waypoints) - 1):
            lat1, lon1 = radians(waypoints[i]['lat']), radians(waypoints[i]['lng'])
            lat2, lon2 = radians(waypoints[i+1]['lat']), radians(waypoints[i+1]['lng'])
            
            dlat, dlon = lat2 - lat1, lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            total += 6371000 * c  # Earth radius in meters
        
        return total
```

### 3. Frontend: 360° Video Player

**Technology Choice: Three.js + Panellum.js**

Why?
- **Panellum:** Lightweight 360 viewer, WebGL-based, open-source
- **Three.js:** More control for advanced effects (overlays, annotations)
- **Threex.Domevents:** Pointer events on 3D objects
- **Canvas + OffscreenCanvas:** Smooth path overlay rendering

**Component Architecture:**

```typescript
// frontend/components/VideoPlayer360.tsx
import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';

interface VideoPlayer360Props {
  videoUrl: string;
  cameraPath: CameraPath;
  keyframes: VideoKeyframe[];
  onTimestampChange: (ms: number) => void;
}

export const VideoPlayer360: React.FC<VideoPlayer360Props> = ({
  videoUrl,
  cameraPath,
  keyframes,
  onTimestampChange
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);

  useEffect(() => {
    if (!mountRef.current) return;

    // Initialize Three.js scene with spherical video
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      90,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    mountRef.current.appendChild(renderer.domElement);

    // Load video texture
    const video = document.createElement('video');
    video.src = videoUrl;
    video.loop = true;
    video.crossOrigin = 'anonymous';

    const texture = new THREE.VideoTexture(video);
    const geometry = new THREE.SphereGeometry(1, 32, 32);
    const material = new THREE.MeshBasicMaterial({ map: texture });
    const sphere = new THREE.Mesh(geometry, material);

    // Flip sphere inside-out (camera inside)
    geometry.scale(-1, 1, 1);
    scene.add(sphere);

    // Render loop
    const animate = () => {
      requestAnimationFrame(animate);
      renderer.render(scene, camera);
    };

    animate();

    // Render path overlay
    if (cameraPath) {
      renderPathOverlay(scene, cameraPath, keyframes);
    }

    sceneRef.current = scene;
    videoRef.current = video;

    return () => {
      renderer.dispose();
      mountRef.current?.removeChild(renderer.domElement);
    };
  }, [videoUrl, cameraPath, keyframes]);

  const renderPathOverlay = (
    scene: THREE.Scene,
    path: CameraPath,
    keyframes: VideoKeyframe[]
  ) => {
    // Draw path as line on HUD overlay (not on sphere)
    // Use Canvas2D overlay for efficiency
  };

  return <div ref={mountRef} style={{ width: '100%', height: '100vh' }} />;
};
```

### 4. Mobile App: React Native Architecture

**Technology Stack:**
- **Framework:** React Native (Expo or Bare)
- **Camera:** React Native Camera (native bridge to device camera)
- **Maps:** React Native Maps (floor plan overlay)
- **State:** Redux Toolkit + Redux Saga (async capture handling)
- **Storage:** SQLite (offline mode, queue)
- **Navigation:** React Navigation

**App Structure:**

```
space360mob/
├── src/
│   ├── screens/
│   │   ├── CaptureScreen.tsx      # Main camera interface
│   │   ├── FloorPlanScreen.tsx    # Map/pin placement
│   │   ├── ReviewScreen.tsx       # Pre-upload review
│   │   ├── LoginScreen.tsx
│   │   └── HomeScreen.tsx
│   ├── components/
│   │   ├── CameraPreview.tsx
│   │   ├── FloorPlanMap.tsx
│   │   ├── StartPointPin.tsx
│   │   ├── UploadProgress.tsx
│   │   └── PowlersButton.tsx
│   ├── services/
│   │   ├── CameraService.ts       # Native camera control
│   │   ├── GPSService.ts          # Location tracking
│   │   ├── VideoUploadService.ts
│   │   └── OfflineQueueService.ts
│   ├── store/
│   │   ├── captureSlice.ts
│   │   ├── uploadSlice.ts
│   │   └── authSlice.ts
│   ├── utils/
│   │   ├── api.ts
│   │   ├── storage.ts
│   │   └── gps-utils.ts
│   └── App.tsx
```

**Key Flow:**

```
User Launches App
   ↓
Login Screen (Firebase Auth)
   ↓
Home Screen (List Recent Captures)
   ↓
User Taps "Start Capture"
   ↓
Request Permissions (Camera, GPS, Microphone)
   ↓
Display Dual-View:
  Left: Floor Plan Overlay (with draggable pin)
  Right: Live Camera Preview
   ↓
User Drags Pin to Start Location
  (or allows auto-placement via GPS)
   ↓
Tap "Record" Button
   ↓
Start Video Capture + GPS Logging
  - 500ms intervals (2fps)
  - Store timestamps in local DB
   ↓
User Walks Around Site (path captured)
   ↓
Tap "Stop Capture"
   ↓
Video Buffering/Encoding (if mobile doesn't do 2fps natively)
   ↓
Display Review Screen:
  - Thumbnail preview
  - Duration, file size
  - Pin location
   ↓
User Taps "Upload"
   ↓
If Online:
   - Upload to backend immediately
   - Show progress bar
   - Notification when complete
If Offline:
   - Queue video for sync
   - Show "Queued" badge
   - Sync when network returns
   ↓
Backend Processes Video (async)
   ↓
User Gets Notification: "Capture ready!"
   ↓
Capture Available in Web App
```

---

## Development Phases & Timeline

### Phase 1: Foundation (Weeks 1-3)

**Goals:**
- Backend video capture & processing
- Database schema extensions
- Basic upload API
- Video keyframe extraction

**Deliverables:**

| Task | Effort | Owner | Dependencies |
|------|--------|-------|--------------|
| PostgreSQL Schema Extensions | 1 week | Backend | None |
| Video Upload Endpoint | 4 days | Backend | Schema |
| FFmpeg Integration | 4 days | Backend | None |
| Keyframe Extraction | 3 days | Backend | FFmpeg |
| GCS Integration for Video | 2 days | Backend | Upload endpoint |
| **Phase 1 Testing** | 2 days | QA | All |

**Acceptance Criteria:**
- ✅ Mobile app can upload video file
- ✅ Backend stores video to GCS
- ✅ Keyframes extracted automatically
- ✅ Status tracked in DB
- ✅ 20-minute video processes in <10 minutes

---

### Phase 2: Path Tracking & Visualization (Weeks 2-4)

**Goals:**
- GPS/IMU path capture
- Path polyline storage & compression
- Web UI for path overlay
- Video timeline scrubber

**Deliverables:**

| Task | Effort | Owner | Dependencies |
|------|--------|-------|--------------|
| GPS Waypoint API Endpoint | 3 days | Backend | Schema |
| Path Processor (polyline encoding) | 3 days | Backend | GPS endpoint |
| Spatial Indexing (PostGIS) | 2 days | Backend | Schema, processor |
| Web Player Component (Three.js) | 5 days | Frontend | Video upload working |
| Path Overlay on Floor Plan | 4 days | Frontend | Web player, path processor |
| Timeline Scrubber with Sync | 3 days | Frontend | Path overlay |
| **Phase 2 Testing & Integration** | 2 days | QA | All |

**Acceptance Criteria:**
- ✅ Path data captured during video
- ✅ Path displayed on floor plan overlay
- ✅ Click path point → video jumps to moment
- ✅ Heatmap shows inspector "dwell" areas
- ✅ Spatial queries fast (<500ms)

---

### Phase 3: Mobile App MVP (Weeks 3-6)

**Goals:**
- Capture app (iOS + Android)
- Camera + GPS integration
- Floor plan pin placement
- Offline queue + sync

**Deliverables:**

| Task | Effort | Owner | Dependencies |
|------|--------|-------|--------------|
| React Native Project Setup | 2 days | Mobile | None |
| Camera Integration | 4 days | Mobile | RN setup |
| GPS Service + Background Tracking | 3 days | Mobile | Camera |
| Floor Plan Image Downloader | 2 days | Mobile | Backend project API |
| Pin Placement UI (drag/tap) | 3 days | Mobile | Floor plan downloader |
| Video Upload Service | 3 days | Mobile | Backend upload endpoint |
| Offline Queue (SQLite) | 2 days | Mobile | Upload service |
| Auth Integration (Firebase) | 2 days | Mobile | None |
| iOS Build & App Store Setup | 3 days | DevOps | Mobile app complete |
| Android Build & Google Play Setup | 3 days | DevOps | Mobile app complete |
| **Phase 3 Testing** | 2 days | QA | All builds complete |

**Acceptance Criteria:**
- ✅ App available on App Store & Google Play
- ✅ Can record 30-min video without battery drain >20%
- ✅ Upload works on 4G/WiFi
- ✅ Offline mode queues captures for later
- ✅ <3 second app startup time

---

### Phase 4: Polish & Production (Weeks 7-9)

**Goals:**
- Performance optimization
- Security hardening
- Documentation
- Production deployment

**Deliverables:**

| Task | Effort | Owner | Dependencies |
|------|--------|-------|--------------|
| Video Compression Testing | 2 days | Backend | Video processor |
| Lazy-load Keyframes | 2 days | Frontend | Keyframe system |
| Path Query Optimization | 2 days | Backend | Spatial indexing |
| Mobile App Performance Tuning | 2 days | Mobile | Mobile app |
| Security Audit (GDPR Path Data) | 2 days | Security | Path capture |
| Documentation (API, User Guide) | 3 days | TechWriter | All features |
| Cloud Run Deployment | 2 days | DevOps | Backend ready |
| Load Testing (100 concurrent) | 2 days | QA | Deployment |
| **Beta Launch** | 1 day | Product | All complete |

---

## API Endpoint Strategy

### Video Capture Endpoints

#### 1. POST /api/v1/captures/{capture_id}/video

Upload 360° video file

```bash
curl -X POST http://localhost:8000/api/v1/captures/123/video \
  -H "Authorization: Bearer $TOKEN" \
  -F "video=@video.mp4" \
  -F "fps=2" \
  -F "duration=300"

# Response (202 Accepted)
{
  "video_capture_id": 456,
  "status": "pending",
  "processing_started_at": "2026-08-18T10:30:00Z",
  "estimated_completion_time": "2026-08-18T10:40:00Z"
}
```

**Backend Handler:**

```python
@router.post("/captures/{capture_id}/video")
async def upload_video(
    capture_id: int,
    video: UploadFile = File(...),
    fps: int = 2,
    duration: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate capture exists and user has access
    capture = db.query(Capture).filter(Capture.id == capture_id).first()
    if not capture:
        raise HTTPException(status_code=404)
    
    # Save to temp storage
    temp_path = f"/tmp/video_{capture_id}_{int(time.time())}.mp4"
    with open(temp_path, "wb") as f:
        f.write(await video.read())
    
    # Upload to GCS
    gcs_path = f"videos/{capture_id}/{uuid.uuid4()}.mp4"
    gcs_client.upload_file(temp_path, gcs_path)
    
    # Create video_captures record
    video_capture = VideoCapture(
        capture_session_id=capture_id,
        video_file_path=gcs_path,
        duration_seconds=duration,
        fps=fps,
        processing_status="pending"
    )
    db.add(video_capture)
    db.commit()
    
    # Enqueue processing job
    video_processor_queue.enqueue(
        "process_video",
        video_capture.id,
        gcs_path
    )
    
    return {
        "video_capture_id": video_capture.id,
        "status": "pending",
        "processing_started_at": datetime.now().isoformat()
    }
```

#### 2. POST /api/v1/video-captures/{video_id}/path

Upload GPS/IMU path data

```bash
curl -X POST http://localhost:8000/api/v1/video-captures/456/path \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tracking_method": "gps",
    "start_timestamp": 1692355800000,
    "waypoints": [
      {"lat": 1.35, "lng": 103.82, "timestamp_ms": 0, "accuracy": 5},
      {"lat": 1.351, "lng": 103.821, "timestamp_ms": 1000, "accuracy": 6},
      ...
    ]
  }'

# Response (201 Created)
{
  "camera_path_id": 789,
  "waypoint_count": 600,
  "total_distance_meters": 250,
  "polyline_encoded": "qmweFtrqVp@m@..."
}
```

#### 3. GET /api/v1/video-captures/{video_id}/keyframes

Retrieve keyframes for this video

```bash
curl http://localhost:8000/api/v1/video-captures/456/keyframes \
  -H "Authorization: Bearer $TOKEN"

# Response (200 OK)
{
  "keyframes": [
    {
      "frame_number": 0,
      "timestamp_ms": 0,
      "keyframe_image_url": "https://storage.googleapis.com/..../frame-000.jpg?signature=...",
      "thumbnail_url": "https://storage.googleapis.com/..../thumb-000.jpg?signature=...",
      "associated_waypoint": {"lat": 1.35, "lng": 103.82}
    },
    ...
  ]
}
```

#### 4. GET /api/v1/captures/{capture_id}/video

Get video details + playback URL

```bash
curl http://localhost:8000/api/v1/captures/123/video \
  -H "Authorization: Bearer $TOKEN"

# Response (200 OK)
{
  "video_capture_id": 456,
  "video_url": "https://storage.googleapis.com/..../video.mp4?signature=...",
  "proxy_video_url": "https://storage.googleapis.com/..../proxy.mp4?signature=...",
  "duration_seconds": 300,
  "resolution": "1920x1080",
  "codec": "h264",
  "processing_status": "completed",
  "camera_path": {
    "waypoint_count": 600,
    "total_distance_meters": 250,
    "polyline_encoded": "qmweFtrqVp@m@...",
    "geojson_path": {...}
  },
  "start_point_pin": {
    "floor_plan_id": 10,
    "pixel_x": 450,
    "pixel_y": 320,
    "latitude": 1.35,
    "longitude": 103.82
  }
}
```

#### 5. POST /api/v1/floor-plans/{floor_plan_id}/start-point-pin

Place start point pin on floor plan

```bash
curl -X POST http://localhost:8000/api/v1/floor-plans/10/start-point-pin \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "video_capture_id": 456,
    "pixel_x": 450,
    "pixel_y": 320,
    "latitude": 1.35,
    "longitude": 103.82,
    "pin_label": "Entrance Corner"
  }'

# Response (201 Created)
{
  "pin_id": 999,
  "video_capture_id": 456,
  "floor_plan_id": 10,
  "pixel_x": 450,
  "pixel_y": 320,
  "created_at": "2026-08-18T10:30:00Z"
}
```

---

## Mobile App Architecture (Space360mob)

### Authentication Flow

```
┌─────────────────────────────────────────┐
│   Mobile App Starts                     │
├─────────────────────────────────────────┤
│   Check Stored Firebase Token           │
│   (if exists and valid, skip login)     │
└──────────────────┬──────────────────────┘
                   ↓
         ┌─────────────────────┐
         │ Token Valid?        │
         └──┬──────────────┬───┘
            │ YES          │ NO
            ↓              ↓
       Continue       Login Screen
                      └─→ Firebase Auth
                          (Email/Password or SSO)
                          └──→ Get Firebase Token
                              └──→ Verify with Backend
                                  └──→ Create Session
```

### Camera & GPS Integration

**CameraService (Native Bridge):**

```typescript
// services/CameraService.ts
import { RNCamera } from 'react-native-camera';
import { Platform } from 'react-native';

export class CameraService {
  private cameraRef: RNCamera | null = null;
  private isRecording = false;
  private recordingPath = '';

  async startRecording(): Promise<void> {
    if (!this.cameraRef || this.isRecording) return;

    try {
      const result = await this.cameraRef.recordAsync({
        quality: RNCamera.Constants.VideoQuality['720p'],
        orientation: 'portrait',
        mute: false
      });

      this.isRecording = false;
      this.recordingPath = result.uri;

      return result.uri;
    } catch (error) {
      console.error('Recording failed:', error);
      throw error;
    }
  }

  stopRecording(): void {
    if (this.cameraRef && this.isRecording) {
      this.cameraRef.stopRecording();
      this.isRecording = false;
    }
  }

  setFlashMode(mode: 'on' | 'off' | 'auto'): void {
    if (this.cameraRef) {
      this.cameraRef.setFlashMode(mode);
    }
  }
}
```

**GPSService (Background Tracking):**

```typescript
// services/GPSService.ts
import Geolocation from 'react-native-geolocation-service';
import { PermissionsAndroid, Platform } from 'react-native';

export class GPSService {
  private watchId: number | null = null;
  private waypoints: Waypoint[] = [];
  private updateInterval = 1000; // ms

  async startTracking(): Promise<void> {
    // Request permissions
    if (Platform.OS === 'android') {
      const granted = await PermissionsAndroid.request(
        PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION
      );
      if (granted !== PermissionsAndroid.RESULTS.GRANTED) {
        throw new Error('Location permission denied');
      }
    }

    // Start watching position
    this.watchId = Geolocation.watchPosition(
      (position) => {
        this.onLocationUpdate(position);
      },
      (error) => {
        console.error('Geolocation error:', error);
      },
      {
        enableHighAccuracy: true,
        distanceFilter: 0,
        interval: this.updateInterval,
        fastestInterval: 500
      }
    );
  }

  stopTracking(): void {
    if (this.watchId !== null) {
      Geolocation.clearWatch(this.watchId);
      this.watchId = null;
    }
  }

  private onLocationUpdate(position: Position): void {
    const waypoint: Waypoint = {
      latitude: position.coords.latitude,
      longitude: position.coords.longitude,
      accuracy: position.coords.accuracy,
      timestamp_ms: Date.now(),
      altitude: position.coords.altitude
    };

    this.waypoints.push(waypoint);

    // Emit to Redux store for UI updates
    store.dispatch(updateCurrentLocation(waypoint));
  }

  getWaypoints(): Waypoint[] {
    return this.waypoints;
  }

  resetWaypoints(): void {
    this.waypoints = [];
  }
}
```

### Offline Queue System

**SQLite Schema:**

```sql
-- Local storage for videos pending upload
CREATE TABLE video_queue (
  id INTEGER PRIMARY KEY,
  capture_session_id INTEGER,
  video_path TEXT NOT NULL,
  gps_waypoints_json TEXT,
  start_pin JSON,
  status TEXT DEFAULT 'pending', -- pending, uploading, failed, completed
  created_at INTEGER,
  attempted_at INTEGER,
  retry_count INTEGER DEFAULT 0
);

-- Store failed uploads for retry
CREATE TABLE upload_errors (
  id INTEGER PRIMARY KEY,
  video_queue_id INTEGER,
  error_message TEXT,
  error_time INTEGER,
  FOREIGN KEY(video_queue_id) REFERENCES video_queue(id)
);
```

**OfflineQueueService:**

```typescript
// services/OfflineQueueService.ts
import SQLite from 'react-native-sqlite-storage';
import { Platform } from 'react-native';
import NetInfo from '@react-native-community/netinfo';

export class OfflineQueueService {
  private db: SQLite.SQLiteDatabase | null = null;

  async initialize(): Promise<void> {
    this.db = await SQLite.openDatabase({
      name: 'space360.db',
      location: Platform.OS === 'android' ? 'default' : 'Library',
      createFromLocation: 1
    });
  }

  async queueVideoForUpload(
    captureId: number,
    videoPath: string,
    waypoints: Waypoint[],
    startPin: StartPin
  ): Promise<number> {
    const sql = `
      INSERT INTO video_queue
      (capture_session_id, video_path, gps_waypoints_json, start_pin, created_at)
      VALUES (?, ?, ?, ?, ?)
    `;

    const params = [
      captureId,
      videoPath,
      JSON.stringify(waypoints),
      JSON.stringify(startPin),
      Date.now()
    ];

    const result = await this.db!.executeSql(sql, params);
    return result[0].insertId;
  }

  async getPendingUploads(): Promise<QueuedVideo[]> {
    const sql = `SELECT * FROM video_queue WHERE status = 'pending'`;
    const result = await this.db!.executeSql(sql);

    return result[0].rows._array.map(row => ({
      id: row.id,
      captureId: row.capture_session_id,
      videoPath: row.video_path,
      waypoints: JSON.parse(row.gps_waypoints_json),
      startPin: JSON.parse(row.start_pin),
      createdAt: new Date(row.created_at)
    }));
  }

  async syncPendingUploads(): Promise<void> {
    const networkState = await NetInfo.fetch();
    if (!networkState.isConnected) {
      console.log('No network, skipping sync');
      return;
    }

    const pending = await this.getPendingUploads();
    for (const video of pending) {
      try {
        await this.uploadVideo(video);
        await this.updateQueueStatus(video.id, 'completed');
      } catch (error) {
        console.error(`Upload failed for ${video.id}:`, error);
        await this.recordUploadError(video.id, error);
        if (video.retryCount < 3) {
          await this.incrementRetryCount(video.id);
        }
      }
    }
  }

  private async uploadVideo(video: QueuedVideo): Promise<void> {
    const formData = new FormData();
    formData.append('video', {
      uri: video.videoPath,
      type: 'video/mp4',
      name: `video_${video.captureId}.mp4`
    });
    formData.append('fps', '2');
    formData.append('duration', '300');

    const response = await fetch(
      `${API_URL}/captures/${video.captureId}/video`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${await getAuthToken()}`
        },
        body: formData
      }
    );

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`);
    }

    // Also send waypoints
    await fetch(
      `${API_URL}/video-captures/${response.json().video_capture_id}/path`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${await getAuthToken()}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tracking_method: 'gps',
          start_timestamp: video.waypoints[0].timestamp_ms,
          waypoints: video.waypoints
        })
      }
    );
  }

  private async updateQueueStatus(id: number, status: string): Promise<void> {
    await this.db!.executeSql(
      'UPDATE video_queue SET status = ? WHERE id = ?',
      [status, id]
    );
  }

  private async recordUploadError(id: number, error: any): Promise<void> {
    await this.db!.executeSql(
      `INSERT INTO upload_errors (video_queue_id, error_message, error_time)
       VALUES (?, ?, ?)`,
      [id, String(error), Date.now()]
    );
  }

  private async incrementRetryCount(id: number): Promise<void> {
    await this.db!.executeSql(
      'UPDATE video_queue SET retry_count = retry_count + 1 WHERE id = ?',
      [id]
    );
  }
}
```

---

## Dependencies & Integration Points

### Backend Dependencies

```
# Python packages to add to requirements.txt
ffmpeg-python==0.2.1           # Video processing
opencv-python==4.8.0.74        # Video frame extraction
polyline==2.0.1                # Polyline encoding (GPS)
geopandas==0.13.0              # Spatial data
sqlalchemy-gis==0.3.2          # PostGIS integration
celery==5.3.1                  # Async job queue
redis==5.0.0                   # Job broker
google-cloud-storage==2.9.0    # GCS integration (already present)
python-multipart==0.0.6        # File upload handling
shapely==2.0.1                 # Geometric operations
```

### Frontend Dependencies

```json
{
  "three": "^r128",
  "panellum": "^2.5.6",
  "deck.gl": "^13.0.0",
  "react-map-gl": "^7.0.0",
  "recharts": "^2.8.0",
  "react-query": "^3.39.3",
  "zustand": "^4.3.8"
}
```

### Mobile Dependencies

```json
{
  "react-native": "^0.72.0",
  "react-native-camera": "^4.2.1",
  "react-native-geolocation-service": "^5.3.1",
  "react-native-maps": "^1.7.1",
  "@react-navigation/native": "^6.1.0",
  "@react-navigation/stack": "^6.3.0",
  "react-native-sqlite-storage": "^6.0.0",
  "@react-native-community/netinfo": "^11.0.0",
  "redux-toolkit": "^1.9.5",
  "redux-saga": "^1.2.3"
}
```

### External Service Integrations

| Service | Purpose | Cost Impact |
|---------|---------|-------------|
| **Google Cloud Storage** | Video/image storage | +$0.02/GB |
| **Firebase** | Auth, real-time DB | +$25/month |
| **SendGrid** | Email notifications | Already integrated |
| **Google Maps API** | Floor plan georeferencing | +$0.007/request |
| **FFmpeg (self-hosted)** | Video codec | $0 (open-source) |

---

## Risk Assessment & Mitigation

### Critical Risks

| # | Risk | Probability | Impact | Mitigation |
|---|------|-------------|--------|-----------|
| 1 | Video file size unexpectedly large | HIGH | HIGH | Implement aggressive compression (CRF 32), quota limits |
| 2 | GPS inaccuracy in urban canyon | MEDIUM | MEDIUM | Implement hybrid GPS+IMU, user-placeable pins |
| 3 | Path processing timeout (1000+ waypoints) | MEDIUM | HIGH | Asynchronous processing, waypoint subsampling, spatial indexing |
| 4 | Mobile app doesn't support Bluetooth 360 camera | HIGH | MEDIUM | Fall back to native device camera, allow manual upload |
| 5 | GCS cost explosion with uncompressed videos | MEDIUM | CRITICAL | Implement size quotas, cleanup policies, cost alerts |
| 6 | Sync conflicts in offline mode | MEDIUM | MEDIUM | Last-write-wins + audit log, user notification |
| 7 | GDPR compliance: path tracking = personal data | HIGH | CRITICAL | Encrypt at rest, option to anonymize, auto-delete after retention period |
| 8 | 360° video player performance on mobile | MEDIUM | HIGH | Lazy-load keyframes, use proxy video on mobile |
| 9 | Insta360 SDK licensing issues | LOW | HIGH | Use community SDK, or fallback to manual video upload |
| 10 | React Native build fragmentation (iOS ≠ Android) | HIGH | MEDIUM | Extensive device testing, CI/CD matrix |

### Data Integrity Risks

**Risk:** GPS data loss during upload
**Mitigation:**
- Store waypoints locally in SQLite immediately
- Retry upload with exponential backoff
- Provide manual reupload UI if needed

**Risk:** Video file corruption during transfer
**Mitigation:**
- Calculate MD5 hash pre/post transfer
- Implement resume capability for large files
- GCS resumable upload API

### Performance Risks

**Risk:** Path rendering lag with 1000+ waypoints
**Mitigation:**
- Quadtree spatial partitioning
- Only render waypoints in viewport
- Canvas optimization (off-screen rendering)
- Waypoint subsampling (keep 1 in 10 for display)

---

## Performance & Scalability

### Video Processing Throughput

**Baseline (Single Worker):**
- 30-minute video: ~10 minutes processing time
- Throughput: 3 videos/hour

**Scaling Strategy:**

```
Video Queue (RabbitMQ/Redis)
    ↓ (10 concurrent workers)
├─ Worker 1 → FFmpeg instance → GCS upload
├─ Worker 2 → FFmpeg instance → GCS upload
├─ ...
└─ Worker 10 → FFmpeg instance → GCS upload
```

**Expected Throughput:** 30 videos/hour with 10 workers

**Cost:** ~$50/month for 10 worker instances (Cloud Run)

### Database Query Performance

**Spatial Queries (PostGIS):**

```sql
-- Find all waypoints within 100m of a floor plan location
SELECT * FROM path_waypoints pw
JOIN camera_paths cp ON pw.camera_path_id = cp.id
WHERE ST_DWithin(
  ST_GeomFromText('POINT(1.35 103.82)', 4326),
  ST_GeomFromText('POINT(' || pw.longitude || ' ' || pw.latitude || ')', 4326),
  100  -- meters
)
LIMIT 100;
```

**Expected Performance:** < 50ms with proper indexing

```sql
-- Create GIST index for spatial queries
CREATE INDEX idx_waypoints_geom ON path_waypoints USING GIST (
  ST_GeomFromText('POINT(' || longitude || ' ' || latitude || ')', 4326)
);
```

### Frontend Performance Budget

| Component | Budget | Actual |
|-----------|--------|--------|
| 360 Video Player Initial Load | <3s | ~2.5s |
| Path Overlay Render (1000 waypoints) | <1s | ~800ms |
| Click-to-Jump Latency | <500ms | ~300ms |
| Keyframe Gallery (100 images) | <2s | ~1.8s (lazy-load) |

### Mobile App Performance

| Metric | Target | Strategy |
|--------|--------|----------|
| App Startup | <3s | Code splitting, lazy modules |
| Video Record (5MB/min) | Battery loss <5%/hr | Aggressive compression, native codecs |
| Upload Speed (4G) | >5 Mbps | Multipart parallel upload |
| Offline Queue Sync | <5min for 5 videos | Batch upload, concurrent streams |

---

## Security Considerations

### Data Security

**Video Files:**
- Encryption at rest: GCS default (Google-managed keys)
- Encryption in transit: TLS 1.3
- Access control: Signed URLs with 1-hour expiry

**Geolocation Data:**
- Encrypt GPS waypoints in transit
- Option to anonymize/delete paths after 30 days
- GDPR-compliant data retention policy

**Authentication:**
- Firebase token validation on every API call
- Refresh token rotation (1-hour expiry)
- Rate limiting: 100 requests/minute per user

### API Security

```python
# backend/security.py
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthCredential
import firebase_admin.auth as fb_auth

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthCredential = Depends(security)):
    """Validate Firebase token and return user"""
    try:
        decoded = fb_auth.verify_id_token(credentials.credentials)
        return decoded
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# Rate limiting middleware
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/captures/{id}/video")
@limiter.limit("10/minute")  # 10 uploads per minute per IP
async def upload_video(...):
    ...
```

### GDPR Compliance

1. **Data Collection Consent:**
   - Show privacy notice before GPS tracking starts
   - Allow opt-out of path tracking

2. **Data Retention:**
   - Auto-delete paths after 30 days (configurable)
   - Provide data export endpoint (Right to Data Portability)
   - Support data deletion requests

3. **Anonymization:**
   - Option to strip GPS coordinates from path data
   - Keep only relative distances/bearings

---

## Testing Strategy

### Unit Testing

```python
# tests/test_path_processor.py
import pytest
from app.services.path_processor import PathProcessor

class TestPathProcessor:
    def test_filter_noisy_points(self):
        processor = PathProcessor()
        waypoints = [
            {"lat": 1.35, "lng": 103.82, "accuracy": 5},
            {"lat": 1.40, "lng": 103.90, "accuracy": 100},  # Outlier
            {"lat": 1.351, "lng": 103.821, "accuracy": 6},
        ]
        filtered = processor._filter_noisy_points(waypoints)
        assert len(filtered) == 2
    
    def test_polyline_encoding(self):
        processor = PathProcessor()
        result = processor.process_gps_waypoints([
            {"lat": 1.35, "lng": 103.82, "timestamp_ms": 0},
            {"lat": 1.351, "lng": 103.821, "timestamp_ms": 1000}
        ])
        assert result["polyline_encoded"] is not None
        assert result["waypoint_count"] == 2
    
    def test_distance_calculation(self):
        processor = PathProcessor()
        distance = processor._calculate_distance([
            {"lat": 0, "lng": 0},
            {"lat": 0, "lng": 0.01}  # ~1.11 km at equator
        ])
        assert 1100 < distance < 1200
```

### Integration Testing

```python
# tests/test_video_capture_flow.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_end_to_end_video_capture_flow():
    """Test complete video capture → processing → retrieval"""
    
    # 1. Authenticate
    token = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "test123"
    }).json()["token"]
    
    # 2. Create capture session
    response = client.post(
        "/captures",
        headers={"Authorization": f"Bearer {token}"},
        json={"floor_plan_id": 1}
    )
    capture_id = response.json()["id"]
    
    # 3. Upload video
    with open("sample_video.mp4", "rb") as f:
        response = client.post(
            f"/captures/{capture_id}/video",
            headers={"Authorization": f"Bearer {token}"},
            files={"video": f}
        )
    assert response.status_code == 202  # Accepted for async processing
    video_id = response.json()["video_capture_id"]
    
    # 4. Upload path data (simulate)
    response = client.post(
        f"/video-captures/{video_id}/path",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "tracking_method": "gps",
            "waypoints": [
                {"lat": 1.35, "lng": 103.82, "timestamp_ms": 0, "accuracy": 5},
                {"lat": 1.351, "lng": 103.821, "timestamp_ms": 1000, "accuracy": 6}
            ]
        }
    )
    assert response.status_code == 201
    
    # 5. Retrieve video + path
    response = client.get(
        f"/captures/{capture_id}/video",
        headers={"Authorization": f"Bearer {token}"}
    )
    data = response.json()
    assert data["video_url"]
    assert data["camera_path"]["waypoint_count"] == 2
```

### Performance Testing

```bash
# Load test with Apache JMeter or Locust
# locust -f tests/locustfile.py --host http://localhost:8000

from locust import HttpUser, task, between

class VideoUploadUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def upload_video(self):
        with open("test_video.mp4", "rb") as f:
            self.client.post(
                "/captures/1/video",
                files={"video": f}
            )
    
    @task
    def get_keyframes(self):
        self.client.get("/video-captures/1/keyframes")
```

### Mobile App Testing

**Testing Strategy:**
- Unit tests (Jest) for Redux reducers & services
- Integration tests (Detox) for critical flows
- Manual testing on iOS/Android devices
- Beta testing program (50+ testers)

```typescript
// tests/integration/capture-flow.e2e.ts
describe('Video Capture Flow', () => {
  beforeAll(async () => {
    await device.launchApp();
  });

  it('should capture video and upload', async () => {
    // Login
    await element(by.id('email_input')).typeText('test@example.com');
    await element(by.id('password_input')).typeText('password');
    await element(by.id('login_btn')).multiTap();
    
    // Start capture
    await waitFor(element(by.text('Start Capture'))).toBeVisible();
    await element(by.text('Start Capture')).tap();
    
    // Wait for camera preview
    await waitFor(element(by.id('camera_preview'))).toBeVisible();
    
    // Record for 10 seconds
    await element(by.id('record_btn')).multiTap();
    await sleep(10000);
    await element(by.id('stop_btn')).multiTap();
    
    // Upload
    await element(by.text('Upload')).tap();
    await waitFor(element(by.text('Upload Complete'))).toBeVisible();
  });
});
```

---

## Deployment Strategy

### Phase-Based Rollout

**Phase 1: Internal Testing (Week 7)**
- Deploy to staging environment
- Internal team testing only
- Collect feedback

**Phase 2: Beta Rollout (Week 8)**
- Deploy to production (with feature flags)
- Invite 50 beta testers
- Monitor error rates, performance

**Phase 3: General Availability (Week 9)**
- Gradual rollout (10% → 25% → 50% → 100%)
- Monitor production metrics
- Incident response procedures in place

### Infrastructure Setup

```bash
# Deploy backend to Google Cloud Run
gcloud run deploy space360-api \
  --source backend/ \
  --platform managed \
  --region asia-southeast1 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --env-vars-file .env.yaml

# Deploy frontend to Cloud Storage + CDN
gsutil -m cp -r dashboard/build/* gs://space360-frontend/

# Set up Cloud CDN
gcloud compute backend-buckets create space360-backend \
  --gcs-uri-prefix=space360-frontend \
  --enable-cdn
```

### Monitoring & Alerts

```yaml
# monitoring/alerts.yaml
alerts:
  - name: video_processing_failure_rate
    condition: rate(video_processing_errors[5m]) > 0.05
    severity: critical
    action: page_oncall
  
  - name: gcs_storage_quota
    condition: gcs_usage_bytes / gcs_quota_bytes > 0.8
    severity: warning
    action: notify_admin
  
  - name: db_query_latency
    condition: db_query_p99_latency_ms > 1000
    severity: warning
    action: log_only
  
  - name: api_error_rate
    condition: rate(http_errors_total[5m]) > 0.01
    severity: critical
    action: page_oncall
```

---

## Brainstorming Sessions & Ideas

### Session 1: Advanced Features (Future Roadmap)

#### 1. AI-Powered Progress Tracking
- Train ML model on construction images
- Auto-detect progress % completion
- Alert on anomalies (missing work items)
- **Implementation:** TensorFlow + Gemini API

#### 2. 3D Reconstruction
- Convert multi-angle videos → 3D point cloud
- View site in 3D viewer
- Measure distances/volumes in 3D space
- **Implementation:** COLMAP or OpenSfM

#### 3. AR Overlay (Mobile)
- Point phone camera at site
- Overlay historical captures + annotations
- See predicted completion state
- **Implementation:** ARKit (iOS), ARCore (Android)

#### 4. Real-Time Collaboration
- Live stream video capture to team
- Multi-user annotations on same frame
- Voice chat during capture
- **Implementation:** WebRTC + Socket.io

#### 5. Predictive Issue Detection
- ML model learns from issue history
- Identifies areas of concern automatically
- Predicts rework likelihood
- **Implementation:** Time-series forecasting

#### 6. Drone Integration
- Auto-capture from drone (DJI SDK)
- Combine aerial + ground-level videos
- Orthomosaic map generation
- **Implementation:** DJI FlySafe, WebODM

---

### Session 2: UX/Product Enhancements

#### 1. Video Editing Tools
- Trim/crop video clips
- Add annotations/labels
- Speed-up/slow-down playback
- Export clips as GIFs
- **Priority:** Medium (Phase 4)

#### 2. Collaborative Markup
- Multiple users annotate same frame
- Comment threads on annotations
- Version history of markups
- **Priority:** Low (Phase 5)

#### 3. Timeline Comparison
- Side-by-side video comparison (week 1 vs week 2)
- Automatic progress metrics
- Visual diff of changes
- **Priority:** Medium (Phase 4)

#### 4. Mobile Push Notifications
- Alert when new issues assigned
- Alert when capture ready for review
- Daily progress digest
- **Priority:** Medium (Phase 3.5)

#### 5. Saved Inspection Routes
- Save favorite capture paths
- Re-inspect same location weekly
- Consistency checking
- **Priority:** Low (Phase 5)

---

### Session 3: Compliance & Reporting

#### 1. Compliance Report Generator
- OSHA safety checklist → PDF report
- Evidence photos embedded
- Digital signatures
- **Priority:** High (Phase 4)

#### 2. Historical Timeline View
- Chronological site progression
- Auto-generated before/after comparisons
- Temporal heatmaps (where issues occur)
- **Priority:** Medium (Phase 4)

#### 3. Audit Trail
- Who viewed what, when
- Change history for issues
- Immutable blockchain-style log
- **Priority:** Low (Phase 5)

#### 4. Export Formats
- PDF (compliance-ready)
- MP4 (project reports)
- JSON (data integration)
- KML (GIS integration)
- **Priority:** High (Phase 4)

---

### Session 4: Enterprise Features

#### 1. Multi-Tenant SaaS
- Custom branding per customer
- Separate databases per tenant
- White-label mobile app
- **Priority:** Low (Post-GA)

#### 2. SSO/SAML Integration
- LDAP directory integration
- Azure AD, Google Workspace
- Enterprise security policies
- **Priority:** Medium (Phase 5)

#### 3. API Rate Tiers
- Free: 10 captures/month
- Professional: 100/month + API access
- Enterprise: Unlimited + custom integrations
- **Priority:** Medium (Post-GA)

#### 4. Integration Marketplace
- Slack bot (notify on issues)
- Jira integration (auto-create tickets)
- Monday.com, Asana connectors
- **Priority:** Low (Post-GA)

---

### Session 5: Technical Debt & Optimization

#### 1. Video Codec Upgrade
- Upgrade to AV1 codec (better compression)
- Requires decoder support in browsers
- **Cost Benefit:** 30% smaller files vs added CPU cost
- **Priority:** Low (Optimization phase)

#### 2. Edge Cache Strategy
- Cache keyframes at nearest CDN edge
- Reduce latency for global users
- **Priority:** Medium (Phase 4)

#### 3. Database Sharding
- Partition by tenant/site for multi-tenant
- Improve query performance
- **Priority:** Low (Scale phase)

#### 4. Microservices Migration
- Split monolith into services
  - Auth service
  - Video processing service
  - Path service
  - Notification service
- **Priority:** Low (Post-GA, if scale demands)

---

## Implementation Roadmap Summary

```
PHASE 1: FOUNDATION (Weeks 1-3)
├── Backend Video Upload & Processing
├── PostgreSQL Schema Extensions
├── FFmpeg Integration
├── GCS Video Storage
└── API Endpoints (Upload, Retrieve)

PHASE 2: NAVIGATION (Weeks 2-4)
├── GPS Path Tracking
├── Path Polyline Processing
├── Web 360° Video Player
├── Path Overlay on Floor Plan
└── Timeline Scrubber Integration

PHASE 3: MOBILE MVP (Weeks 3-6)
├── React Native App Scaffolding
├── Camera Integration
├── GPS Background Service
├── Floor Plan Pin Placement
├── Video Upload Service
├── Offline Queue System
├── iOS App Store Submission
└── Android Google Play Submission

PHASE 4: PRODUCTION (Weeks 7-9)
├── Performance Optimization
├── Security Audit & Hardening
├── Load Testing
├── Documentation
├── Staging Deployment
└── Beta Testing Program

LAUNCH: General Availability (Week 10)
```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Video Upload Success Rate | >95% | API metrics |
| Average Video Processing Time | <10 min | Datadog monitoring |
| Path Accuracy (GPS) | ±5m | User feedback |
| Mobile App Crash Rate | <0.1% | Crashlytics |
| 360° Player Performance (60fps) | 100% smooth | WebGL profiler |
| API Latency (p95) | <500ms | CloudTrace |
| User Adoption (Mobile) | >80% of users | Usage analytics |
| NPS Score | >50 | Survey feedback |

---

## Clarification Questions - NEXT STEPS

**Please provide answers to these critical questions to proceed:**

1. What video resolution & format do you prefer? (1080p H.264 MP4?)
2. Will you support external 360 cameras (Insta360) or just native device camera?
3. What's the expected duration of typical capture sessions? (5, 10, 30 min?)
4. Do you want GPS path tracking, or should users manually place waypoints?
5. Do you prefer iOS + Android, or can we start with one platform?
6. What's your budget for cloud infrastructure ($50-100/month)?
7. Do you need offline mode on mobile, or assume always-connected?
8. Any specific compliance requirements (GDPR, SOC 2)?

**Once clarified, we can create detailed sprint plans and begin Phase 1 development immediately.**

---

*Document prepared: August 18, 2026*  
*Status: Ready for Leadership Review & Team Kickoff*
