# Space360 Android — Phase 2 Planning Summary
**Status:** ✅ Planning Complete | Ready for AG Execution  
**Date:** August 29, 2026  
**Feature Build Order:** B → A → C (LOCKED)  

---

## Phase 2 Overview

| Feature | Purpose | Timeline | Status |
|---|---|---|---|
| **Feature B** | Offline-first caching + sync queue (foundational) | Weeks 1–2 | 🔄 **READY FOR AG** |
| **Feature A** | Issue Viewer (contractor mobile UX) | Weeks 2–4 | ⏳ Prompt pending |
| **Feature C** | Path Capture (GPS tracking) | Weeks 4–6 | ⏳ Prompt pending |

---

## Key Decisions (LOCKED)

### Status Workflow
✅ **Open → In Progress → Done** (sequential transitions, backend enforces)

### Photo Evidence
✅ **Contractor CAN add new photos** to existing issue (POST /api/issues/{id}/photos)

### Sync Frequency
✅ **WorkManager 15-minute periodic** + on-demand (reconnect event + user manual retry)

### GPS Interval
✅ **15–30 second sampling** (supports 2fps video correlation in Phase 3)

### Background Tracking
✅ **NO background service Phase 2** (user must keep app in foreground; Phase 3 adds background capability)

### Start Point PIN
✅ **Contractor manually pins on Android map BEFORE recording** (not automatic GPS placement)

### Non-Critical Recommendations (Approved)
✅ Search/Filter: Status + Site + Priority  
✅ Conflict Resolution: Silent last-write-wins (no dialog)  
✅ Path Upload: Auto-upload on completion  
✅ Path Retention: 30-day auto-delete (GDPR-friendly)  

---

## Phase 2 Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     Jetpack Compose UI                    │
│  (IssuesPage, IssueDetail, PathCaptureScreen, etc.)      │
└──────────────────────┬───────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────┐
│                   ViewModels                              │
│  (IssueViewModel, PathViewModel, etc.)                    │
│  Observe: isOnline, pendingSyncCount, issues, errors      │
└──────────────────────┬───────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────┐
│              Domain Layer (Repositories)                  │
│  (IssueRepository, PathRepository)                        │
│  • Offline-aware (cache-first reads)                      │
│  • Write queueing (optimistic updates)                    │
│  • Sync logic                                             │
└──────┬──────────────────────────────────────┬────────────┘
       │                                       │
       ▼                                       ▼
┌────────────────┐                   ┌───────────────────┐
│  Retrofit +    │                   │ Room Database     │
│  OkHttp        │                   ├───────────────────┤
│  (Network)     │                   │ • issues          │
│                │                   │ • comments        │
│                │                   │ • photos          │
└────────────────┘                   │ • sync_queue (NEW)│
                                     │ • cache_metadata  │
        ▲                            │ • sites (NEW)     │
        │                            │ • paths (C)       │
        │ (WorkManager)              │ • path_points (C) │
        │                            └───────────────────┘
