# Space360 Insta360 X4 Module v1.1.0 Chat Summary (2026-09-19)

### 1. Project Status (Current State)
- **Module v1.1.0:** LIVE on Cloud Run
- **Production URL:** https://insta360-module-1046334946412.asia-southeast1.run.app
- **All phases complete:** P1, P2, P3
- **Test scorecard:** 65/65 passing (40 module, 17 backend, 4 frontend + 4 integration approx)

### 2. Architecture Decisions (Frozen)
- HTTP-only module boundary (no direct imports)
- FFmpeg as permanent fallback (MediaSDK optional)
- multiprocessing.Process for MediaSDK isolation
- python:3.13-slim Linux container (pivoted from Windows)
- max-instances=1 (job state safety)
- h264 codec (web-safe for Pannellum)
- Firebase JWT auth (all endpoints)
- GCS bucket: 360-field-check-media-sgb (asia-southeast1)
- Sidecar JSON schema v1.0 (locked)

### 3. File Locations
- Module: F:\Space360\modules\insta360\
- Backend: F:\Space360\backend\
- Frontend: F:\Space360\dashboard\
- Docs: F:\Space360\docs\
- AG Prompts: F:\Space360\docs\ag-prompts\
- Master Roadmap: F:\Space360\docs\SPACE360_MASTER_ROADMAP_v1_0.md
- Deployment Record: F:\Space360\modules\insta360\DEPLOYMENT_RECORD.md
- Sample Video: F:\insta360 sample video\

### 4. What Was Built (v1.1.0 Changes)
- PyBind11 wrapper for Insta360 MediaSDK (stitcher_bind.cp313-win_amd64.pyd)
- Hybrid stitching engine (MediaSDK subprocess → FFmpeg fallback)
- Dual-lens auto-detection (is_dual_lens())
- 3 backend HTTP endpoints (/ingest, /status, /videos)
- Videos table + VideoRepository + VideoIngestService + VideoStatusPoller
- UploadVideoPage + VideoJobPoller + VideoGallery + PannellumViewer
- JSON structured logging (Cloud Logging compatible)
- Windows → Linux container pivot (python:3.13-slim)
- Cloud Run deployment (asia-southeast1)
- GCS lifecycle rules (90-day TTL)
- CORS policy for Pannellum video access

### 5. Known Issues & Limitations
- MediaSDK crashes on all real videos (0xC0000005) — FFmpeg handles production
- Job state in-memory + file (not Firestore yet) — max-instances=1 required
- Cold start ~10-15s (Linux container, acceptable)
- No upload size limit explicitly set (monitor for large .insv files)
- Pannellum equirectangular output: verify manually after first real upload

### 6. Next Session Priorities (v2 Roadmap)
- Priority 1 (High): Firestore job state migration (removes max-instances=1 constraint)
- Priority 2 (High): GCS signed URLs for large file uploads
- Priority 3 (Medium): Cloud Monitoring alerts (error rate, latency, memory)
- Priority 4 (Medium): MediaSDK investigation (contact Insta360 support)
- Priority 5 (Low): Circuit breaker for MediaSDK (auto-disable after N crashes)
- Priority 6 (Low): GPU h264_nvenc (if NVIDIA driver upgrade approved)

### 7. Open Questions for Next Session
- Q1: Did Pannellum display equirectangular correctly after first real upload?
- Q2: What is actual cold start time in production?
- Q3: Any unexpected errors in first 48 hours of Cloud Logging?
- Q4: Is max-instances=1 causing any bottleneck (queue backlog)?
- Q5: Ready to start Firestore migration for v2?

### 8. Environment & Credentials Reference
- GCP Project ID: space360-114433
- Cloud Run URL: https://insta360-module-1046334946412.asia-southeast1.run.app
- GCS Bucket: 360-field-check-media-sgb
- Region: asia-southeast1
- Service Account: insta360-sa@space360-114433.iam.gserviceaccount.com
- Container Registry: asia-southeast1-docker.pkg.dev
- Python version: 3.13
- MediaSDK version: v3.1.5

### 9. How to Start Next Session
Paste this summary into a new Claude chat and say:
"I'm continuing Space360 v2 development. Here's the current state: [paste summary]"
Then answer any open questions (Section 7) and Claude will generate AG prompts for v2 priorities.
