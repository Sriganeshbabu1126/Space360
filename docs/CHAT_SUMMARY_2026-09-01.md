# Chat Summary — September 1, 2026
## Space360 Insta360 X4 Video Handling Module — Planning Session

---

## Project Context

**Space360** is a 360° field inspection platform for construction and site management.

**This Chat Scope:**  
Planning the **Insta360 X4 Video Handling Module** — a standalone component that will integrate into Space360's Stage 3 pipeline.

- **Module Status:** v1.0.0 production-ready (FFmpeg-based, 15 tests passing)
- **Current Environment:** Windows local dev (F:\Space360\modules\insta360\)
- **Next Phase:** v1.1.0 (MediaSDK integration) → Space360 backend integration → infrastructure hardening
- **Key Constraint:** Module runs as standalone; Space360 backend consumes it via HTTP only (no direct Python import)

---

## Key Decisions (Frozen)

### Architecture & Integration
- **Module Boundary:** HTTP-only consumption by Space360 backend (no direct Python import)
- **Stitching Engine v1.0:** FFmpeg (permanent fallback for all scenarios)
- **Stitching Engine v1.1:** Insta360 Native MediaSDK via PyBind11 (C++ native binding)
- **Fallback Logic:** Try MediaSDK → silent import failure → use FFmpeg (graceful degradation)
- **Codec Strategy:** libx264 ← libx265 probe (if file ≤200MB); force libx264 if >200MB
- **GPU Encoding:** Permanently disabled (NVIDIA driver incompatible; unlock via driver upgrade in P3)
- **Thread Logging:** File-based subprocess logs (no pyexiftool; native subprocess.run only)

### API Contract (Frozen)
- **No Breaking Changes** to existing endpoints (GET /health, POST /ingest, GET /jobs/{job_id}, etc.)
- **Sidecar JSON Schema:** v1.0 frozen; any changes require versioning
- **Storage Bucket:** 360-field-check-media-sgb (GCS, asia-southeast1)

### Build Strategy
- **P1 First:** MediaSDK integration (SDK build + PyBind11 wrapper + hybrid routing)
- **P2 Second:** Space360 backend endpoints + DB schema + frontend wiring
- **P3 Parallel:** GPU driver upgrade + Cloud Run containerization + JSON logging

---

## Current Status

### ✅ Completed
- v1.0.0 production deployment (FFmpeg, 15 tests passing, all pipelines working)
- 6-step async pipeline fully operational (detect → validate → transfer → extract → stitch → upload)
- API endpoints live (health, ingest, jobs, schema)
- Environment variables and path handling hardcoded (absolute paths, no PATH env issues)
- Codec fallback logic validated (libx264/libx265 probe, GPU disabled, >200MB files forced to libx264)
- Known v1.0.0 issues resolved (subprocess failures, exiftool hanging, thread PATH drops, NVENC GPU issues)
- Space360 master roadmap reviewed (full project context acquired)

### 🔄 In Progress
- **Planning phase:** Detailed agenda drafted covering P1/P2/P3 breakdown, risks, test strategy, success criteria
- **Awaiting blocker answers:** 6 open questions submitted to human (Q1–Q6 below)
- **Ready for:** AG prompt generation (pending blocker answers)

### ⏸️ Blocked
- **AG Prompt Generation** blocked on answers to 6 blocker questions:
  - Q1: Visual Studio Build Tools installed?
  - Q2: Insta360 SDK verified to compile on this machine?
  - Q3: Pre-built MediaSDK .dll available?
  - Q4: GPU driver upgrade planned or blocked?
  - Q5: Cloud Run deployment in scope for next sprint?
  - Q6: When does Space360 backend team need HTTP consumption ready?

