---
name: fix-video-stitching
description: >
  Diagnoses and fixes Space360 video stitching hanging issues. Identifies root causes 
  in Cloud Run FFmpeg pipeline, compares versions, and either fixes or rolls back 
  to working state. Use when video stitching takes 2+ hours instead of 2-4 minutes. 
  Critical infrastructure skill — must complete with verification.
---

# Space360 Video Stitching Fix Skill

**CRITICAL PRIORITY**: Video stitching is the core feature of Space360. This skill resolves hangs, timeouts, and performance issues that prevent users from processing 360° videos.

---

## Decision Tree: Diagnosis First

Before fixing, determine the issue:

```
Is video stitching hanging for 2+ hours?
├─ YES, no error in logs
│   └─ Likely: FFmpeg subprocess deadlock, pipe buffering, or timeout
├─ YES, with FFmpeg error in logs
│   └─ Likely: Filter chain incompatibility or codec issue
└─ NO, but slow (5-20 min)
    └─ Likely: Optimization issue (2fps filter, scale order, etc)
```

---

## Phase 1: Deep Log Investigation (30 minutes)

### Step 1: Access Cloud Run Logs
```
https://console.cloud.google.com/run/detail/asia-southeast1/insta360-module/logs
```

### Step 2: Locate Stuck Job
- Find job in Firestore database
- Note: `created_at_utc`, `status: "running"`, `current_step: "stitch"`
- Current stuck job: `b427e53a-00a5-4a47-8569-76cf23b91f9c` (created 2026-09-23T09:20:02)

### Step 3: Extract FFmpeg Details from Logs
Look for these patterns in logs:

```
# FFmpeg command being executed
ffmpeg -i input.insv -vf ... -c:v libx264 ... output.mp4

# FFmpeg output (frames being processed)
frame= 120 fps=  45 q=-1 Lsize=...

# Errors (timeouts, pipe issues, etc)
Pipe broken | Timeout | Buffer overflow | Segmentation fault
```

### Step 4: Identify Issue Type
- **Hangs at frame N**: FFmpeg is processing but stuck (subprocess issue)
- **No frame output**: FFmpeg initialization hanging (filter chain issue)
- **Pipe broken**: Buffer overflow or subprocess crash (pipe handling issue)
- **Timeout after 3600s**: Exceeds Cloud Run timeout (need faster algorithm)

### Step 5: Compare Versions
```bash
# Get v2.0.6 (last known working)
git show v2.0.6:modules/insta360/core/stitcher.py | grep -A 50 "def _build_ffmpeg_command"

# Get v2.0.10 (current broken)
cat F:\Space360\modules\insta360\core\stitcher.py | grep -A 50 "def _build_ffmpeg_command"

# Diff them
git diff v2.0.6 v2.0.10 -- modules/insta360/core/stitcher.py
```

---

## Phase 2: Root Cause Analysis

### Decision: Is root cause clear?

| Finding | Action |
|---------|--------|
| Clear FFmpeg error in logs | **Fix v2.0.10** (fix the specific issue) |
| Logs show subprocess timeout (3600s) | **Optimize v2.0.10** (faster algorithm) |
| No logs, just hangs | **Investigate subprocess** (pipe/buffering issue) |
| Multiple cascading issues | **Rollback to v2.0.6** (safest option) |
| Unknown issue | **Rollback to v2.0.6** (get working fast) |

### If fixing v2.0.10:
- File: `F:\Space360\modules\insta360\core\stitcher.py`
- Modify: FFmpeg command construction
- Common fixes:
  - Move `-an` (audio strip) to correct position
  - Fix filter chain order: `fps=fps=2,scale=...` 
  - Check pipe buffering in subprocess calls
  - Verify codec arguments

### If rolling back to v2.0.6:
```bash
cd F:\Space360
git checkout v2.0.6 -- modules/insta360/core/stitcher.py
# Build v2.0.11 (with v2.0.6 code)
```

