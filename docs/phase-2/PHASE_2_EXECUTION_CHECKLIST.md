# Space360 Android Phase 2 — Execution Checklist
**Quick Reference for Managing Feature Development**

---

## Feature B: Offline Sync + Local Caching (WEEKS 1–2)

### Before Sending to AG
- [ ] Download `SPACE360_ANDROID_PROMPT_B_OFFLINE_SYNC.md`
- [ ] Review all Room schema changes (sync_queue, cache_metadata, sites)
- [ ] Confirm Project structure ready (`modules/android/`)
- [ ] Confirm GitHub branch ready (feature/phase-2-offline-sync)
- [ ] Prepare Android emulator (API 26 + latest)
- [ ] Prepare real test device (optional but recommended)

### Send to AG
- [ ] Copy entire prompt to Antigravity IDE
- [ ] Set AG to Agent Mode (autonomous execution)
- [ ] Provide brief context: "This is Phase 1 complete Android app. Build Feature B (offline + sync queue)."
- [ ] Let AG execute (should take 1–2 weeks)

### While AG is Building
- [ ] Check GitHub for commits (daily/weekly)
- [ ] Review commit messages for architecture decisions
- [ ] Flag any questions or concerns early

### After AG Commits (Testing Phase)
- [ ] Check out feature branch locally
- [ ] Run on emulator (API 26):
  - [ ] App launches without crash
  - [ ] Issue list loads + caches
  - [ ] Offline banner appears when network disabled
  - [ ] Update status offline → see pending badge
  - [ ] Reconnect → see syncing → complete
  - [ ] Force quit app → reopen → verify queue persisted
- [ ] Test on real device (if available):
  - [ ] Same scenarios as above
  - [ ] Check battery impact (15-min usage)
  - [ ] Verify no ANR (Application Not Responding)
- [ ] Run unit tests:
  - [ ] `./gradlew test` should pass
  - [ ] Coverage ≥ 70% for offline logic
- [ ] Check crash logs (Android Studio Logcat)

### Approval Gate (Go/No-Go)
- [ ] Zero crashes on SDK 26
- [ ] Offline banner + sync badges work
- [ ] WorkManager sync job triggers
- [ ] No data loss on force quit
- [ ] Unit + integration tests passing
- [ ] **DECISION: Approve OR Request Changes**

### If Approved
- [ ] Merge feature branch to main
- [ ] Tag commit: `v2.0.0-feature-b-complete`
- [ ] Notify: "Feature B complete. Ready for Feature A."
- [ ] I'll draft Feature A prompt

### If Changes Requested
- [ ] Document issues clearly
- [ ] Provide to AG with specific guidance
- [ ] Re-test after AG updates
- [ ] Back to Approval Gate

**Estimated Timeline: 2–3 weeks (AG build + your testing)**

---

## Feature A: Issue Viewer (WEEKS 2–4)

### Prerequisites
- [ ] Feature B approved + merged to main
- [ ] `IssueViewModel` + `IssueRepository` from Phase 1 ready
- [ ] Coil library available (already in Phase 1)

### Before Sending to AG
- [ ] I'll draft `SPACE360_ANDROID_PROMPT_A_ISSUE_VIEWER.md`
- [ ] Review screens: IssuesListScreen, IssueDetailScreen, StatusUpdateBottomSheet
- [ ] Review API endpoints (all existing; no new backend work needed)
- [ ] Confirm contractor-scoped access requirements
- [ ] Decision: Add photo upload Phase 2 or defer? (**Already decided: YES, add photos**)

### Send to AG
- [ ] Copy entire prompt to AG
- [ ] Context: "Feature A depends on Feature B (offline reads). Build Issue Viewer screens + API integration."
- [ ] Let AG execute

### While AG is Building
- [ ] Check GitHub commits
- [ ] Flag any questions early
- [ ] Prepare test data (contractor account + assigned issues)

### After AG Commits (Testing Phase)
- [ ] Check out feature branch
- [ ] Run on emulator:
  - [ ] Login as contractor
  - [ ] Issues list loads + shows assigned issues only
  - [ ] Pull-to-refresh updates data
  - [ ] Click issue → detail screen opens
  - [ ] View comments + photos
  - [ ] Update status (Open → In Progress → Done)
  - [ ] Add comment → see in thread (immediately locally)
  - [ ] Add photos → multi-select, upload, see in gallery
  - [ ] Go offline → view cached data
  - [ ] Reconnect → see syncing complete
- [ ] Test on real device
- [ ] Run tests: `./gradlew test`

### Approval Gate
- [ ] List loads + filters work (status, site, priority)
- [ ] Detail screen shows all data (comments, photos, history)
- [ ] Status update works (queued offline, synced online)
- [ ] Comments add + display
- [ ] Photos add + display + lightbox
- [ ] Contractor-scoped (no cross-account data leak)
- [ ] Zero crashes
- [ ] Tests passing

