# Space360 Phase 1: Sprint Planning & Quick-Start Guide
## Foundation: 360° Video Upload & Processing (Weeks 1-3)
**Date:** August 18, 2026 | **Target:** GA Oct 6, 2026

---

## Table of Contents
1. [Sprint Overview](#sprint-overview)
2. [Week-by-Week Breakdown](#week-by-week-breakdown)
3. [Task Dependencies](#task-dependencies)
4. [Database Schema (SQL)](#database-schema-sql)
5. [API Specifications](#api-specifications)
6. [Code Examples](#code-examples)
7. [Testing Strategy](#testing-strategy)
8. [Deployment Checklist](#deployment-checklist)

---

## Sprint Overview

### Goals
- Backend can receive, process, and store 360° video
- Mobile app can upload video files to backend
- Keyframes auto-extracted for navigation
- Start point pin stored with video metadata
- Processing status visible to users

### Acceptance Criteria
```
✅ POST /captures/{id}/video endpoint accepts video file
✅ Video uploaded to GCS within 5 minutes
✅ FFmpeg processing starts automatically
✅ Keyframes extracted (1 per second, ~120 frames for 2min video)
✅ Database records created: video_captures, path_waypoints, video_keyframes
✅ GET /captures/{id}/video returns video URL + metadata
✅ Mobile app can successfully upload 30MB video
✅ Processing status: pending → processing → completed
✅ Zero data loss (videos persisted even if processing fails)
✅ Error handling (invalid format, oversized file, corrupted video)
```

### Team Allocation
| Role | Person | Hours/Week | Tasks |
|------|--------|-----------|-------|
| Backend Lead | Backend Dev | 40 | Video API, FFmpeg, GCS, DB schema |
| Frontend Lead | Frontend Dev | 30 | API integration, upload UI |
| Mobile Dev | Mobile Dev | 35 | Camera integration, upload service |
| DevOps | DevOps Eng | 20 | CI/CD, GCS setup, worker pool |
| QA | QA Eng | 20 | E2E testing, performance testing |

---

## Week-by-Week Breakdown

### Week 1: Foundation & Schema (Mon Aug 19 - Fri Aug 23)

#### Monday-Tuesday: Database Schema (Backend Lead)
**Task:** Design & migrate PostgreSQL schema

**Deliverables:**
```sql
-- Create 5 new tables
1. video_captures (video metadata)
2. camera_paths (GPS waypoints polyline)
3. path_waypoints (individual GPS points)
4. video_keyframes (extracted frames)
5. start_point_pins (floor plan location)

-- Create indexes for performance
6. idx_video_captures_session_id
7. idx_path_waypoints_timestamp
8. idx_video_keyframes_video_id
```

**File:** `backend/alembic/versions/xxxxx_add_video_capture_tables.py`

**Commands:**
```bash
cd backend
alembic revision --autogenerate -m "Add video capture tables"
alembic upgrade head
psql -U postgres -d fieldcheck -f schema.sql
```

**Acceptance:** 
- [ ] All 5 tables created
- [ ] All indexes created
- [ ] Migration script runs without errors
- [ ] Rollback tested (alembic downgrade)

---

#### Tuesday-Wednesday: Pydantic Models & API Schemas (Backend Lead)
**Task:** Create data models for API validation

**Deliverables:**
```python
# backend/app/schemas.py (add to existing file)

class VideoCaptureBase(BaseModel):
    duration_seconds: float
    fps: int = 2
    resolution_width: int
    resolution_height: int
    codec: str = "h264"

class VideoCaptureCreate(VideoCaptureBase):
    capture_session_id: int

class VideoCaptureResponse(VideoCaptureBase):
    id: int
    video_file_path: str
    processing_status: str
    created_at: datetime
    
class CameraPathResponse(BaseModel):
    id: int
    waypoint_count: int
    polyline_encoded: str
    total_distance_meters: float
    
class PathWaypointResponse(BaseModel):
    latitude: float
    longitude: float
    timestamp_ms: int
    accuracy_meters: float
```

**Acceptance:**
- [ ] All Pydantic models created
- [ ] Field validation rules added
- [ ] Example data in docstrings
- [ ] No circular imports

---

#### Wednesday: FFmpeg Integration (Backend Lead)
**Task:** Set up video processing service

**Deliverables:**
```python
# backend/app/services/video_processor.py

class VideoProcessor:
    def __init__(self, gcs_client, ffmpeg_path="/usr/bin/ffmpeg"):
        self.gcs = gcs_client
        self.ffmpeg = ffmpeg_path
        self.temp_dir = "/tmp/video_processing"
    
    def process_video(self, video_capture_id: int, gcs_path: str):
        """Main processing pipeline"""
        # 1. Download from GCS
        # 2. Compress with FFmpeg
        # 3. Extract keyframes
        # 4. Create proxy version
        # 5. Upload results
        # 6. Update DB
```

**Dependencies to install:**
```bash
pip install ffmpeg-python opencv-python
# or install ffmpeg system-wide
sudo apt-get install ffmpeg  # Ubuntu
brew install ffmpeg          # macOS
```

**Test locally:**
```bash
cd backend
python -c "from app.services.video_processor import VideoProcessor; print('✅ Import OK')"
ffmpeg -version  # Verify installation
```

**Acceptance:**
- [ ] FFmpeg successfully installed
- [ ] Python wrapper compiles without errors
- [ ] Can extract 1 frame from test video
- [ ] Compression produces smaller file

---

#### Thursday: Backend API Endpoints (Backend Lead)
**Task:** Create POST & GET video endpoints

**Deliverables:**
```python
# backend/app/routes/captures.py (add to existing file)

@router.post("/captures/{capture_id}/video", status_code=202)
async def upload_video(
    capture_id: int,
    video: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload video file for a capture session"""
    # Validate capture exists
    # Validate user has access
    # Save to temp storage
    # Upload to GCS
    # Create video_captures record
    # Enqueue processing job
    # Return 202 Accepted

@router.get("/captures/{capture_id}/video", response_model=VideoCaptureResponse)
async def get_video(
    capture_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve video URL + metadata"""
    # Get video_captures record
    # Generate signed GCS URL
    # Return metadata + URL
```

**Testing:**
```bash
curl -X POST http://localhost:8000/api/captures/1/video \
  -H "Authorization: Bearer $TOKEN" \
  -F "video=@test.mp4" \
  -F "fps=2" \
  -F "duration=300"
```

**Acceptance:**
- [ ] Endpoint returns 202 Accepted
- [ ] Video file saved to GCS
- [ ] database record created
- [ ] Proper error handling (missing file, wrong user)

---

#### Friday: Async Job Queue Setup (DevOps + Backend)
**Task:** Set up Celery + Redis for background processing

**Deliverables:**
```python
# backend/app/tasks.py

from celery import shared_task
from app.services.video_processor import VideoProcessor

@shared_task(bind=True, max_retries=3)
def process_video_task(self, video_capture_id: int, gcs_path: str):
    """Background task: process video, extract keyframes, upload"""
    try:
        processor = VideoProcessor(...)
        result = processor.process_video(video_capture_id, gcs_path)
        
        # Update DB with results
        # Send notification to user
        return {"status": "completed", "result": result}
    
    except Exception as exc:
        # Retry with exponential backoff
        self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

**Infrastructure:**
```bash
# Install & start Redis
docker run -d -p 6379:6379 redis:latest

# Start Celery worker
celery -A app.tasks worker --loglevel=info -c 4
```

**Acceptance:**
- [ ] Redis server running
- [ ] Celery worker process started
- [ ] Task queue visible in Flower (monitoring UI)
- [ ] Sample task completes successfully

---

### Week 2: Video Processing & Testing (Mon Aug 26 - Fri Aug 30)

#### Monday-Tuesday: FFmpeg Processing Pipeline (Backend Lead)
**Task:** Build complete video processing service

**Implementation:**
```python
# backend/app/services/video_processor.py (complete version)

class VideoProcessor:
    def process_video(self, video_capture_id: int, gcs_source_path: str) -> dict:
        """
        Process video:
        1. Download from GCS → /tmp
        2. Compress (H.264, CRF 28)
        3. Extract keyframes (1/sec)
        4. Create proxy (720p, CRF 32)
        5. Upload all to GCS
        6. Update database
        """
        
        # Download
        local_video = self._download_from_gcs(gcs_source_path)
        
        # Compress
        compressed = self._compress_video(local_video)
        
        # Keyframes
        keyframes = self._extract_keyframes(local_video)
        
        # Proxy
        proxy = self._create_proxy_video(compressed)
        
        # Upload
        uploaded = self._upload_results(compressed, proxy, keyframes, video_capture_id)
        
        # Update DB
        self._update_database(video_capture_id, uploaded)
        
        return uploaded
    
    def _compress_video(self, input_path: str) -> str:
        output_path = f"{self.temp_dir}/compressed.mp4"
        subprocess.run([
            "ffmpeg", "-i", input_path,
            "-c:v", "libx264",
            "-crf", "28",      # Quality (0-51, lower=better)
            "-c:a", "aac",     # Audio codec
            "-b:a", "128k",    # Audio bitrate
            output_path
        ], check=True)
        return output_path
    
    def _extract_keyframes(self, video_path: str) -> list:
        """Extract 1 frame per second"""
        frame_template = f"{self.temp_dir}/frame-%03d.jpg"
        subprocess.run([
            "ffmpeg", "-i", video_path,
            "-vf", "fps=1",    # 1 frame per second
            frame_template
        ], check=True)
        
        frames = sorted(Path(self.temp_dir).glob("frame-*.jpg"))
        return [
            {"frame_number": i, "path": str(f), "timestamp_ms": i * 1000}
            for i, f in enumerate(frames)
        ]
```

**Testing:**
```bash
# Test with sample video (create 10-sec test video)
ffmpeg -f lavfi -i testsrc=duration=10:size=1920x1080:rate=2 \
       -f lavfi -i sine=frequency=1000:duration=10 test_video.mp4

# Test processor
python -c "
from app.services.video_processor import VideoProcessor
processor = VideoProcessor(gcs_client)
result = processor.process_video(1, 'gs://bucket/test.mp4')
print(f'Extracted {result['keyframe_count']} keyframes')
"
```

**Acceptance:**
- [ ] 10-sec video processes in <30 sec
- [ ] ~10 keyframes extracted (1 per sec)
- [ ] Compressed file 30-50% smaller
- [ ] Proxy file 720p, plays smoothly

---

#### Wednesday: Mobile Upload Service (Mobile Dev)
**Task:** Implement video upload in React Native app

**Deliverables:**
```typescript
// mobile/services/VideoUploadService.ts

class VideoUploadService {
  async uploadVideo(
    captureId: number,
    videoPath: string,
    fps: number = 2,
    duration: number = 300
  ): Promise<VideoUploadResponse> {
    const formData = new FormData();
    
    // Add video file
    formData.append('video', {
      uri: videoPath,
      type: 'video/mp4',
      name: `video_${captureId}.mp4`
    });
    
    // Add metadata
    formData.append('fps', fps.toString());
    formData.append('duration', duration.toString());
    
    // Upload with progress
    return fetch(
      `${API_URL}/captures/${captureId}/video`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${await getAuthToken()}`,
          // FormData sets Content-Type automatically
        },
        body: formData
      }
    ).then(async (response) => {
      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }
      return response.json();
    });
  }
}
```

**Integration with CaptureFlow:**
```typescript
// mobile/screens/CaptureScreen.tsx

const handleStopRecording = async () => {
  setRecording(false);
  
  // Get video path from camera
  const videoResult = await camera.stopRecording();
  
  // Show uploading UI
  setUploadStatus('uploading');
  setUploadProgress(0);
  
  try {
    // Upload video
    const result = await videoUploadService.uploadVideo(
      currentCaptureId,
      videoResult.uri,
      fps = 2,
      duration = calculateDuration()
    );
    
    // Success!
    setUploadStatus('success');
    showNotification('Capture uploaded! Processing will complete in ~10 minutes');
    
  } catch (error) {
    // Failure: queue for retry
    await offlineQueueService.queueVideoForUpload(
      currentCaptureId,
      videoResult.uri,
      { /* metadata */ }
    );
    setUploadStatus('queued');
    showNotification('No network. Video will upload when online.');
  }
};
```

**Acceptance:**
- [ ] Video file selected from device
- [ ] Upload progress visible (percentage)
- [ ] Success notification after upload
- [ ] Error handling (network failure, file too large)

---

#### Thursday: Frontend Upload UI (Frontend Dev)
**Task:** Build video upload component for web app

**Deliverables:**
```typescript
// frontend/components/VideoUploadModal.tsx

export const VideoUploadModal: React.FC<VideoUploadModalProps> = ({
  captureId,
  onSuccess,
  onClose
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate: MP4, max 500MB
      if (!file.type.startsWith('video/')) {
        setError('Please select a video file');
        return;
      }
      if (file.size > 500 * 1024 * 1024) {
        setError('File too large (max 500MB)');
        return;
      }
      setSelectedFile(file);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    
    setUploading(true);
    
    const formData = new FormData();
    formData.append('video', selectedFile);
    formData.append('fps', '2');
    formData.append('duration', '300');
    
    try {
      const response = await fetch(
        `/api/captures/${captureId}/video`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${await getAuthToken()}`
          },
          body: formData
        }
      );
      
      if (!response.ok) throw new Error('Upload failed');
      
      const result = await response.json();
      onSuccess(result);
      onClose();
      
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <Modal open={true} onClose={onClose}>
      <div className="p-6 max-w-md">
        <h2 className="text-xl font-bold mb-4">Upload Video</h2>
        
        <div className="mb-4 p-4 border-2 border-dashed rounded">
          <input
            type="file"
            accept="video/*"
            onChange={handleFileSelect}
            disabled={uploading}
          />
        </div>
        
        {selectedFile && (
          <p className="text-sm text-gray-600 mb-4">
            {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(1)}MB)
          </p>
        )}
        
        {uploading && (
          <div className="mb-4">
            <div className="w-full bg-gray-200 rounded h-2">
              <div
                className="bg-blue-500 h-2 rounded"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-sm text-gray-600 mt-2">{progress}% uploaded</p>
          </div>
        )}
        
        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
            {error}
          </div>
        )}
        
        <div className="flex justify-end gap-3">
          <button onClick={onClose} disabled={uploading}>
            Cancel
          </button>
          <button
            onClick={handleUpload}
            disabled={!selectedFile || uploading}
            className="bg-blue-500 text-white px-4 py-2 rounded"
          >
            {uploading ? 'Uploading...' : 'Upload'}
          </button>
        </div>
      </div>
    </Modal>
  );
};
```

**Acceptance:**
- [ ] File selection works
- [ ] Size validation (max 500MB)
- [ ] Progress bar visible
- [ ] Success/error messages
- [ ] Mobile-responsive

---

#### Friday: End-to-End Testing (QA + Team)
**Task:** Full integration test: upload → process → retrieve

**Test Scenario:**
```
1. Create capture session (capture_id = 123)
2. Select video file (test_video.mp4, 30MB)
3. Upload via web UI
4. Verify 202 Accepted response
5. Check GCS bucket (video uploaded)
6. Wait 5 minutes (processing)
7. Check database:
   - video_captures.processing_status = 'completed'
   - video_keyframes table has ~120 rows
8. GET /captures/123/video
   - Returns video_url (signed GCS URL)
   - Returns keyframes list
9. Open video in browser
   - Plays without buffering
   - 360° viewer shows all angles
```

**Test Data:**
```bash
# Create test video (30 sec, 2fps = 60 frames)
ffmpeg -f lavfi -i testsrc=duration=30:size=1920x1080:rate=2 \
       -f lavfi -i sine=frequency=1000:duration=30 \
       -c:v libx264 -crf 23 \
       -c:a aac -b:a 128k \
       test_video_30sec.mp4

# File size check
ls -lh test_video_30sec.mp4  # Should be ~30-50MB
```

**Acceptance Criteria:**
- [ ] Upload completes in <5 minutes
- [ ] Processing finishes in <10 minutes
- [ ] No data loss (video retrievable)
- [ ] Keyframes count reasonable (~60 for 30sec)
- [ ] Zero errors in logs
- [ ] Video plays in browser

---

### Week 3: Mobile + Production Hardening (Mon Sep 2 - Fri Sep 6)

#### Monday-Tuesday: Mobile Camera Integration (Mobile Dev)
**Task:** Connect mobile camera to upload flow

**Implementation:**
```typescript
// mobile/services/CameraService.ts

import { RNCamera } from 'react-native-camera';

export class CameraService {
  private cameraRef: RNCamera | null = null;
  private recordingStartTime: number = 0;
  
  async startRecording(): Promise<void> {
    if (!this.cameraRef) return;
    
    this.recordingStartTime = Date.now();
    
    try {
      await this.cameraRef.recordAsync({
        quality: RNCamera.Constants.VideoQuality['720p'],
        orientation: 'portrait',
        mute: false,  // Capture audio
        maxDuration: 1800  // 30 minutes max
      });
    } catch (error) {
      console.error('Recording failed:', error);
      throw error;
    }
  }
  
  async stopRecording(): Promise<{ uri: string; duration: number }> {
    if (!this.cameraRef) return { uri: '', duration: 0 };
    
    const duration = (Date.now() - this.recordingStartTime) / 1000;
    this.cameraRef.stopRecording();
    
    return {
      uri: (await this.cameraRef.recordAsync({ maxDuration: 1800 })).uri,
      duration: Math.floor(duration)
    };
  }
}
```

**Acceptance:**
- [ ] Camera preview shows live feed
- [ ] Record button captures video
- [ ] Video saved to device storage
- [ ] Duration calculated correctly

---

#### Wednesday-Thursday: Error Handling & Retry (Backend + Mobile)
**Task:** Robust error handling for failed uploads/processing

**Backend Error Handling:**
```python
# backend/app/routes/captures.py

@router.post("/captures/{capture_id}/video")
async def upload_video(...):
    try:
        # Validate file
        if video.size > 500 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="File too large (max 500MB)"
            )
        
        if video.content_type not in ["video/mp4", "video/quicktime"]:
            raise HTTPException(
                status_code=415,
                detail="Unsupported format. Use MP4."
            )
        
        # Upload to GCS
        gcs_path = await storage_service.upload_video(video)
        
        # Create DB record
        video_capture = VideoCapture(...)
        db.add(video_capture)
        db.commit()
        
        # Enqueue async job
        process_video_task.apply_async(
            args=[video_capture.id, gcs_path],
            retry=True,
            retry_policy={
                'max_retries': 3,
                'interval_start': 1,
                'interval_step': 0.2,
                'interval_max': 60
            }
        )
        
        return {
            "video_capture_id": video_capture.id,
            "status": "pending",
            "message": "Video queued for processing. You'll be notified when ready."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")
```

**Mobile Retry Logic:**
```typescript
// mobile/services/VideoUploadService.ts

async uploadWithRetry(
  captureId: number,
  videoPath: string,
  maxRetries: number = 3
): Promise<void> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      await this.uploadVideo(captureId, videoPath);
      return; // Success!
    } catch (error) {
      if (attempt === maxRetries) {
        // Final attempt failed, queue for later
        await offlineQueueService.queueVideoForUpload(
          captureId,
          videoPath
        );
        throw new Error('Upload failed. Queued for later.');
      }
      
      // Exponential backoff
      const delay = Math.pow(2, attempt - 1) * 1000;
      await sleep(delay);
    }
  }
}
```

**Acceptance:**
- [ ] Invalid video rejected with clear error message
- [ ] Network failure triggers retry (3x)
- [ ] Failed uploads queued locally
- [ ] Sync when network returns

---

#### Friday: Security Hardening & Documentation (All)
**Task:** Finalize Phase 1, prepare for launch

**Security Checklist:**
- [ ] API rate limiting (100 req/min per user)
- [ ] Video file validation (not malicious)
- [ ] GCS signed URLs expire (1 hour)
- [ ] User authorization (only access own videos)
- [ ] HTTPS enforced (no HTTP)
- [ ] CORS properly configured

**Security Implementation:**
```python
# backend/app/middleware.py

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Apply to upload endpoint
@app.post("/captures/{id}/video")
@limiter.limit("100/minute")
async def upload_video(...):
    # User can upload max 100 videos per minute
    ...
