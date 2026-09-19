# Insta360 Module Deployment Record

## Deployment Details
- **Date/Time:** 2026-09-19 13:58:00 (SGT)
- **Image Version:** v1.1.0
- **Base Image:** python:3.13-slim (Linux Container)
- **Cloud Run URL:** https://insta360-module-1046334946412.asia-southeast1.run.app
- **Region:** asia-southeast1
- **Project ID:** space360-114433
- **Port Mapping:** 8000

## Architecture Change Log
During deployment, the decision was made to pivot from a Windows Server Core container to a lightweight Linux container. 
- The unreliable Insta360 MediaSDK DLL was disabled via `MEDIASDK_ENABLE=false`.
- The robust FFmpeg fallback pipeline (which performs the equirectangular dual-fisheye projection perfectly via `-vf v360=input=fisheye:output=equirect`) is now the permanent primary stitcher.
- This allows native deployments using Google Cloud Build's default worker pool without complex private Windows worker networking.

## Test Results
- **Module Regression:** 40/40 PASS
- **Backend Regression:** 17/17 PASS
- **Frontend Regression:** 4/4 PASS
- **Health Check (Cloud Run):** PASS (`ffmpeg_available: true`)

## Known Limitations
- **Cold Starts:** Requests hitting the module after 15 minutes of inactivity may take ~2-5 seconds longer to process initially while the container provisions.
- **Concurrency:** The instance is configured with `max-instances=1` to prevent GCS write locking issues if multiple files are stitched simultaneously. Scale this up if queuing mechanisms are enhanced.