---

## Phase 3: Implementation

### Autonomously decide and execute:

**Option A: Fix v2.0.10**
```bash
# 1. Fix stitcher.py
# 2. Rebuild
gcloud builds submit modules/insta360 \
  --tag asia-southeast1-docker.pkg.dev/space360-114433/space360/insta360-module:v2.0.11 \
  --project space360-114433
# 3. Deploy
gcloud run deploy insta360-module \
  --image=asia-southeast1-docker.pkg.dev/space360-114433/space360/insta360-module:v2.0.11 \
  --region=asia-southeast1 --project=space360-114433
```

**Option B: Rollback to v2.0.6**
```bash
# 1. Checkout v2.0.6 code
# 2. Build v2.0.11 (same binary as v2.0.6)
gcloud builds submit modules/insta360 \
  --tag asia-southeast1-docker.pkg.dev/space360-114433/space360/insta360-module:v2.0.11 \
  --project space360-114433
# 3. Deploy same way
```

**PRIORITY**: Get working stitching ASAP. Choose fastest path.

---

## Phase 4: Verification & Testing

### Verification Checklist:

- [ ] **Deployment verified**
  ```bash
  curl https://insta360-module-1046334946412.asia-southeast1.run.app/health
  # Expected: {"status": "ok", "version": "2.0.11", "available_codec": "libx264"}
  ```

- [ ] **Stuck job deleted**
  - Go to Firestore → jobs collection
  - Delete: `b427e53a-00a5-4a47-8569-76cf23b91f9c`

- [ ] **Fresh upload test**
  - Dashboard → Captures → Upload new video
  - Monitor status page
  - **Target time: 2-4 minutes to completion**

- [ ] **Multiple uploads tested** (3x)
  - All should complete in 2-4 minutes
  - No hangs, no errors
  - Videos appear in gallery

- [ ] **Compare page works**
  - Videos load in Compare viewer
  - Path overlay renders
  - No console errors

### Stress Test (if working):
- Upload 3 videos simultaneously
- All should complete ~4 min
- Dashboard should handle concurrent jobs
- No resource exhaustion

---

## Phase 5: Quality Assurance

### Final Verification:

```
✅ Stitching completes in 2-4 minutes (not 2+ hours)
✅ No errors in Cloud Run logs
✅ No hanging FFmpeg processes
✅ Videos process reliably
✅ Dashboard displays results
✅ Compare page functional with path overlay
✅ Database records updated correctly
✅ Zero console errors
```

### If still failing:
- Do NOT declare success
- Continue debugging
- Consider alternative approaches
- Document findings
- Report blockers

---

## Phase 6: Final Report

Report must include:

**ROOT CAUSE**
- What was causing the 2+ hour hang?
- Why did v2.0.6-v2.0.10 differ?

**SOLUTION**
- Option A (fixed): What was changed?
- Option B (rollback): Why v2.0.6 chosen?

**VERIFICATION**
- Stitching time: X minutes
- Test results: All passed ✅
- No errors: ✅
- Ready for production: ✅

**READY FOR**
- User testing (Compare page + path overlay)
- Production deployment
- Sprint 3B/3C work

---

## Autonomous Authority

You have **FULL AUTHORITY** to:
- Deep-dive into logs without asking
- Make technical decisions independently
- Modify code and rebuild
- Test comprehensively
- Declare success only when verified
- Don't stop until stitching works at 2-4 minute target

---

## Critical Success Criteria

This skill succeeds when:
1. ✅ Root cause identified and documented
2. ✅ Video stitching completes in 2-4 minutes
3. ✅ 3+ consecutive uploads all successful
4. ✅ No hanging FFmpeg processes
5. ✅ Dashboard + Compare page fully functional
6. ✅ Zero console/backend errors
7. ✅ Ready for production use

**DO NOT** consider this complete until ALL criteria met.
