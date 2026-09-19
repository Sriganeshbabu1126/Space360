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

## IAM Setup
To ensure the Cloud Run service account has the necessary permissions to access Firestore, run the following command:
```bash
gcloud projects add-iam-policy-binding space360-114433 --member="serviceAccount:insta360-sa@space360-114433.iam.gserviceaccount.com" --role="roles/datastore.user"
```

## Firestore Cost Estimate
Firestore is a NoSQL document database, and its pricing is based on reads, writes, deletes, and storage.
- **Free Tier (per day):** 50,000 reads, 20,000 writes, 20,000 deletes, 1 GB storage.
- **Beyond Free Tier:**
  - $0.06 per 100,000 reads
  - $0.18 per 100,000 writes
  - $0.02 per 100,000 deletes
  - $0.108 per GB/month storage
Given the typical workload of storing job metadata, the cost is expected to remain within or very close to the free tier limits.