```

**Documentation:**
- [ ] README updated with video feature
- [ ] API documentation (Swagger)
- [ ] User guide (how to upload video)
- [ ] Troubleshooting guide
- [ ] Performance tuning guide

**Deployment Checklist:**
- [ ] All tests pass (unit + integration)
- [ ] No critical bugs
- [ ] Performance benchmarks met
- [ ] Cost estimates realistic
- [ ] Monitoring/alerting configured
- [ ] Rollback plan ready

---

## Database Schema (SQL)

### Complete DDL

```sql
-- Video Capture Sessions
CREATE TABLE video_captures (
    id SERIAL PRIMARY KEY,
    capture_session_id BIGINT NOT NULL REFERENCES capture_sessions(id) ON DELETE CASCADE,
    
    -- File Paths
    video_file_path VARCHAR(512) NOT NULL,  -- GCS path
    proxy_video_path VARCHAR(512),          -- Lower bitrate version
    
    -- Metadata
    duration_seconds FLOAT,
    fps INTEGER DEFAULT 2,
    resolution_width INTEGER,
    resolution_height INTEGER,
    codec VARCHAR(32) DEFAULT 'h264',
    bitrate_kbps INTEGER,
    file_size_mb FLOAT,
    proxy_file_size_mb FLOAT,
    
    -- Processing Status
    processing_status VARCHAR(32) DEFAULT 'pending',  -- pending, processing, completed, failed
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    processing_error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(capture_session_id),
    INDEX idx_processing_status (processing_status),
    INDEX idx_created_at (created_at DESC)
);

