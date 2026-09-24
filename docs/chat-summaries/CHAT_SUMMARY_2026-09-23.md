# 🚀 Work Done Report - Sept 22/23, 2026

## Overview
This report summarizes the troubleshooting, fixes, optimizations, and infrastructure planning completed for Space360.

### 1. Refactored the Capture Upload Flow (Phase 3)
* **Component Extraction**: Cleaned up the massive `CapturesPage.tsx` file by extracting the upload UI into a dedicated, clean `CaptureUpload.tsx` component.
* **Pin Selection Logic**: Wired the upload modal to automatically fetch and display `LocationPoints` (pins) specifically for the currently selected project site.
* **Backend Wiring**: Updated the FastAPI backend (`POST /api/videos/ingest`) to accept the selected `pin_id` so that uploaded captures are correctly associated with floor plan pins in the database.

### 2. Fixed Frontend-to-Backend Routing (404 Errors)
* **API Configuration**: Fixed a major bug where the frontend was accidentally making requests to the React server (`localhost:3000`) instead of the FastAPI backend. Replaced raw `axios` calls with the centralized `api` interceptor to ensure all requests correctly route to `localhost:8000` with the proper authentication headers.
* **New Endpoints**: Created the `GET /sites/{site_id}/inspection-points` API endpoint using SQLAlchemy JOINs to fetch pins efficiently.

### 3. Resolved WebGL 360° Viewer Blocking (403 CORS Errors)
* **Cloud Storage Configuration**: Diagnosed an issue where the 360° image viewer was failing to render uploaded images due to Google Cloud Storage blocking the preflight requests. 
* **Applied Fix**: Created and applied a comprehensive CORS policy to the `360-field-check-media-sgb` bucket via the `gcloud` CLI, allowing the dashboard to load the heavy WebGL textures seamlessly.

### 4. Fixed Server Crashes & Windows Network Resolution Bugs
* **Attribute Error Fix**: Tracked down a silent backend crash where the system was querying `x_coord` and `y_coord` instead of `pin_x` and `pin_y` on the `LocationPoint` database model.
* **IPv4 vs IPv6 Binding**: Solved a frustrating "Network Error" where the React dashboard was silently failing to reach the backend. Windows was resolving `localhost` to an IPv6 address (`[::1]`), but the Python server was bound to IPv4. Fixed this by strictly routing all dashboard API traffic through `127.0.0.1` and binding `uvicorn` to `0.0.0.0`.

### 5. Production Infrastructure Planning
* **Domain Integration Plan**: Analyzed the new Vodien domain (`sgbapps.com`) and local architecture.
* **Migration Strategy**: Authored a detailed roadmap (`F:\Space360\docs\production_migration_plan.md`) outlining the precise steps required to move from the local SQLite database to Google Cloud SQL (PostgreSQL), deploy the FastAPI backend to Google Cloud Run, and host the React dashboard on Firebase Hosting so it can be securely linked to the custom domain.

### 6. Cloud Run Video Processor Optimizations (insta360-module)
* **2fps Optimization**: Based on the master roadmap, updated the `ffmpeg` video stitching command in `modules/insta360/core/stitcher.py` to extract only **2 frames per second** (`-r 2`) instead of full 30fps. This drastically reduces CPU load, memory usage, and file sizes.
* **Timeout Fix**: Increased the hardcoded `subprocess` timeout and the Cloud Run service timeout from 10 minutes to **60 minutes** (`3600s`) to prevent processing failures for large 4K files.
* **Deployment**: Built and deployed the updated `v2.0.8` Docker container to Google Cloud Run.