### If Approved
- [ ] Merge to main
- [ ] Tag: `v2.0.0-feature-a-complete`
- [ ] Notify: "Feature A complete. Ready for Feature C."
- [ ] I'll draft Feature C prompt

**Estimated Timeline: 3–4 weeks (AG build + your testing)**

---

## Feature C: Path Capture (WEEKS 4–6)

### Prerequisites
- [ ] Feature A approved + merged
- [ ] Backend team has built POST /api/paths endpoint (parallel work)
- [ ] POST /api/paths returns `path_id`, `waypoint_count`, status
- [ ] GPS + location services working in test environment

### Backend Coordination (Parallel)
- [ ] POST /api/paths endpoint exists
- [ ] Accepts: site_id, started_at, ended_at, waypoints JSON
- [ ] Returns: path_id, waypoint_count, status
- [ ] Creates paths + path_points rows (PostGIS geometry)
- [ ] Test with Postman/curl before AG integration

### Before Sending to AG
- [ ] I'll draft `SPACE360_ANDROID_PROMPT_C_PATH_CAPTURE.md`
- [ ] Review screens: PathCaptureScreen, MapPinScreen (optional)
- [ ] Review GPS setup (FusedLocationProviderClient)
- [ ] Review WorkManager background job
- [ ] Confirm 15–30s GPS interval acceptable
- [ ] Confirm auto-upload on completion (no manual review)

### Send to AG
- [ ] Copy prompt to AG
- [ ] Context: "Feature C: Build path recording UI + GPS capture + background job + auto-upload."
- [ ] Mention: Backend POST /api/paths ready (URL + request/response format)

### While AG is Building
- [ ] Backend team finalizes POST /api/paths
- [ ] Test POST /api/paths endpoint
- [ ] Prepare test site + floor plan map
- [ ] Check GitHub for AG commits

### After AG Commits (Testing Phase)
- [ ] Check out feature branch
- [ ] Run on emulator (tricky—use Android emulator GPS simulation):
  - [ ] Open PathCaptureScreen
  - [ ] Tap "Pin on Map" → see floor plan
  - [ ] Tap to place pin → confirm
  - [ ] Tap "Start Recording"
  - [ ] See elapsed time + accuracy indicator
  - [ ] Simulate GPS updates (Android emulator can send GPS via telnet)
  - [ ] After 5 min, tap "Stop Recording"
  - [ ] Path auto-uploads
  - [ ] See upload status (pending → synced)
  - [ ] Go offline → start recording → stop → path queued → reconnect → sync
- [ ] Test on real device with real GPS:
  - [ ] Walk around site while recording
  - [ ] Verify waypoints captured every 15–30s
  - [ ] Verify upload completes
  - [ ] Check battery impact (5–15 min recording)
- [ ] Run tests: `./gradlew test`

### Approval Gate
- [ ] Path recording UI works (Start/Stop)
- [ ] GPS updates captured (15–30s interval)
- [ ] Path waypoints stored in Room (path + path_points)
- [ ] Manual pin placement on map works
- [ ] Path auto-uploads on completion
- [ ] Backend POST /api/paths receives + stores correctly
- [ ] Failed uploads queued (Feature B sync handles)
- [ ] Battery impact acceptable (15–30s interval, PRIORITY_BALANCED otherwise)
- [ ] Foreground service notification shows (Android requirement)
- [ ] No crashes
- [ ] Tests passing

### If Approved
- [ ] Merge to main
- [ ] Tag: `v2.0.0-feature-c-complete`
- [ ] Tag: `v2.0.0-phase-2-complete` (all three features done)
- [ ] Notify: "Phase 2 complete. Ready for Phase 3 planning."
- [ ] I'll start Phase 3 planning (360° video, path visualization)

**Estimated Timeline: 3–4 weeks (AG build + your testing + backend coordination)**

---

## Testing Checklist (Each Feature)

### Unit Tests
- [ ] Run: `./gradlew test`
- [ ] All tests passing?
- [ ] Coverage ≥ 70% for critical paths (offline logic, sync queue, GPS, etc.)

### Integration Tests
- [ ] Emulator (API 26): Does the feature work end-to-end?
- [ ] Emulator (latest API): Does the feature work on newer Android?
- [ ] Real device: Does it work with real network + GPS?

### Functional Tests
- [ ] Follow acceptance criteria step-by-step
- [ ] Document any failures with screenshots/logs
- [ ] Test edge cases (network dropout mid-sync, low battery, etc.)

### Performance Tests
- [ ] Battery usage (5–30 min typical scenarios)
- [ ] Memory usage (Android Profiler)
- [ ] Crash-free (Logcat, no ANR)

