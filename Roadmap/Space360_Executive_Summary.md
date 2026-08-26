# Space360: Executive Summary
## 360° Video + Camera Path + Mobile App Strategy
**Date:** August 18, 2026 | **Status:** Ready for Kickoff

---

## 🎯 Strategic Vision

**Transform Space360 from Static Image Capture → Dynamic Video-Centric Site Documentation**

### The Problem We're Solving
| Today | Tomorrow |
|-------|----------|
| Single 360° image snapshots | Continuous 2fps video + movement path |
| No context on where inspector went | Visual footprint shows exact walk pattern |
| Manual site review (photo by photo) | Fast-forward site evolution (video timeline) |
| Desktop-only capture setup | Field workers capture via mobile app |

### Business Impact
- 🚀 **30% faster field documentation** (mobile capture, no desktop)
- 📍 **Improved evidence quality** (continuous video vs single frames)
- 🗺️ **Better spatial understanding** (path visualization answers "where did they go?")
- 📊 **Temporal analysis** (track progress over weeks/months)

---

## 📦 What We're Building

### Feature 1: 360° Video @ 2fps
**Continuous temporal capture of construction progress**
```
Capture Session (20-30 min video)
    ↓
Extract at 2fps (120-180 frames)
    ↓
Store to GCS (compressed H.264)
    ↓
View in 360° player (browser)
```

### Feature 2: Camera Path Tracking
**GPS coordinates of inspector movement during video**
```
Video Recording
    ↓
Background: GPS every 1 second (or every 5m moved)
    ↓
Store waypoints + timestamps
    ↓
Create polyline (compressed, searchable)
    ↓
Sync to video timeline
```

### Feature 3: Navigation by Path
**Click path point → video jumps to that moment**
```
Floor Plan
    ↓
Path overlay (breadcrumb trail)
    ↓
User clicks point on trail
    ↓
Video scrubber jumps to that timestamp
    ↓
See what inspector was doing at that location
```

### Feature 4: Mobile App (Space360mob)
**Field workers start captures from site, no laptop needed**
```
Worker opens app on site
    ↓
Selects floor plan
    ↓
Drags pin to start location (or auto-places via GPS)
    ↓
Taps "Record"
    ↓
Walks around site (path + video captured)
    ↓
Taps "Stop"
    ↓
Uploads (or queues if offline)
    ↓
Appears in web app in 5 minutes
```

---

## 📊 Key Metrics & Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Development Velocity** | 7-9 weeks to GA | Sprint metrics + code commits |
| **Video Upload Success** | >95% | API error tracking |
| **Processing Time** | <10 min/video | CloudTask monitoring |
| **Path Accuracy** | ±5m acceptable | GPS + user feedback |
| **Mobile App Adoption** | >80% of users | App store analytics |
| **User NPS Score** | >50 | Post-release survey |
| **Infrastructure Cost** | $50-100/month | GCP billing |
| **Path Query Latency** | <500ms | Datadog APM |

---

## 🛠️ Technology Decisions

### Backend Enhancements
| Component | Technology | Why? |
|-----------|-----------|------|
| Video Encoding | FFmpeg + H.264 | Industry standard, cost-effective, all browsers support |
| Async Processing | Celery + Redis | Non-blocking, scales to 30 videos/hour |
| Spatial Data | PostGIS + PostgreSQL | Native SQL spatial queries, proven at scale |
| Path Compression | Google Polyline Algorithm | ~95% smaller than raw waypoints, navigation-optimized |
| Storage | Google Cloud Storage | Already integrated, enterprise-grade |

### Frontend Stack
| Component | Technology | Why? |
|-----------|-----------|------|
| 360° Player | Three.js + Panellum | WebGL, cross-browser, smooth performance |
| Path Overlay | Canvas2D | Lightweight, efficient for 1000+ waypoints |
| Timeline Scrubber | React + Recharts | Responsive, touch-friendly, existing pattern |
| State Management | Redux Toolkit | Already using, async handling (sagas) |