-- Camera Movement Paths (Polyline Encoded)
CREATE TABLE camera_paths (
    id SERIAL PRIMARY KEY,
    video_capture_id BIGINT NOT NULL UNIQUE REFERENCES video_captures(id) ON DELETE CASCADE,
    
    -- Encoded Path
    polyline_encoded TEXT,                  -- Google polyline format (compact)
    geojson_path JSONB,                     -- GeoJSON LineString (for queries)
    waypoint_count INTEGER,
    total_distance_meters FLOAT,
    
    -- Tracking Metadata
    tracking_method VARCHAR(32),            -- 'gps', 'imu', 'manual', 'hybrid'
    gps_accuracy_meters FLOAT,
    
    -- Temporal Alignment
    start_timestamp BIGINT,                 -- Unix ms
    end_timestamp BIGINT,
    
    -- Geospatial Bounds (for fast queries)
    min_latitude FLOAT,
    max_latitude FLOAT,
    min_longitude FLOAT,
    max_longitude FLOAT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_video_capture_id (video_capture_id)
);

-- Individual Path Waypoints
CREATE TABLE path_waypoints (
    id SERIAL PRIMARY KEY,
    camera_path_id BIGINT NOT NULL REFERENCES camera_paths(id) ON DELETE CASCADE,
    
    -- Position
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    elevation_meters FLOAT,
    
    -- Timing
    timestamp_ms BIGINT NOT NULL,           -- Relative to capture start
    video_frame_number INTEGER,
    
    -- Quality
    accuracy_meters FLOAT,                  -- GPS accuracy
    
    -- Order
    sequence_index INTEGER,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(camera_path_id, sequence_index),
    INDEX idx_timestamp (timestamp_ms),
    INDEX idx_sequence (sequence_index)
);