### 🧪 Tested & Verified
- v1.0.0 production running locally (Uvicorn, http://localhost:8000)
- 15 unit tests passing (metadata + stitcher)
- FFmpeg codec detection and fallback working
- exiftool metadata extraction working
- GCS upload pipeline validated
- Job tracking (in-memory + file persistence) working

---

## Next Steps (Priority Order)

### Phase 1: MediaSDK Integration (v1.1.0) — 2–3 weeks
**Blockers:** Q1, Q2, Q3

1. **Build native .dll** from Desktop-MediaSDK-Cpp (Visual Studio Build Tools)
2. **Implement PyBind11 wrapper** (`stitcher_bind.cpp`) — C++ → Python interface
3. **Build & test .pyd** (Python native module) — import validation
4. **Update `core/stitcher.py`** with hybrid routing (MediaSDK + FFmpeg fallback)
5. **Implement dual-lens detection** → route to correct engine automatically
6. **Regression testing:** all 15 existing tests must pass unchanged
7. **Performance benchmark:** MediaSDK ≥15% faster than FFmpeg (or acceptable trade-off)

### Phase 2: Space360 Backend Integration — 1–2 weeks
**Blocker:** Q6 (timing)

1. **Add 3 new endpoints:**
   - `POST /api/videos/ingest` — trigger module, receive job_id
   - `GET /api/videos/{job_id}/status` — poll job status + GCS URIs
   - `GET /api/videos` — list site videos

2. **Add DB schema:**
   - `videos` table (id, site_id, user_id, job_id, status, gcs_mp4_uri, gcs_metadata_uri, capture_timestamp, error_message)
   - Indexes on site_id, status, job_id

3. **Add service layer:**
   - `VideoIngestService` — POST to module, store job_id
   - `VideoStatusPoller` — poll module status on interval, update DB
   - `VideoRepository` — CRUD + role-based filtering

4. **Add frontend wiring:**
   - `UploadVideoPage` — file picker → trigger ingest → store job_id
   - `VideoJobPoller` — useEffect polling `/api/videos/{job_id}/status`
   - `VideoGallery` — display videos + lazy-load Pannellum viewer
   - Path overlay wiring (when Stage 3 #82–#83 ready)

### Phase 3: Infrastructure Hardening — 1 week (parallel)
**Blockers:** Q4, Q5

1. **GPU driver upgrade** (if approved) — unlock h264_nvenc (80% faster stitching)
2. **Cloud Run Dockerization** (if in-scope) — wrap module for Cloud Run deployment
3. **Logging migration** — file-based → structured JSON → Cloud Logging
4. **GCS lifecycle rules** — TTL on videos/ prefix

---

## Open Questions for Human (Genuine Blockers)

### MediaSDK Build (P1)
**Q1:** Is Visual Studio Build Tools installed on `F:\` machine?
- Required to compile Desktop-MediaSDK-Cpp `.dll`
- If NO: Do we install it, or use pre-built SDK binary?

**Q2:** Has the Insta360 SDK been verified to compile on this machine?
- Try: navigate to `F:\Insta360_SDK\Desktop-MediaSDK-Cpp` → run build script
- If it fails, what's the error? (Links? Dependencies? MSVC version?)

**Q3:** Do you have a pre-built MediaSDK `.dll`?
- If YES: location/path? (Skips compilation step)
- If NO: confirmed we build from source?

### Infrastructure (P3)
**Q4:** GPU driver upgrade — planned or blocked?
- Current: NVIDIA GPU disabled due to driver incompatibility
- Benefit: h264_nvenc unlocked (80% faster stitching)
- Decision: Upgrade now, or accept FFmpeg as final fallback?

**Q5:** Cloud Run deployment — in scope for next sprint?
- Affects whether AG should build with Docker mindset now (env vars, logging structure)
- If YES: include Dockerfile in v1.1.0, or defer to separate sprint?

### Integration Timeline (P2)
**Q6:** When does Space360 backend team want HTTP consumption ready?
- Affects P2 priority relative to P1
- Can backend test with module running locally first, or do they need production-ready immediately?

---

## Tech Stack Summary

### Insta360 Module (Current v1.0.0)
- **Language:** Python 3.13
- **Framework:** FastAPI + Uvicorn
- **Video Processing:** FFmpeg N-126264, exiftool v13.59
- **Native SDK:** Insta360 Desktop MediaSDK (F:\Insta360_SDK, not yet integrated)
- **Storage:** Google Cloud Storage SDK
- **Job Tracking:** In-memory + file persistence
- **Testing:** pytest (15 tests passing)
- **Deployment:** Local Windows dev (future: Cloud Run)

### Space360 Backend (Context)
- **Backend:** Python 3.13 + FastAPI + SQLAlchemy
- **Database:** PostgreSQL 16
- **Auth:** Firebase JWT Bearer
- **Storage:** Google Cloud Storage
- **GCP Region:** asia-southeast1

### Frontend (Context)
- **Framework:** React 18 + TypeScript
- **360° Viewer:** Pannellum.js
- **Styling:** Tailwind CSS v3.4.1
- **Components:** lucide-react, recharts

---

## Files/Folders Referenced This Session
- `F:\Space360\modules\insta360\api\main.py` — FastAPI app entry
- `F:\Space360\modules\insta360\core\stitcher.py` — Encoding logic (to be updated with MediaSDK)
- `F:\Space360\modules\insta360\core\metadata.py` — Sidecar JSON generation
- `F:\Space360\modules\insta360\core\uploader.py` — GCS upload pipeline
- `F:\Space360\modules\insta360\tests\` — 15 passing tests
- `F:\Insta360_SDK\Desktop-MediaSDK-Cpp\` — SDK source (for v1.1.0 build)
- `F:\Space360\docs\SPACE360_MASTER_ROADMAP_v1_0.md` — Master project reference
- `F:\Space360\backend\` — Space360 FastAPI backend (for P2 integration)
- `F:\Space360\frontend\` — React frontend (for P2 wiring)

---

## Known Issues & Gotchas

| # | Issue | Status | Mitigation |
|---|---|---|---|
| 1 | MediaSDK build may fail if VS Build Tools missing or SDK incompatible | Active | Pre-flight validation; have FFmpeg fallback confirmed working |
| 2 | PyBind11 DLL linking can fail on Windows (MSVC runtime conflicts) | Medium risk | Static link if possible; otherwise document required MSVC version |
| 3 | Silent import failure of `stitcher_bind` must not crash app | Critical | Pattern already established: log warning, fall back to FFmpeg |
| 4 | Existing 15 tests must pass after v1.1.0 changes | Regression risk | All tests should pass unchanged; no API surface changes |
| 5 | Space360 backend HTTP contract must not change | Frozen constraint | Validate endpoints match integration contract before P2 |
| 6 | GCS URI storage in DB must match sidecar schema v1.0 | Data consistency | Verify schema match; no field renames or additions |
| 7 | Video specs for Stage 3 Phase 2 (mobile video capture) ON HOLD | Blocking mobile work | 8 unanswered questions; not affecting this module's work |

---

## Architecture Diagram (ASCII)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Space360 Backend                             │
├─────────────────────────────────────────────────────────────────┤
│  POST /api/videos/ingest  →  VideoIngestService                │
│  GET /api/videos/{job_id} →  VideoStatusPoller                │
│  GET /api/videos          →  VideoRepository                   │
└─────────────────┬──────────────────────────────────────────────┘
                  │ HTTP POST /ingest
                  │ HTTP GET /jobs/{job_id}
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│        Insta360 X4 Module (Standalone)                          │
├─────────────────────────────────────────────────────────────────┤
│  v1.1.0 (MediaSDK + FFmpeg)                                     │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 6-Step Pipeline                                            │ │
│  │  1. detect()      → Find .insv files (USB/SD)             │ │
│  │  2. validate()    → Validate batch                         │ │
│  │  3. transfer()    → Copy to output/YYYYMMDD/             │ │
│  │  4. extract()     → Metadata → _metadata.json            │ │
│  │  5. stitch()      → [HYBRID] MediaSDK OR FFmpeg          │ │
│  │       ├─ Dual-lens? → Try MediaSDK                       │ │
│  │       └─ Import fail or error? → FFmpeg                  │ │
│  │  6. upload()      → GCS MP4 + sidecar JSON              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Job Tracking:  In-memory + file persistence                   │
│  Codec Fallback: libx264 ← libx265 (if <200MB probe pass)     │
│  GPU:            Disabled (NVIDIA driver incompatible)         │
└─────────────────┬──────────────────────────────────────────────┘
                  │ Upload to GCS
                  ▼
        ┌─────────────────────┐
        │  GCS Bucket         │
        │ (360-field-check-   │
        │  media-sgb)         │
        │                     │
        │ /videos/            │
        │  ├─ {id}_stitched.  │
        │  │  mp4            │
        │  └─ {id}_metadata.  │
        │     json           │
        └─────────────────────┘
```

---

## Decision Log (This Session)

| Decision | Choice | Rationale | Status |
|---|---|---|---|
| Build order | P1 → P2 → P3 | P1 validates SDK/PyBind11 pipeline before P2 consumes; P3 independent infrastructure work | ✅ Approved |
| MediaSDK binding | PyBind11 (C++) | Native performance, GPU support, Insta360 proprietary codecs | ✅ Frozen |
| Fallback strategy | FFmpeg (permanent) | Production-tested, reliable fallback for any MediaSDK failure | ✅ Frozen |
| API contract | No breaking changes | Existing endpoints/schema frozen; new endpoints in P2 additive only | ✅ Frozen |
| Integration model | HTTP polling | Space360 backend polls /jobs/{job_id} until completion (no direct import) | ✅ Frozen |
| Test regression | 15 tests unchanged | All v1.0.0 tests must pass in v1.1.0 (zero tolerance) | ✅ Constraint |

---

## Context Continuity Notes

- **Module is production-ready** (v1.0.0 running live; safe to continue work)
- **No breaking changes expected** in v1.1.0 (additive MediaSDK support, fallback guaranteed)
- **All decisions validated** against Space360 integration contract (HTTP-only boundary)
- **Blocker answers critical** before AG prompt generation can proceed
- **Team onboarding:** This summary + answers to 6 Qs = sufficient context for new developer to jump in
- **Parallel workflow:** P1 can run independently; P2 begins after P1 stabilizes; P3 can start anytime

---

## Version / Chat Metadata
- **Chat Date:** September 1, 2026
- **Session Type:** Planning + Architecture
- **Messages:** ~8 (user brief + 2 documents provided; 1 planning agenda produced)
- **Deliverables:** Detailed planning agenda (P1/P2/P3 breakdown, risks, test strategy, 6 blocker Qs)
- **Next Session:** Answer 6 blocker Qs → receive detailed AG prompts (one at a time)
- **Summary Generated:** September 1, 2026 @ 12:00 UTC

---

**Ready for Migration.** 🚀

Next chat: Paste this summary, answer the 6 Qs, then receive AG prompts.
