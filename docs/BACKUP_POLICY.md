# Space360 Backup & Retention Policy

## 1. Cloud SQL (PostgreSQL)
- **Automated Backups**: Enabled. Daily backups run automatically.
- **Retention**: 7 days of automated backups.
- **Point-in-Time Recovery (PITR)**: Enabled. Allows recovery to any specific second within the last 7 days.
- **High Availability**: Regional configuration enabled (multi-zone).

## 2. Google Cloud Storage (Media Bucket)
- **Object Versioning**: Enabled on `360-field-check-media-sgb`. Every time a file is overwritten or deleted, a non-current version is retained.
- **Lifecycle Policy**:
  - Non-current versions (overwritten/deleted files) are permanently deleted after **30 days** to save costs.
  - Original capture files (.insv) are transitioned to Nearline storage after 90 days.

## 3. Firestore
- **Scheduled Backups**: Automated exports are configured to run daily via Cloud Scheduler and Cloud Functions, saving to `gs://space360-114433-firestore-backups`.
- **Retention**: 30 days of daily backups in GCS.

## 4. Source Code & Artifacts
- **GitHub**: All source code is version controlled. Main branch requires PR reviews.
- **Artifact Registry**: Docker images for Cloud Run are retained for the last 10 versions. Older versions are pruned.