### Mobile Stack
| Component | Technology | Why? |
|-----------|-----------|------|
| Framework | React Native | Single codebase iOS + Android, code reuse |
| Camera | react-native-camera | Native bridge, hardware acceleration |
| GPS | react-native-geolocation | Background tracking, high accuracy |
| Offline Queue | SQLite + Redux | Resilient to network, syncs automatically |

---

## 📅 Timeline Breakdown

### Phase 1: Foundation (Weeks 1-3)
**Video Upload & Processing Pipeline**
```
Week 1-2: Backend setup
├─ PostgreSQL schema extensions (5 new tables)
├─ FFmpeg integration (codec, keyframe extraction)
├─ GCS upload orchestration
└─ API endpoints (POST /captures/{id}/video)

Week 2-3: Testing & Stabilization
├─ End-to-end flow: mobile upload → backend process → GCS store
├─ Error handling & retry logic
├─ Performance testing (20MB video processing)
└─ Database indexing optimization
```
**Acceptance:** Mobile can upload video, backend processes in <10 min, keyframes extracted

### Phase 2: Path & Navigation (Weeks 2-4)
**GPS Tracking + Interactive Path Visualization**
```
Week 2-3: Backend path processing
├─ GPS waypoint API endpoint
├─ Polyline encoding (compress 600 points → 5KB)
├─ PostGIS spatial indexing
└─ Path-to-video-frame association

Week 3-4: Frontend visualization
├─ 360° video player integration (Three.js)
├─ Path overlay on floor plan
├─ Timeline scrubber with sync
├─ Click-point-to-jump navigation
└─ Responsive grid layout (desktop/mobile)
```
**Acceptance:** Click path point on floor plan → video jumps to that moment

### Phase 3: Mobile MVP (Weeks 3-6)
**React Native App for iOS + Android**
```
Week 3-4: Project foundation
├─ React Native boilerplate (Expo or Bare)
├─ Firebase authentication
├─ Camera + GPS integration
└─ Floor plan image loader

Week 4-5: Core capture flow
├─ Live camera preview
├─ Dual-view: floor plan + camera feed
├─ Pin drag/placement
├─ Start/stop recording controls
├─ GPS waypoint collection

Week 5-6: Robustness
├─ Offline SQLite queue
├─ Sync-on-reconnect
├─ Error handling & retries
├─ Battery optimization
├─ iOS/Android builds

Week 6: Submissions
├─ App Store (iOS) submission
├─ Google Play (Android) submission
├─ Wait for approval (1-2 weeks)
```
**Acceptance:** App available in both stores, 30-min video capture with <20% battery drain

### Phase 4: Production (Weeks 7-9)
**Optimization, Security, Documentation**
```
Week 7: Performance & Security
├─ Video compression tuning (CRF 32)
├─ Keyframe lazy-loading
├─ GDPR compliance audit (geolocation data)
├─ Encryption at rest
└─ Rate limiting & DDoS protection

Week 8: Testing & Validation
├─ Load testing (100 concurrent users)
├─ Mobile app stability testing
├─ Cross-browser compatibility
├─ Accessibility audit (WCAG 2.1)
└─ Documentation (API, user guide)

Week 9: Deployment & Launch
├─ Cloud Run deployment setup
├─ Database backup/recovery procedures
├─ Monitoring & alerting (Datadog)
├─ Incident response runbook
├─ Beta testing program (50 testers)
└─ General Availability (GA) launch
```
**Acceptance:** Production-ready, no critical issues, monitoring in place

---

## 💰 Cost Analysis

### Infrastructure Monthly Cost

| Component | Estimated | Notes |
|-----------|-----------|-------|
| **Cloud Run (backend)** | $10-20 | ~30 concurrent requests/minute |
| **Cloud SQL (database)** | $15-25 | Managed PostgreSQL 16 |
| **Google Cloud Storage** | $20-50 | 500GB stored (compressed videos) |
| **Video Processing (Celery)** | $30-50 | 10 worker instances |
| **CDN & Data Transfer** | $10-20 | Keyframe downloads |
| **Firebase Auth** | $5-10 | Auth tokens, device management |
| **Monitoring (Datadog)** | $20-30 | APM + logs + alerts |
| **Backup & Archival** | $10-15 | Redundancy, disaster recovery |
| **Total Monthly** | **$120-220** | Scales with usage |

