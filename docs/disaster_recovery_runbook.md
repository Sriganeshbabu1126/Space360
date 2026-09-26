# Space360 Disaster Recovery Runbook

This runbook outlines the procedures for recovering the Space360 application components in the event of a critical failure or data loss.

## Incident Escalation
If a critical outage occurs (e.g. database dropped, Cloud Run deleted):
1. **P1 Alert Triggered** via Google Cloud Monitoring (email/SMS to admins).
2. Follow steps below based on the impacted system.

---

## 1. Cloud SQL (PostgreSQL) Recovery

**Scenario**: Accidental data deletion, corrupted tables, or dropped database.

### 1.1 Restore from Automated Backup
Cloud SQL is configured with automated daily backups.
1. Go to Google Cloud Console > SQL > `space360-prod-db`.
2. Click **Backups**.
3. Select the most recent successful backup.
4. Click **Restore**. Note: This will overwrite the current instance state and cause downtime.

### 1.2 Point-in-Time Recovery (PITR)
If you need to recover to a specific minute (e.g., right before a bad migration):
1. PITR must be enabled (Verify via `gcloud sql instances describe space360-prod-db`).
2. Run the restore command (clone to a new instance for safety):
```bash
gcloud sql instances clone space360-prod-db space360-prod-db-recovery \
    --point-in-time="2026-09-26T12:00:00.000Z"
```
3. Update backend `DATABASE_URL` secret to point to `space360-prod-db-recovery`.

---

## 2. GCS Media Bucket Recovery

**Scenario**: Deleted 360 videos or floor plans.

### 2.1 Object Versioning Recovery
The `360-field-check-media-sgb` bucket has Object Versioning enabled.
If a file is overwritten or deleted, you can restore a previous version.
1. List all versions of a deleted file:
```bash
gsutil ls -a gs://360-field-check-media-sgb/path/to/file.mp4
```
2. Copy the specific generation ID back to the main file name:
```bash
gsutil cp gs://360-field-check-media-sgb/path/to/file.mp4#123456789 gs://360-field-check-media-sgb/path/to/file.mp4
```

---

## 3. Firestore Recovery

**Scenario**: Audit logs or job state lost.

### 3.1 Scheduled Exports
Firestore is exported weekly/daily to GCS bucket `gs://space360-114433-firestore-backups`.
To restore from the latest export:
1. Locate the latest backup folder in GCS.
2. Run the import command:
```bash
gcloud firestore import gs://space360-114433-firestore-backups/2026-09-26T00:00:00_5641/
```

---

## 4. Cloud Run / Compute Recovery

**Scenario**: Cloud Run service deleted or region outage.
1. The images are safely stored in Artifact Registry.
2. Re-deploy the latest image to another region if necessary:
```bash
gcloud run deploy space360-backend \
  --image=asia-southeast1-docker.pkg.dev/space360-114433/space360/backend:latest \
  --region=asia-east1 \
  --platform=managed
```