-- Extracted Video Keyframes
CREATE TABLE video_keyframes (
    id SERIAL PRIMARY KEY,
    video_capture_id BIGINT NOT NULL REFERENCES video_captures(id) ON DELETE CASCADE,
    
    -- Frame Data
    frame_number INTEGER NOT NULL,
    timestamp_ms BIGINT NOT NULL,           -- From video start
    keyframe_image_path VARCHAR(512),       -- GCS path to JPG
    thumbnail_path VARCHAR(512),            -- Smaller thumbnail
    
    -- Associated Path Point (if available)
    latitude FLOAT,
    longitude FLOAT,
    associated_waypoint_id BIGINT REFERENCES path_waypoints(id),
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(video_capture_id, frame_number),
    INDEX idx_timestamp (timestamp_ms),
    INDEX idx_waypoint (associated_waypoint_id)
);

-- Start Point Pins on Floor Plans
CREATE TABLE start_point_pins (
    id SERIAL PRIMARY KEY,
    video_capture_id BIGINT NOT NULL UNIQUE REFERENCES video_captures(id) ON DELETE CASCADE,
    floor_plan_id BIGINT NOT NULL REFERENCES floor_plans(id),
    
    -- Position on Floor Plan Image
    pixel_x FLOAT NOT NULL,
    pixel_y FLOAT NOT NULL,
    
    -- Geographic Reference (optional)
    latitude FLOAT,
    longitude FLOAT,
    
    -- Metadata
    pin_label VARCHAR(256),
    notes TEXT,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    created_by BIGINT REFERENCES users(id),
    
    INDEX idx_floor_plan (floor_plan_id),
    INDEX idx_created_at (created_at DESC)
);

