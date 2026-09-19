# Space360 v2 Kickoff Migration Summary

## 1. Project Status
- **Current State:** Space360 Insta360 X4 Module v1.1.0 is **LIVE** on Cloud Run.
- **Production URL:** `https://insta360-module-1046334946412.asia-southeast1.run.app`
- **Phases Completed:** Phase 1 (Module), Phase 2 (Backend/Frontend integration), Phase 3 (Cloud Run deployment).
- **Test Scorecard:** 65/65 passing (40 module, 17 backend, 4 frontend + 4 integration).

## 2. Environment & Credentials Reference
- **GCP Project ID:** `space360-114433`
- **GCS Bucket:** `360-field-check-media-sgb`
- **Region:** `asia-southeast1`
- **Container Registry:** `asia-southeast1-docker.pkg.dev`
- **Service Account:** `insta360-sa@space360-114433.iam.gserviceaccount.com`
- **Python version:** 3.13
- **MediaSDK version:** v3.1.5

## 3. Architecture Decisions (Frozen)
- **Module Boundary:** HTTP-only module boundary (no direct Python imports into backend).
- **Stitching Engine:** FFmpeg is the permanent fallback, MediaSDK is optional due to Windows stability issues.
- **Multiprocessing:** `multiprocessing.Process` wrapper is used for MediaSDK isolation to prevent master crashes.
- **Deployment OS:** `python:3.13-slim` Linux container (pivoted away from Windows Server Core).
- **Concurrency:** `max-instances=1` on Cloud Run to protect in-memory/file-based job state.
- **Codec:** `h264` codec enforced (web-safe for Pannellum 360 viewer).
- **Authentication:** Firebase JWT auth required across all endpoints.
- **Sidecar JSON:** Schema v1.0 locked.

## 4. File Locations
- **Insta360 Module:** `F:\Space360\modules\insta360\`
- **Backend (FastAPI):** `F:\Space360\backend\`
- **Frontend (React):** `F:\Space360\dashboard\`
- **Docs:** `F:\Space360\docs\`
- **Master Roadmap:** `F:\Space360\docs\SPACE360_MASTER_ROADMAP_v1_0.md`
- **Deployment Record:** `F:\Space360\modules\insta360\DEPLOYMENT_RECORD.md`

## 5. Known Limitations
- **MediaSDK Instability:** MediaSDK throws `0xC0000005` on all real `.insv` videos. FFmpeg completely handles production stitching.
- **Job State Limit:** Job state is currently stored in-memory + file. Cloud Run requires `max-instances=1` to prevent parallel processing overwrites.
- **Cold Start:** The Linux container takes ~10-15s to warm up on first request.
- **Pannellum Validation:** Equirectangular output requires manual visual verification after the first *real* field upload.

## 6. v2 Priority Roadmap
1. **[High]** Firestore job state migration (Removes `max-instances=1` concurrency limit).
2. **[High]** GCS Signed URLs for extremely large `.insv` file uploads (bypassing backend bottlenecks).
3. **[Medium]** Cloud Monitoring custom alerts (error rates, latency spikes, memory OOMs).
4. **[Medium]** Deep dive investigation into Insta360 MediaSDK (requires contacting support).
5. **[Low]** Circuit breaker for MediaSDK (auto-disable if failure threshold is reached).
6. **[Low]** GPU `h264_nvenc` encoding (if NVIDIA drivers are upgraded in the future).

## 7. Open Questions for Human (To Answer on Kickoff)
- **Q1:** Did Pannellum display the 360 video correctly (equirectangular) after your first real upload?
- **Q2:** What was the actual cold start delay during your manual testing?
- **Q3:** Have there been any unexpected errors in Cloud Logging over the last 48 hours?
- **Q4:** Have you noticed any queue backlogs due to the `max-instances=1` constraint?
- **Q5:** Are we ready to begin the Firestore job state migration today?

## 8. Migration Instructions
To migrate to the new session, attach this file and paste the opening message from `NEW_CHAT_SETUP.md`.