### Development Cost
- **Team:** 1 Backend Dev + 1 Frontend Dev + 1 Mobile Dev
- **Duration:** 7-9 weeks
- **Equivalent:** 1050-1350 development hours

---

## ⚠️ Risk Map (Mitigation Strategies)

### Critical Risks (Must Mitigate)

| # | Risk | Impact | Mitigation |
|---|------|--------|-----------|
| 1 | **Uncontrolled Video File Size** | Cost explosion | CRF 32 compression, 100MB quota/video, aggressive cleanup |
| 2 | **GPS Inaccuracy (Urban Canyon)** | Path misleading | Hybrid GPS+IMU, user-placeable pins, accuracy badges |
| 3 | **GCS Storage Runaway** | $1000+/month | Cost alerts, retention policy (30 days raw, 1yr compressed) |
| 4 | **GDPR Violation (Path Data)** | Legal liability | Encrypt at rest, anonymize option, auto-delete, privacy notice |
| 5 | **Path Processing Timeout** | UX lag | Async jobs, spatial indexing, waypoint sampling (1:10) |

### High Priority Risks

| # | Risk | Mitigation |
|---|------|-----------|
| 6 | React Native build fragmentation | CI/CD matrix, early device testing |
| 7 | 360 player performance on mobile | Proxy video (720p), lazy keyframes, canvas optimization |
| 8 | Concurrent video processing bottleneck | Scale workers (10→20), queue monitoring, alerts |
| 9 | Sync conflicts (offline mode) | Last-write-wins, audit log, conflict UI notification |
| 10 | Insta360 SDK availability | Fallback to manual upload, community SDK option |

---

## 🚀 Quick Start Checklist

### Pre-Kickoff (This Week)
- [ ] **Answer 8 clarification questions** (see detailed plan)
- [ ] **Approve budget** ($120-220/month ongoing)
- [ ] **Assign team** (backend, frontend, mobile devs)
- [ ] **Set up CI/CD** (GitHub Actions for mobile builds)
- [ ] **Provision GCS** (if not already done)

### Week 1 Sprint
- [ ] **Backend:** Schema migrations (5 new tables)
- [ ] **Frontend:** 360 player research (Three.js integration)
- [ ] **Mobile:** Project scaffold (React Native setup)
- [ ] **DevOps:** Video processing worker setup

### Week 2 Sprint
- [ ] **Backend:** Video upload + FFmpeg integration
- [ ] **Frontend:** Path overlay components
- [ ] **Mobile:** Camera + GPS integration
- [ ] **QA:** End-to-end test planning

---

## ❓ Critical Questions (Need Answers Before Week 1)

These answers unlock Phase 1 development:

### Video Specifications (Impact: file size, processing time, codec selection)
1. **Resolution?** → 1080p, 4K, 8K, or flexible?
2. **Codec?** → H.264 (safe), VP9 (better), AV1 (best)?
3. **Quality preference?** → File size vs visual quality trade-off?

### Path Tracking (Impact: accuracy, data volume, privacy)
4. **GPS only or hybrid (GPS+IMU)?** → Accuracy vs complexity
5. **Frequency?** → 1 sample/sec or 1 sample/5m moved?
6. **Accuracy ok at ±5m?** → Acceptable for site scale?

### Scale & Compliance (Impact: infrastructure, legal)
7. **Typical video duration?** → 5/10/30 min?
8. **GDPR/data retention?** → 30 days, 1 year, permanent?

### Mobile (Impact: development effort)
9. **iOS + Android or one platform?** → Affects build/test matrix
10. **External 360 camera or native device?** → Hardware assumptions

---

## 📈 Success Metrics Post-Launch