-- Create Alembic Migration
-- File: backend/alembic/versions/xxxxx_add_video_capture_schema.py
```

---

## API Specifications

### Endpoint 1: POST /api/v1/captures/{capture_id}/video

**Description:** Upload video file for a capture session

**Request:**
```http
POST /api/v1/captures/123/video HTTP/1.1
Authorization: Bearer eyJhbGc...
Content-Type: multipart/form-data

video: <binary video file>
fps: 2
duration: 300
```

**Response (202 Accepted):**
```json
{
  "video_capture_id": 456,
  "status": "pending",
  "processing_started_at": "2026-09-06T10:30:00Z",
  "estimated_completion_time": "2026-09-06T10:40:00Z",
  "message": "Video queued for processing"
}
```

**Error Responses:**
```json
// 413 Payload Too Large
{ "detail": "File too large (max 500MB)" }

// 415 Unsupported Media Type
{ "detail": "Unsupported format. Use MP4." }

// 401 Unauthorized
{ "detail": "Invalid or expired token" }

// 404 Not Found
{ "detail": "Capture not found" }
```

### Endpoint 2: GET /api/v1/captures/{capture_id}/video

**Description:** Retrieve video details and playback URL

**Request:**
```http
GET /api/v1/captures/123/video HTTP/1.1
Authorization: Bearer eyJhbGc...
```

**Response (200 OK):**
```json
{
  "video_capture_id": 456,
  "video_url": "https://storage.googleapis.com/bucket/video.mp4?X-Goog-Signature=...",
  "proxy_video_url": "https://storage.googleapis.com/bucket/video-proxy.mp4?...",
  "duration_seconds": 300,
  "resolution": "1920x1080",
  "codec": "h264",
  "processing_status": "completed",
  "keyframes_count": 300,
  "keyframes": [
    { "frame_number": 0, "timestamp_ms": 0, "keyframe_image_url": "..." },
    ...
  ],
  "camera_path": {
    "waypoint_count": 600,
    "total_distance_meters": 250,
    "polyline_encoded": "qmweFtrqVp@m@..."
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

---

## Code Examples

### Backend: Complete Upload Handler

See code examples sections above for full implementations.

### Frontend: React Component

See code examples sections above.

### Mobile: React Native Upload

See code examples sections above.

---

## Testing Strategy

### Unit Tests

```python
# tests/test_video_processor.py

def test_compress_video():
    processor = VideoProcessor(gcs_client)
    result = processor._compress_video("test.mp4")
    assert Path(result).exists()
    assert os.path.getsize(result) < os.path.getsize("test.mp4")

def test_extract_keyframes():
    processor = VideoProcessor(gcs_client)
    frames = processor._extract_keyframes("test_30sec.mp4")
    assert len(frames) == 30  # 1 per second
```

### Integration Tests

```python
# tests/test_video_upload_flow.py

def test_end_to_end_video_upload():
    # 1. Upload video
    response = client.post(
        f"/captures/1/video",
        files={"video": open("test.mp4", "rb")},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 202
    video_id = response.json()["video_capture_id"]
    
    # 2. Wait for processing (in test, mock with immediate completion)
    time.sleep(5)  # In prod, wait ~10 min
    
    # 3. Retrieve video
    response = client.get(
        f"/captures/1/video",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["video_url"]
    assert data["keyframes_count"] > 0
```

---

## Deployment Checklist

### Pre-Launch
- [ ] All database migrations tested
- [ ] API endpoints tested with real video files
- [ ] FFmpeg worker pool operational
- [ ] GCS bucket configured + signed URLs working
- [ ] Error logging + monitoring setup
- [ ] Rate limiting configured
- [ ] Security audit passed

### Launch Day
- [ ] Deploy backend to Cloud Run
- [ ] Deploy frontend (React build)
- [ ] Release mobile app (iOS + Android)
- [ ] Monitor error rates (<1%)
- [ ] Verify video processing latency (<15 min)
- [ ] Announce to beta testers

### Post-Launch (Week 1)
- [ ] Monitor infrastructure costs
- [ ] Collect user feedback
- [ ] Fix any critical bugs
- [ ] Prepare Phase 2 (path tracking)

---

**Status:** ✅ Ready for Execution  
**Kickoff Date:** Monday, August 19, 2026  
**Target Launch:** Friday, September 6, 2026  
**Team:** 3 developers + 1 DevOps + 1 QA
