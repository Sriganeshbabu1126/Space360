# Space360 — Comprehensive Master Roadmap
**Version:** v1.0
**Created:** August 21, 2026
**Purpose:** AI assistant handoff reference — self-contained context for any new chat session
**Maintained at:** `F:\Space360\docs\SPACE360_MASTER_ROADMAP_v1.0.md`

---

## How to Use This Document

This is the single source of truth for the Space360 project. When starting a new AI assistant chat:
1. Share this document at the start of the conversation
2. The assistant reads it to understand full project context
3. Reference specific sections as needed during development
4. Update this document when major decisions or completions occur

---

## 1. Project Overview

**Space360** is a 360° field inspection platform for construction and site management.

| Property | Value |
|---|---|
| Type | Web app + Mobile app + Standalone modules |
| Domain | Construction / Site inspection |
| Primary users | Admin, Manager, Contractor |
| GitHub | https://github.com/Sriganeshbabu1126/Space360 |
| Project root | `F:\Space360\` |
| Docs folder | `F:\Space360\docs\` |

---

## 2. Technology Stack

### Backend
| Component | Technology |
|---|---|
| Language | Python 3.13 |
| Framework | FastAPI + Uvicorn |
| ORM | SQLAlchemy + Alembic (migrations) |
| Database | PostgreSQL 16 |
| Storage | Google Cloud Storage (GCS) |
| Auth | Firebase Authentication |
| Task queue | Celery + Redis (added in Stage 2) |
| Search | PostgreSQL full-text search (GIN + tsvector) |

### Frontend (Web)
| Component | Technology |
|---|---|
| Framework | React 18 + TypeScript |
| Styling | Tailwind CSS v3.4.1 |
| Routing | React Router v7 |
| Charts | recharts |
| Icons | lucide-react |
| 360° viewer | Pannellum.js |
| Markup/annotation | Canvas API |
| Notifications | react-hot-toast |

### Mobile App (Stage 3 — in progress)
| Component | Technology |
|---|---|
| Framework | React Native + Expo (managed workflow) |
| Platforms | iOS + Android |
| Navigation | React Navigation v7 (native stack + bottom tabs) |
| State | Redux Toolkit + redux-persist |
| Auth | @react-native-firebase/auth |
| HTTP | Axios |
| Storage | AsyncStorage |
| Location | expo-location |
| Camera | expo-camera |

### Infrastructure
| Component | Value |
|---|---|
| Backend hosting | Google Cloud Run |
| Database hosting | Google Cloud SQL (PostgreSQL) |
| File storage | Google Cloud Storage |
| GCS bucket | `360-field-check-media-sgb` |
| Firebase project | `field-check-72967` |
| GCP region | `asia-southeast1` |
| Service account | `space360-backend@field-check-72967.iam.gserviceaccount.com` |
| CI/CD | GitHub Actions |

### Stage 3 Additions (planned)
- PostGIS (path/GPS data)
- Three.js (path navigation overlay)
- Deck.gl (geospatial rendering)
- Cloud Tasks + Redis (async job handling)
- FFmpeg / OpenCV (video processing — Insta360 module)

---

## 3. Repository & Local Development

| Item | Value |
|---|---|
| Project root | `F:\Space360\` |
| Backend | `F:\Space360\backend\` |
| Frontend | `F:\Space360\frontend\` |
| Mobile app | `F:\Space360\mobile\` |
| Insta360 module | `F:\Space360\modules\insta360\` |
| Docs | `F:\Space360\docs\` |
| Start script | `F:\Space360\START-SPACE360.bat` |
| Backend port | 8000 |
| Frontend port | 3000 |
| Roadmap docs | `F:\Space360\docs\` (8+ docs, 200+ pages) |

---

## 4. User Roles

| Role | Permissions |
|---|---|
| Admin | Full access — all sites, all users, all data |
| Manager | Site-scoped access — manage issues, contractors, reports |
| Contractor | Restricted — only assigned sites, limited field visibility |

---

## 5. Development Workflow

| Role | Responsibility |
|---|---|
| AG (Antigravity IDE) | Autonomous developer — executes prompts, writes all code |
| Human (You) | Strategic decisions, prompt authoring, testing, review |
| AI Assistant (Claude) | Consultant — drafts AG prompts, reviews plans, answers questions |

**Process:** Plan → draft AG prompt → human sends to AG → AG implements → human tests → review → next prompt

**Principles:**
- Quality over speed — no artificial deadlines
- Complete one feature → test → mark done → next prompt
- Stage 1 must remain 100% backward compatible through all changes
- AG context drifts in long sessions — reset with explicit state messages when needed

---

## 6. Overall Progress

| Stage | Name | Status | Completion |
|---|---|---|---|
| Stage 1 | Core Platform | ✅ Complete | 100% |
| Stage 2 | Advanced Features | ✅ Complete | 100% |
| Stage 3 | Path Tracking + Mobile + Video | 🔄 In Progress | ~10% |
| Insta360 Module | Standalone video handling | 🎯 Planning | 0% |

---

## 7. Stage 1 — Core Platform ✅ COMPLETE

**Do not revisit or modify Stage 1 features.** All are production-ready and backward compatibility must be preserved.

Features shipped:
- Issue tracking (create, update, assign, close)
- Evidence photo upload and management
- Markup / annotation tools (Canvas API)
- Push notifications system
- Dashboard with summary metrics
- Bulk actions on issues
- Mobile-responsive web UI
- Multi-role access control (Admin / Manager / Contractor)
- Firebase Authentication integration
- GCS file upload/download
- 2000+ lines of stable, tested code
- Ready for Cloud Run deployment

---

## 8. Stage 2 — Advanced Features ✅ COMPLETE

All features shipped and tested.

| Feature | ID | Status | Notes |
|---|---|---|---|
| Project Hub | #76 | ✅ Complete | Multi-project management |
| Multi-Site Contractors | #77 | ✅ Complete | Contractors assigned across sites |
| Frame Sequence Capture | #78 | ✅ Complete | Sequential 360° photo capture |
| Advanced Filtering & Search | #79 | ✅ Complete | B-Tree + GIN indexes, tsvector full-text |
| Column Sort Fix | #79.1 | ✅ Complete | Tri-state sort on Issues page |
| Data Export | #80 | ✅ Complete | CSV / Excel / PDF, streaming + async |

### Key Stage 2 Implementation Details

**#79 — Advanced Filtering & Search**
- Database: Alembic migration — B-Tree indexes on `issues`, `issue_comments`, `issue_assignments`; GIN indexes with `to_tsvector` for full-text search on titles, descriptions, comments
- Backend: `IssueFilterQuery` service — dynamic filter criteria, tsvector matching, safe relationship loading (no N+1)
- API: `/search` endpoint in `issues.py` — contractor-scoped (contractors see assigned sites only)
- Frontend: `AdvancedFilterPanel` + `FilterPresetManager` (presets stored in localStorage)
- Dashboard: `IssuesPage.tsx` refactored with collapsible advanced filter UI

**#79.1 — Column Sort**
- Tri-state: click = asc → click = desc → click = reset
- Sort indicator icon (↑/↓) next to active column
- State: `sortColumn`, `sortDirection` in React state
- Params: `?sort_by=created_at&sort_dir=asc` passed to `/search`
- Sortable: Title, Status, Priority, Created Date, Updated Date, Assignee
- Works simultaneously with active filters and search

**#80 — Data Export**
- `export_service.py` — CSV, Excel (openpyxl), PDF (reportlab) generation
- Role-based fields: Admin/Manager = all fields; Contractor = limited fields
- Small exports (≤500 issues): streaming response, direct browser download
- Large exports (>500 issues): Celery background job → GCS → in-app notification with signed URL (1hr expiry)
- Endpoints: `POST /issues/export` + `GET /issues/export/{job_id}`
- Frontend: export button, format dropdown, loading spinner, async polling, toast notification
- GCS path: `360-field-check-media-sgb/exports/{user_id}/{job_id}.{ext}`
- Default filename: `space360_issues_{YYYY-MM-DD}.{ext}`
- Dependencies added: `openpyxl`, `reportlab`, `celery`, `redis`
- Celery worker start (Windows): `celery -A app.celery_app worker --loglevel=info -P threads`

---

## 9. Stage 3 — Path Tracking + Mobile + Video 🔄 IN PROGRESS

### 9.1 Feature Tracker

| Feature | ID | Status | Blocking? |
|---|---|---|---|
| Mobile App Foundation | #81 | 🔄 In Progress (AG working) | No |
| Path Tracking (GPS/IMU + PostGIS) | #82 | 🎯 Planned | No |
| Path Navigation (Three.js overlay) | #83 | 🎯 Planned | Needs #82 |
| Video Capture (Insta360 X4) | #84 | ⏸️ On Hold | Yes — see video spec questions |
| Mobile: Issue Viewer | #85 | 🎯 Planned | Needs #81 |
| Mobile: Path Capture | #86 | 🎯 Planned | Needs #81 + #82 |

### 9.2 Feature #81 — Mobile App Foundation

**Status:** 🔄 In Progress (AG implementing)

**Scope delivered by AG:**
- Expo managed workflow, TypeScript strict mode
- Location: `F:\Space360\mobile\`
- Bottom tab navigation: Dashboard, Issues, Capture (placeholder), Profile
- Firebase Auth (email/password) — token persisted via redux-persist + AsyncStorage
- Redux store: `authSlice` + `appSlice`
- Axios client with Firebase token interceptor + auto-logout on 401
- Auth guard: unauthenticated → LoginScreen
- Brand color: `#1D9E75` (teal)