### Week 2 Post-Launch
- [ ] Video upload success rate > 95%
- [ ] Average processing time < 10 minutes
- [ ] Mobile app crashes < 0.5%

### Month 1 Post-Launch
- [ ] >80% of contractors using mobile app
- [ ] Path accuracy validated by users (±5m feedback)
- [ ] Zero data loss incidents
- [ ] Infrastructure cost within budget

### Month 3 Post-Launch
- [ ] User NPS score > 50
- [ ] <0.1% API error rate
- [ ] Mobile app store rating > 4.5/5 stars
- [ ] Ready for enterprise customers

---

## 🎬 Next Steps

### Immediate (Today)
1. **Review detailed strategic plan** (attached: `Space360_Strategic_Implementation_Plan.md`)
2. **Schedule kickoff meeting** with development team
3. **Answer 8 clarification questions** (move to development phase)
4. **Approve budget & resource allocation**

### This Week
1. **Sprint 0:** Project setup (repos, environments, CI/CD)
2. **Team kickoff:** Architecture review, tech stack walkthrough
3. **Infrastructure prep:** GCS, Cloud Run, database setup
4. **Risk assessment:** Identify team-specific blockers

### Next Week
1. **Sprint 1 begins:** Phase 1 foundation development
2. **Daily standups:** Async status updates (Slack)
3. **Weekly reviews:** Demo progress, adjust priorities
4. **Monitor metrics:** Cost, performance, error rates

---

## 📞 Contact & Questions

**For Strategic Questions:**
- Review the comprehensive 40-page detailed plan: `Space360_Strategic_Implementation_Plan.md`
- Sections covered: Architecture, Data Models, API Design, Testing, Security, Deployment

**For Technical Deep Dives:**
- Phase 1: Video Processing Pipeline
- Phase 2: Spatial Database & Path Visualization
- Phase 3: Mobile App Architecture & Offline Sync
- Phase 4: Performance Optimization & Security Hardening

**For Timeline/Resource Questions:**
- Development velocity: 7-9 weeks to General Availability
- Team size: 3 developers (backend, frontend, mobile)
- Cost: $120-220/month infrastructure

---

## Appendix: System Architecture (Visual)

```
┌─────────────────────────────────────┐
│      MOBILE APP (Space360mob)       │
│  - Camera Preview                   │
│  - Floor Plan Pin Placement         │
│  - GPS Background Tracking          │
│  - Offline SQLite Queue             │
└────────────────┬────────────────────┘
                 │ HTTP/REST + WebSocket
                 ↓
┌─────────────────────────────────────┐
│   BACKEND API (FastAPI + Python)    │
│  - Video Upload Handler             │
│  - FFmpeg Processing (Celery)       │
│  - Path Processing Service          │
│  - Navigation Service               │
│  - Issue Service (extended)         │
└────────────────┬────────────────────┘
                 │ SQL Queries
                 ↓
┌─────────────────────────────────────┐
│   DATABASE (PostgreSQL 16)          │
│  - video_captures                   │
│  - camera_paths (GeoJSON)          │
│  - path_waypoints (spatial index)   │
│  - video_keyframes                  │
│  - start_point_pins                 │
└────────────────┬────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────┐
│  STORAGE (Google Cloud Storage)     │
│  - Raw Videos (video/)              │
│  - Proxy Videos (video-proxy/)      │
│  - Keyframes (keyframes/)           │
│  - Thumbnails (thumbnails/)         │
└─────────────────────────────────────┘

┌──────────────────────────────────────────┐
│   WEB APP FRONTEND (React)               │
│  - 360° Video Player (Three.js)         │
│  - Path Overlay (Canvas2D)              │
│  - Timeline Scrubber                    │
│  - Issue Creation from Video            │
└──────────────────────────────────────────┘
```

---

**Document Status:** ✅ Ready for Leadership Review & Team Kickoff  
**Next Action:** Answer clarification questions → Begin Phase 1 Sprint  
**Estimated GA Date:** Week 9 (7-9 weeks from kickoff)