### Security Tests
- [ ] No data leaks (contractor sees only own assigned data)
- [ ] Firebase token refreshes automatically
- [ ] 401 responses logout user
- [ ] No hardcoded secrets in code

---

## GitHub Workflow

### For You
1. Feature branch created by AG: `feature/phase-2-[feature-name]`
2. Pull request opened (you review + test)
3. Approve + merge to `main`
4. Tag release: `v2.0.0-feature-[x]-complete`

### Commit Messages to Expect
```
feat(android): Add offline sync queue + WorkManager (Feature B)
- Implement SyncQueueEntity + DAOs
- Add NetworkConnectivityManager
- Add SyncWorker for periodic sync
- Add Offline Banner UI component
- Update IssueRepository for offline writes
- Add unit tests (70% coverage)
```

---

## Communication Checklist

### When Sending to AG
- [ ] Paste entire prompt (no truncation)
- [ ] Provide context: "This is Phase 2 Feature [X]. Prior work complete. Build X. Here are specs."
- [ ] Mention blockers: "Backend needs POST /api/paths ready before you start Feature C."

### While AG is Building
- [ ] Check GitHub daily/weekly for progress
- [ ] Ask clarifying questions ASAP (don't wait until end)
- [ ] Flag blockers early (e.g., "Backend POST /api/paths not ready yet")

### After AG Completes
- [ ] Review code quality (structure, naming, comments)
- [ ] Run full test cycle
- [ ] Document approval/changes clearly
- [ ] Provide feedback to AG: "Approved" OR "Request changes: [specific issues]"

---

## Decision Tracker (For Reference)

| Decision | Feature(s) | Status |
|---|---|---|
| Build order: B → A → C | All | ✅ LOCKED |
| Status workflow: Open → In Progress → Done | A | ✅ LOCKED |
| Contractor adds photos on mobile | A | ✅ LOCKED |
| Sync frequency: 15-min WorkManager + on-demand | B | ✅ LOCKED |
| GPS interval: 15–30s sampling | C | ✅ LOCKED |
| Background tracking Phase 2: NO | C | ✅ LOCKED |
| Start point PIN: Manual (user taps map) | C | ✅ LOCKED |
| Conflict resolution: Silent last-write-wins | B | ✅ LOCKED |
| Path auto-upload: YES (on completion) | C | ✅ LOCKED |
| Path retention: 30-day auto-delete | C | ✅ LOCKED |

---

## Success Criteria (Phase 2 COMPLETE)

**When all three features pass:**

- ✅ Feature B: Offline sync working (15-min WorkManager, queue persistence, no data loss)
- ✅ Feature A: Issue Viewer working (list, detail, update status, add comments/photos)
- ✅ Feature C: Path capture working (GPS recording, upload, offline queue)
- ✅ All unit tests passing (≥70% coverage)
- ✅ All integration tests passing (emulator + real device)
- ✅ Zero crashes on SDK 26+ devices
- ✅ No security issues (contractor scoped, token handling)
- ✅ Battery impact acceptable (15–30s GPS interval, WorkManager backoff)
- ✅ Code review approved
- ✅ Documentation complete (commit messages, README updates)

**Phase 2 is COMPLETE when all above are checked ✅**

---

## Timeline at a Glance

```
Week 1–2:   Feature B (Offline Sync) — AG building
Week 2–3:   Feature B testing + approval
Week 3–4:   Feature A (Issue Viewer) — AG building
Week 4–5:   Feature A testing + approval
Week 5–6:   Feature C (Path Capture) — AG building + Backend coordination
Week 6–7:   Feature C testing + approval
Week 7+:    Phase 2 COMPLETE — Phase 3 planning
```

**Conservative estimate: 7–11 weeks total (quality-first approach)**

---

## Documents You'll Need

1. **Current (Aug 29, 2026):**
   - `SPACE360_MASTER_ROADMAP_v1.0.md` — Full project context
   - `PHASE_2_PLANNING_SUMMARY.md` — This planning doc
   - `PHASE_2_EXECUTION_CHECKLIST.md` — This checklist
   - `SPACE360_ANDROID_PROMPT_B_OFFLINE_SYNC.md` — Feature B AG prompt (READY)

2. **Coming (After Feature B Approved):**
   - `SPACE360_ANDROID_PROMPT_A_ISSUE_VIEWER.md` — Feature A AG prompt
   
3. **Coming (After Feature A Approved):**
   - `SPACE360_ANDROID_PROMPT_C_PATH_CAPTURE.md` — Feature C AG prompt

---

## Help & Questions?

If you get stuck:
1. Review this checklist (most issues are here)
2. Check GitHub for AG commit messages (context on decisions)
3. Ping me in chat for clarification
4. I can revise prompts if needed

**You've got this. Send Feature B to AG when ready. 🚀**

---

*Checklist v1.0 | August 29, 2026*