**Success criteria:**
- App launches on iOS + Android
- Login/logout works with existing Firebase accounts
- Session persists across restarts
- No TypeScript errors

### 9.3 Feature #82 — Path Tracking (Planned)

**Scope:**
- GPS + IMU data capture during site walkthroughs
- Store path data in PostgreSQL with PostGIS extension
- Schema: `paths` table (id, site_id, user_id, started_at, ended_at, geometry)
- Schema: `path_points` table (id, path_id, lat, lng, altitude, heading, timestamp)
- Accuracy target: ±5m acceptable
- Typical duration: 5–30 minutes

**Dependencies:** PostGIS on Cloud SQL, `expo-location` (already installed in #81)

### 9.4 Feature #83 — Path Navigation (Planned)

**Scope:**
- Three.js overlay on 360° viewer showing captured path
- Tap point on path → jump to nearest 360° frame
- Breadcrumb trail visualization

**Dependencies:** #82 complete

### 9.5 Video Capture — ON HOLD ⏸️

**Blocked by 8 unanswered spec questions:**

| # | Question | Status |
|---|---|---|
| 1 | Video resolution: 1080p / 4K / 8K? | ❓ Unanswered |
| 2 | Codec: H.264 / VP9 / AV1? | ❓ Unanswered |
| 3 | Quality: CRF value (28 recommended)? | ❓ Unanswered |
| 4 | Path tracking: GPS only or GPS+IMU? | ❓ Unanswered |
| 5 | Accuracy: ±5m acceptable? | ❓ Unanswered |
| 6 | Duration: 5–30 min typical? | ❓ Unanswered |
| 7 | Mobile scope: iOS / Android / both? | ❓ Unanswered |
| 8 | Hardware: Insta360 / LG 360 / native / all? | ❓ Unanswered |

**Note:** Insta360 X4 hardware acquired. Video processing is being handled as a standalone module — see Section 10.

---

## 10. Insta360 X4 Video Handling Module 🎯 PLANNING

### 10.1 Overview

**Status:** Planning — no code yet
**Location:** `F:\Space360\modules\insta360\`
**Chat:** Separate Claude chat dedicated to this module
**Approach:** Standalone — built, tested, and validated independently before integration into Space360

### 10.2 Rationale

- Insta360 X4 has hardware-specific workflows (dual-lens `.insv` files, spatial metadata, proprietary stitching) that require dedicated handling
- Isolates complexity from Space360's active development pipeline
- Enables parallel development without blocking Stage 3
- Cleaner integration when module is fully production-ready

### 10.3 Planned Scope

| Responsibility | Detail |
|---|---|
| Video ingestion | From Insta360 X4 via USB / SD card / wireless |
| Format handling | `.insv` dual-lens → stitched equirectangular MP4 |
| Metadata extraction | GPS, IMU, heading, timestamp, resolution, bitrate |
| Quality validation | Corruption detection, completeness check, stitch quality |
| Format standardization | Normalized video + sidecar JSON for Space360 |
| Storage | Upload to GCS: `360-field-check-media-sgb/videos/` |
| Integration interface | Clean API or CLI that Space360 calls |

### 10.4 Planned Tech Stack

| Component | Technology |
|---|---|
| Language | Python |
| Video processing | FFmpeg + OpenCV |
| Interface | FastAPI or CLI (TBD) |
| Storage | Google Cloud Storage SDK |
| Initial environment | Local Windows (`F:\Space360\modules\insta360\`) |
| Future | Containerized for Cloud Run |

### 10.5 Integration Plan

Once module reaches production readiness (testing + documentation + validation complete), it will be merged into Space360 as a pluggable input handler for 360° video sources, per Stage 3 Phase 2 timeline.

---

## 11. Key Architectural Decisions

| Decision | Choice | Reason |
|---|---|---|
| Mobile framework | React Native + Expo | Cross-platform, reuses JS/TS skills |
| Mobile state | Redux Toolkit + redux-persist | Offline-first, consistent with patterns |
| Full-text search | GIN + tsvector (PostgreSQL) | Native, fast, no extra service |
| Contractor search scope | Site-restricted | Security requirement |
| Export async threshold | 500 issues | Balances UX vs server load |
| Export storage | GCS (existing bucket) | Reuse infrastructure |
| Filter presets | localStorage | Simple, no DB changes needed |
| Video processing | Standalone module | Isolates complexity, parallel workflow |
| Path tracking accuracy | ±5m acceptable | Sufficient for site walkthrough use case |
| Insta360 module location | `F:\Space360\modules\insta360\` | Separate from core codebase |
| Video specs | ON HOLD | Team not ready — 8 questions unanswered |
| Stage 3 path + mobile | PROCEED | Independent of video specs |
| Timeline | Flexible | Quality over speed |

---

## 12. Known Issues & Gotchas

| # | Issue | Status |
|---|---|---|
| 1 | Celery + Redis required for large exports (#80) — must be running locally for dev | Active |
| 2 | Video capture specs deferred — Stage 3 Phase 2 (video) cannot start until 8 questions answered | Active |
| 3 | Stage 1 must remain 100% backward compatible through all Stage 2/3 changes | Permanent constraint |
| 4 | AG can lose context in long sessions — send explicit state reset messages when drifting | Ongoing |
| 5 | `google-services.json` (Android) and `GoogleService-Info.plist` (iOS) must be placed manually for mobile Firebase config | Pending #81 |

---

## 13. Success Criteria

### Stage 2 (Complete ✅)
- Advanced filtering + search working
- Column sort working simultaneously with filters
- Data export (CSV/Excel/PDF) working for small and large datasets
- All Stage 1 features backward compatible

### Stage 3 (In Progress)
- Mobile app: login, navigation, session persistence on iOS + Android
- Path tracking: GPS capture + PostGIS storage working
- Path navigation: Three.js overlay on 360° viewer
- Mobile issue viewer: contractors can view/update assigned issues on mobile
- Test coverage: >80%, critical bugs: 0

### Insta360 Module (Planned)
- `.insv` → equirectangular MP4 pipeline working end-to-end
- Metadata sidecar JSON produced correctly
- GCS upload working
- Integration interface (API/CLI) documented and tested

---

## 14. Document History

| Version | Date | Author | Changes |
|---|---|---|---|
| v1.0 | Aug 21, 2026 | Claude (AI consultant) | Initial creation — full project handoff document |

---

*This document is the authoritative reference for Space360 development. Update it when stages complete, decisions change, or new modules are added.*
