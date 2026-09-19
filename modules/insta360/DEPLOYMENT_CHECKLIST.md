# Deployment Checklist

- [x] Firestore permissions granted to service account `insta360-sa@space360-114433.iam.gserviceaccount.com` (role `roles/datastore.user`)
- [x] Updated `.env.example` with Firestore environment variables
- [x] Updated `.env.cloud-run` with Firestore environment variables
- [x] Verified `google-cloud-firestore` in `requirements.txt`