┌───────▼────────────────────────────────────────────────┐
│          NetworkConnectivityManager (NEW)               │
│  • Observe online/offline state                         │
│  • Trigger sync on reconnect                            │
│  • Background WorkManager job (15-min periodic)         │
└────────────────────────────────────────────────────────┘
```

---

## Feature B: Offline Sync + Local Caching (READY FOR AG)

### What's Included in Prompt

✅ **NetworkConnectivityManager** — Observe online/offline state via Flow  
✅ **Room Schema** — 3 new tables (sync_queue, cache_metadata, sites)  
✅ **DAOs** — Query + update operations  
✅ **IssueRepository** — Offline-aware reads + write queueing  
✅ **SyncWorker** — WorkManager background job (15-min + on-demand)  
✅ **UI Components** — Offline banner + sync status badges  
✅ **ViewModel Integration** — Expose isOnline + pendingSyncCount  
✅ **Error Handling** — Retry logic (exponential backoff, max 5 retries)  
✅ **Testing Strategy** — Unit + integration + E2E guidelines  

### Acceptance Criteria

- ✅ Offline banner visible when no network
- ✅ Writes queued immediately (optimistic local updates)
- ✅ WorkManager flushes queue every 15 min + on reconnect
- ✅ Synced operations marked in Room (syncedAt timestamp)
- ✅ Failed operations retry with backoff; max 5 retries → error badge
- ✅ Manual retry button on failed operations
- ✅ Cache expires per TTL (24h issues, 7d sites)
- ✅ Pull-to-refresh forces fresh network fetch
- ✅ No data loss if app force-quit mid-sync
- ✅ Zero crashes on SDK 26+ devices

### Deliverables After AG

- `com/sgbdevapps/space360/data/local/entities/SyncQueueEntity.kt`
- `com/sgbdevapps/space360/data/local/entities/CacheMetadataEntity.kt`
- `com/sgbdevapps/space360/data/local/entities/SiteEntity.kt`
- `com/sgbdevapps/space360/data/local/dao/SyncQueueDao.kt`
- `com/sgbdevapps/space360/data/local/dao/CacheMetadataDao.kt`
- `com/sgbdevapps/space360/data/local/dao/SiteDao.kt`
- `com/sgbdevapps/space360/data/network/NetworkConnectivityManager.kt`
- `com/sgbdevapps/space360/data/sync/SyncWorker.kt`
- `com/sgbdevapps/space360/presentation/components/OfflineBanner.kt`
- `com/sgbdevapps/space360/presentation/components/IssueSyncStatusBadge.kt`
- Updated `IssueRepository.kt` (offline logic)
- Updated `IssueViewModel.kt` (connectivity + sync state)
- Updated `build.gradle.kts` (androidx.work dependency)
- Updated `AndroidManifest.xml` (permissions)
- Database migration: `IssuePhotoEntity.status` field (sync tracking)

---

## Feature A: Issue Viewer (Coming Next)

### High-Level Scope
- Issues list (contractor's assigned sites only)
- Issue detail screen (title, description, status, priority, photos)
- Status update (Open → In Progress → Done)
- Comment posting (add + read)
- Photo gallery (view + add new photos)
- Offline reads from cache (Feature B enabled)

### Key Screens
- `IssuesListScreen` (LazyColumn, pull-to-refresh, filters, search)
- `IssueDetailScreen` (header, comments, photo gallery, status update card)
- `StatusUpdateBottomSheet` (radio buttons, confirm)
- `CommentInputField` (text input, send button, pending state)
- `PhotoGallery` (responsive grid, lightbox, swipe nav)

### Backend Endpoints (All Existing)
- GET `/api/issues?assigned_to=...&site_id=...` (list with filters)
- GET `/api/issues/{id}` (detail + comments + photos)
- PUT `/api/issues/{id}` (update status)
- POST `/api/issues/{id}/comments` (add comment)
- POST `/api/issues/{id}/photos` (add photos) ← **NEW in Phase 2**

### Dependencies
- Coil (image loading, caching)
- Retrofit (existing)
- Room (existing + Feature B tables)

### Acceptance Criteria
- ✅ List all assigned issues (paginated)
- ✅ View detail (title, description, status, priority, comments, photos)
- ✅ Update status (Open → In Progress → Done)
- ✅ Add comments (text input, synced)
- ✅ Add photos (multi-select, JPG/PNG, upload)
- ✅ View photos (lightbox, swipe, metadata)
- ✅ Contractor-scoped (sees only assigned sites)
- ✅ Offline reads from cache
- ✅ User-friendly error handling
- ✅ Pull-to-refresh updates

### Timeline
- Weeks 2–4 (after Feature B complete)

### AG Prompt (Pending)
- Will include full screen designs, ViewModel spec, API integration, error handling
- Depends on Feature B completion

---

## Feature C: Path Capture (Coming Last)

### High-Level Scope
- Start/Stop path recording UI
- Continuous GPS capture (15–30s interval)
- Store waypoints locally (Room: path + path_points tables)
- Manual pin placement on floor plan map (before recording)
- Auto-upload on completion (POST /api/paths)
- Background service + persistent notification
- Battery optimization (PRIORITY_HIGH_ACCURACY while recording)
- Offline sync queue handling (Feature B)

### Key Screens
- `PathCaptureScreen` (Start/Stop button, elapsed time, accuracy indicator, lat/lng debug)
- `MapPinScreen` (floor plan map, tap to place start pin, confirm)
- (Optional) `PathHistoryScreen` (list completed paths, upload status)

### Backend Endpoint (NEW)
```
POST /api/paths
{
  "site_id": "...",
  "started_at": "2026-08-29T...",
  "ended_at": "2026-08-29T...",
  "waypoints": [
    {"lat": 1.3521, "lng": 103.8198, "altitude": 10.5, "heading": 45.2, "timestamp": "..."},
    ...
  ]
}
→ Response: {"path_id": "...", "waypoint_count": 180, "status": "received"}
```

### Dependencies
- Google Play Services: Location (FusedLocationProviderClient)
- androidx.work (WorkManager, already in Feature B)
- Room (Feature B)

### Acceptance Criteria
- ✅ Start/Stop UI works
- ✅ GPS updates every 15–30s (±5m typical accuracy)
- ✅ Path/waypoints stored in Room
- ✅ Elapsed time displays accurately
- ✅ Accuracy indicator (GPS accuracy in meters)
- ✅ Foreground service + persistent notification
- ✅ Auto-upload on completion
- ✅ Backend POST /api/paths endpoint exists
- ✅ Failed uploads queued (Feature B handles retry)
- ✅ 15-min session ≈ 180 waypoints
- ✅ No battery drain complaints (15–30s interval mitigates)

### Timeline
- Weeks 4–6 (after Feature B + A complete)

### AG Prompt (Pending)
- Will include GPS setup, FusedLocationProviderClient integration, WorkManager background service, map integration, error handling
- Requires backend POST /api/paths endpoint (built in parallel by backend team)

---

## Workflow (For You)

### Step 1: Send Feature B Prompt to AG (NOW)

**File:** `SPACE360_ANDROID_PROMPT_B_OFFLINE_SYNC.md` (attached in outputs)

**Action:**
1. Copy the entire prompt
2. Paste into Antigravity IDE (Agent Mode)
3. Let AG execute (1–2 weeks)
4. AG will:
   - Commit code to `modules/android/` branch on GitHub
   - Implement all Room schema, DAOs, WorkManager, UI components
   - Push passing unit tests
   - Document any new decisions/edge cases in commit messages

**Testing (Your Role):**
- Check out branch when AG commits
- Test on Android emulator (API 26 + latest)
- Test on real device if available
- Verify: Offline banner appears, sync queue populates, no crashes
- Approve when satisfied

### Step 2: I'll Draft Feature A Prompt (After B Approved)

Once you confirm Feature B works:
- I'll draft Feature A (Issue Viewer) prompt
- You send to AG
- Same cycle: AG implements → you test → approve

### Step 3: I'll Draft Feature C Prompt (After A Approved)

Once Feature A is solid:
- I'll draft Feature C (Path Capture) prompt
- Coordinate with backend team on POST /api/paths endpoint
- You send to AG
- AG implements

### Step 4: Feature C Backend Work (Parallel)

While AG is building Feature C on Android:
- Backend team adds POST /api/paths endpoint
- Backend creates `paths` + `path_points` tables (PostGIS)
- Backend returns path_id + waypoint_count on success
- Test with Postman or curl

### Step 5: Phase 2 Complete ✅

When all three features pass acceptance criteria:
- Phase 2 is production-ready
- Prepare for Phase 3 (360° video, path visualization, background service)

---

## Risk Mitigation

| Risk | Severity | Mitigation |
|---|---|---|
| **AG loses context in long session** | MEDIUM | Send explicit state reset messages every 2 weeks. I'll provide summary cards. |
| **WorkManager not triggering on SDK 26 devices** | LOW | Test extensively. Android docs cover edge cases. AG can add fallback polling if needed. |
| **GCS signed URLs expire while offline** | MEDIUM | Feature A will handle (refresh URL before display or increase TTL). Coordinate with Feature A prompt. |
| **Feature B too complex; AG needs iteration** | MEDIUM | AG can ask for clarification. I'll provide additional context. Build incrementally (sync queue → offline reads → UI). |
| **Contractor accidentally syncs wrong data offline** | LOW | Last-write-wins is acceptable; backend has audit trail if needed. Warn in docs. |

---

## Timeline Estimate (Conservative)

| Phase | Duration | Notes |
|---|---|---|
| Feature B (Offline Sync) | 1–2 weeks | Foundation; most complex offline logic |
| Testing + Approval (B) | 1 week | Your testing cycle |
| Feature A (Issue Viewer) | 2–3 weeks | UI-heavy; depends on B |
| Testing + Approval (A) | 1 week | Your testing cycle |
| Feature C (Path Capture) | 2–3 weeks | GPS + WorkManager; parallel backend work |
| Testing + Approval (C) | 1 week | Your testing cycle |
| **Total Phase 2** | **8–11 weeks** | Conservative; quality-first approach |

---

## What's NOT in Phase 2

❌ 360° video capture (Phase 3)  
❌ Path visualization on map (Phase 3)  
❌ Background path recording after app exit (Phase 3)  
❌ Admin/Manager mobile views (Phase 3+)  
❌ Real-time collaboration (Phase 4+)  
❌ Insta360 module integration (separate project)  

---

## Next Actions

### Immediate (Today)
1. ✅ Read this summary
2. ✅ Download `SPACE360_ANDROID_PROMPT_B_OFFLINE_SYNC.md`
3. 📋 Prepare Antigravity IDE for AG execution
4. 🚀 Send Feature B prompt to AG when ready

### After Feature B Complete (1–2 weeks)
1. Test Feature B on emulator + real device
2. Approve (or request changes)
3. I'll draft Feature A prompt
4. Send Feature A to AG

### After Feature A Complete (2–3 weeks)
1. Test Feature A on device
2. Approve (or request changes)
3. I'll draft Feature C prompt
4. Coordinate with backend team (POST /api/paths endpoint)
5. Send Feature C to AG

---

## Documentation

**Planning Documents:**
- ✅ `SPACE360_MASTER_ROADMAP_v1.0.md` (overall project context)
- ✅ `PHASE_2_PLANNING_SUMMARY.md` (this file)

**AG Prompts:**
- ✅ `SPACE360_ANDROID_PROMPT_B_OFFLINE_SYNC.md` (Feature B — READY)
- ⏳ `SPACE360_ANDROID_PROMPT_A_ISSUE_VIEWER.md` (Feature A — pending)
- ⏳ `SPACE360_ANDROID_PROMPT_C_PATH_CAPTURE.md` (Feature C — pending)

**GitHub:**
- Module location: `F:\Space360\modules\android\`
- Repository: https://github.com/Sriganeshbabu1126/Space360
- Branch: `feature/phase-2-offline-sync` (AG will use)

---

## Questions?

If you have questions before sending Feature B to AG:
- Review the acceptance criteria (are they clear?)
- Review the dependencies (is everything available?)
- Review the ViewModel spec (are ViewModels designed correctly?)
- Ping me in this chat — I'll clarify or adjust

**Ready to proceed? Send Feature B prompt to AG when you're ready. I'll monitor your progress and draft Feature A once B is approved.** 🚀

---

*Document Version: 1.0 | Created: August 29, 2026*
