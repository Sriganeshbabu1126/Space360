# Space360 v3 Feature Plan
**Version:** v1.0
**Created:** September 20, 2026

## Section 1: Compare Feature
**What is it?** 
The ability to visually compare site captures (360° photos/videos) or floor plans across different time periods side-by-side.

**What does the mobile app have?**
Currently, the mobile app lacks the side-by-side comparison feature. It focuses primarily on capturing data, listing issues, and navigating paths.

**What needs to be built for dashboard?**
The dashboard already has a basic `ComparePage.tsx` that synchronizes two Pannellum viewers for 360° image captures. However, this needs to be expanded to:
1. Support video comparison (syncing two video timelines).
2. Compare floor plans across dates with visual overlays (e.g., highlighting changes).
3. Generate AI summaries of identified changes (currently a placeholder in PDF export).

**Technical approach:**
- **Video Sync:** Extend the existing Pannellum synchronization logic (pitch, yaw, hfov) to also sync `currentTime` for videos.
- **Floor Plan Compare:** Use a Canvas API overlay with image differencing (e.g., pixelmatch) to highlight structural changes.
- **AI Summary:** Implement a backend endpoint that takes both images/frames, sends them to a Vision AI model (e.g., Gemini 1.5 Pro), and returns a textual diff summary.

## Section 2: Path Creation
**What is it?**
The ability to manually draw or verify inspection paths on floor plans, as opposed to just relying on GPS.

**Current state:**
The mobile app handles GPS path capture via `GpsTrackingService.kt` and `PathCaptureViewModel.kt` during walkthroughs. The dashboard currently lacks the ability to draw paths manually or edit GPS paths.

**Dashboard implementation needed:**
An interactive Canvas overlay on the `FloorPlansPage.tsx` where users can draw, edit, and save paths directly onto a 2D floor plan. 

**Technical approach:**
- Use `Fabric.js` or native Canvas API (similar to `ImageMarkupCanvas.tsx`) to draw polylines over floor plan images.
- Convert canvas coordinates to physical coordinates (or relative percentages) based on floor plan scale.
- Save created paths to the PostgreSQL database with PostGIS (`geometry` type) to unify with GPS-captured paths.

## Section 3: Navigate Video Using Path
**What is it?**
Clicking a specific point on a floor plan path or GPS track to instantly jump to the corresponding frame in the 360° video.

**Integration with Pannellum viewer:**
The `PathVideoViewer.tsx` component currently correlates timestamps to GPS coordinates, displaying thumbnails. We need to integrate this directly with a Pannellum 360° video player.

**How path points link to captured videos:**
The `correlations` table maps a `path_id` and `waypoint_id` to a `video_id` and `timestamp_offset_ms`. Clicking a waypoint fetches the `timestamp_offset_ms` and seeks the video player to that exact time.

**Technical approach:**
- Combine `PathVideoViewer.tsx` and `PannellumViewer.tsx` into a unified layout.
- Bind the waypoint click event to call `pannellumViewer.videoElement.currentTime = timestamp_offset_ms / 1000`.
- Display a marker moving along the path as the video plays (by updating selected waypoint state based on video `timeupdate` event).

## Section 4: Pending Dashboard Features
Features present in the mobile app but not in the dashboard:

1. **QR Scanner / Linker (High Priority)**
   - *Mobile:* `QRScannerScreen.kt`
   - *Dashboard:* Ability to generate QR codes for specific locations/issues to be printed and placed on-site.
   - *Dependency:* Floor plans and Sites must be configured.
2. **Offline Sync Management (Medium Priority)**
   - *Mobile:* `OfflineSyncManager.kt`, `SyncWorker.kt`
   - *Dashboard:* A view for admins to monitor pending syncs from field workers and resolve conflicts.
   - *Dependency:* Backend conflict resolution endpoints.
3. **Insta360 Camera Controls (Low Priority)**
   - *Mobile:* `Insta360Controller.kt`
   - *Dashboard:* Not strictly necessary for web, but remote triggering could be useful for mounted cameras.

## Section 5: On-Hold Items
**Video Capture Specs (Deferred from v2)**
- *Why deferred:* 8 critical questions regarding resolution, codec, path tracking accuracy, duration, and hardware scope were unanswered.
- *Ready now?* The Insta360 X4 module is now built and deployed to Cloud Run (v1.1.0). Video ingestion is functional. Once the remaining UX spec questions are answered, full integration into the mobile app and dashboard can commence.

## Section 6: v3 Priority Roadmap

**P1 (High): Navigate Video Using Path**
- *Why:* Unlocks the core value of 360° walkthroughs by linking spatial context (where am I?) to visual context (what does it look like?).
- *Complexity:* Medium (Frontend integration of Pannellum with existing path correlations).

**P2 (High): Video Compare Feature**
- *Why:* Clients need to see progress over time. Syncing two 360° videos is the most powerful demonstration of site progress.
- *Complexity:* High (Requires precise timeline synchronization and performance optimization in React).

**P3 (Medium): Manual Path Creation on Dashboard**
- *Why:* GPS is often inaccurate indoors. Allowing managers to pre-draw paths or correct GPS paths ensures accurate spatial data.
- *Complexity:* Medium (Canvas drawing math and coordinate translation).

**P4 (Low): QR Code Generation Dashboard**
- *Why:* Completes the mobile QR scanning loop.
- *Complexity:* Low (Simple library for QR generation).

## Section 7: Technical Architecture Notes
- **Compare Feature:** Video playback sync needs careful handling of buffering states to prevent one viewer from drifting ahead of the other.
- **Path Creation:** Needs a new DB table `floor_plan_paths` if paths are strictly 2D canvas coordinates, or we can reuse `paths` (PostGIS) by storing relative coordinates and mapping them to real-world coordinates using a floor plan anchor point.
- **Video Navigation:** The backend `/api/correlations/` endpoint already exists. We just need to wire the frontend state between the Floor Plan Canvas and the Pannellum Video component.
- **New Endpoints Needed:** `POST /api/floor-plans/{id}/paths` (save manual path), `GET /api/floor-plans/{id}/paths`.

## AG Implementation Prompts Plan

**Prompt 1: Video Navigation (P1)**
- *Task:* Refactor `PathVideoViewer` to integrate with `PannellumViewer`. Add interactive map/path component that scrubs video.
- *Dependencies:* None.
- *Estimated Cycles:* 2-3 AG prompts.

**Prompt 2: Video Comparison (P2)**
- *Task:* Upgrade `ComparePage.tsx` to handle video sources, syncing `currentTime` alongside pitch/yaw.
- *Dependencies:* None.
- *Estimated Cycles:* 2 AG prompts.

**Prompt 3: Manual Path Creation (P3)**
- *Task:* Build Canvas drawing tools on `FloorPlansPage.tsx`. Add backend endpoints to save paths.
- *Dependencies:* Backend DB schema update for paths linked to floor plans.
- *Estimated Cycles:* 3-4 AG prompts.
