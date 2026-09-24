# Space360 Production Cloud Migration Plan

## Current Architecture (Local Development)
- **Frontend**: React Dashboard running locally (`http://localhost:3000`) via `npm start`.
- **Backend API**: FastAPI running locally (`http://127.0.0.1:8000`) via `uvicorn`.
- **Database**: Local SQLite file (`space360.db`) on the developer's Windows machine.
- **Worker Module**: Python Insta360 video processor running in Google Cloud Run.
- **Storage/Auth**: Google Cloud Storage (`360-field-check-media-sgb`) and Firebase Authentication.

## Target Production Architecture
- **Domain**: `sgbapps.com` (DNS managed via Vodien)
- **Frontend**: Firebase Hosting (mapped to `https://sgbapps.com` and `https://www.sgbapps.com`)
- **Backend API**: Google Cloud Run (mapped to `https://api.sgbapps.com`)
- **Database**: Google Cloud SQL for PostgreSQL (managed database, automatically backed up and scales)

---

## Migration Steps

### Phase 1: Database Migration to Cloud SQL
Currently, the backend stores user data (projects, floor plans, pins, etc.) in a local SQLite file. Cloud Run instances are ephemeral (they scale up to 10 instances and scale down to 0, destroying local files in the process). If we deploy now, the database will be wiped out constantly.
1. Enable the Cloud SQL Admin API in Google Cloud (`space360-114433`).
2. Provision a new **Cloud SQL PostgreSQL instance** (e.g., `db-f1-micro` or `db-g1-small` for cost efficiency).
3. Update the FastAPI `app/database.py` and Alembic configuration to connect to the PostgreSQL database using the `pg8000` or `psycopg2` driver.
4. Run Alembic migrations to generate the schema in Cloud SQL.
5. *(Optional but recommended)* Export the current `space360.db` data and import it into PostgreSQL so we don't lose the test data.

### Phase 2: Deploying the Backend API to Cloud Run
1. Create a `Dockerfile` for the FastAPI backend if it doesn't already exist (or verify the existing one).
2. Configure Cloud Build to push the container to Google Artifact Registry.
3. Deploy the container to **Google Cloud Run** (`space360-backend`).
4. Inject environment variables (Firebase config, Cloud SQL connection string, etc.) into the Cloud Run service via Google Cloud Secret Manager or direct env vars.
5. Set the IAM policy on the Cloud Run service to allow unauthenticated invocations (`roles/run.invoker` for `allUsers`) since the API handles its own JWT bearer token auth via Firebase.

### Phase 3: Deploying the Frontend Dashboard
1. Update `REACT_APP_API_URL` in the React dashboard's `.env.production` to point to the new Cloud Run URL (or `https://api.sgbapps.com`).
2. Build the production React app (`npm run build`).
3. Initialize Firebase Hosting (`firebase init hosting`) in the `dashboard` directory.
4. Deploy the build folder to Firebase Hosting (`firebase deploy --only hosting`).

### Phase 4: Connecting the Custom Domain (Vodien DNS)
1. In the Firebase Console, go to **Hosting** -> **Add Custom Domain** and enter `sgbapps.com`. Firebase will provide an `A` record (e.g., `199.36.158.100`).
2. In Google Cloud Run, go to **Manage Custom Domains**, add a domain mapping for the backend service, and map it to `api.sgbapps.com`. Google will provide a `CNAME` or `A`/`AAAA` records.
3. Log in to the **Vodien DNS Management Panel** and configure:
   - `A` Record for `@` (sgbapps.com) pointing to the Firebase IP.
   - `CNAME` Record for `www` pointing to `sgbapps.com`.
   - `CNAME` or `A` Record for `api` pointing to the Google Cloud Run endpoint.
4. Wait 1-24 hours for DNS propagation and for Google to automatically provision free SSL certificates.

---

## Technical Considerations for Claude
- **CORS**: We recently fixed a CORS issue with GCS WebGL textures. We will need to ensure the FastAPI backend's `CORSMiddleware` is updated to allow `https://sgbapps.com` instead of just `*` or `localhost` for production security.
- **Service Accounts**: The Cloud Run backend will need a Service Account with permissions for Cloud SQL Client (`roles/cloudsql.client`), GCS Admin (`roles/storage.objectAdmin`), and Firebase Admin.
- **SQLAlchemy compatibility**: The current SQLite syntax might need minor tweaks if there are SQLite-specific column types (like JSON vs JSONB), though basic SQLAlchemy `String`, `Float`, and `DateTime` columns will translate to PostgreSQL perfectly.
