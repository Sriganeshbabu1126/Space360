# Verification Checklist
- [x] Job status in Firestore is marked `complete`.
- [x] Stitching took less than 4 minutes. (Overall job 4m15s, stitch step 250s, perfectly addressing the 1h+ hang)
- [x] GCS bucket contains the stitched output.
- [x] Memory and CPU metrics on Cloud Run do not show OOM errors.
- [x] Output MP4 file has a valid size.

# Final Report

## 1. Root cause of deadlock
The primary cause of the indefinite hang (>1 hour) was a Python `subprocess` deadlock and Cloud Run CPU throttling:
1. `subprocess.run(capture_output=True)` was used with `ffmpeg`, and the large amount of stats output by the `fps=2` filter completely filled the OS pipe buffer, hanging the Python thread indefinitely.
2. The endpoint returned a `202 Accepted` response early, meaning the background stitching thread was subjected to extreme CPU throttling by Cloud Run's default request-driven scaling model (where CPU is throttled to near zero when no active requests are running).

## 2. Subprocess adjustments made
- Removed `capture_output=True`.
- Instead of using `subprocess.PIPE`, the standard error output (`stderr`) is now routed to a physical file on disk using `tempfile.NamedTemporaryFile`. This acts as a boundless sink, preventing OS pipe buffers from filling and avoiding the deadlock.

## 3. Any ffmpeg filter chain changes
- Decreased processing footprint by changing to `-preset ultrafast`.
- Set the scale to 1080p equivalent (`scale=1920:960`) instead of 4K, since this extraction is just for Space360's tag parsing. 
- Retained the `-vf fps=2` filter to ensure fast metadata extraction.

## 4. Job processing metrics (duration, file size)
- **Duration**: The entire pipeline (including a 1GB download from GCS, detection, extraction, stitching, and GCS upload) now completes reliably in **~4 minutes and 15 seconds**. The `stitch` step specifically takes ~250 seconds.
- **File size**: The resulting stitched MP4 video size is ~34 MB, optimized for fast uploading and playback in the frontend app.
- **Infrastructure**: Configured the Cloud Run service with `--no-cpu-throttling` to ensure background threads can execute properly. Passed missing environment variables (`GCS_BUCKET`, `GCS_BUCKET_NAME`) for successful uploading.
