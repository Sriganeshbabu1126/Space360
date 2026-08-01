---

# Space360 — Project Specification

Developed by: SGB Dev Apps

## Overview
A construction site progress monitoring app that mimics OpenSpace AI, 
with additional AI features powered by Google Gemini via the user's 
Google AI Pro account.

Field crews use a mobile app (iOS + Android) to capture periodic 360° 
images at fixed location points on a construction site. A web dashboard 
lets project managers compare captures across dates, annotate issues, 
and query the site using natural language.

---

## Authentication
- Google Sign-In (OAuth 2.0) for all users
- Google AI Pro account login gates access to all AI features
- Firebase Authentication handles session tokens
- Role-based access: Owner, Project Manager, Field Crew, Client (view only)

---

## AI Features (on-demand, via Google AI Pro)
All AI features call Gemini API using the authenticated user's 
Google AI Pro credentials. Features are disabled if user is not 
signed in with a Google AI Pro account.

1. **Change Detection** — Compare two 360° captures, return a JSON 
   list of detected changes with region descriptions
2. **Progress Estimation** — Estimate % completion per zone vs baseline
3. **Natural Language Site Q&A** — RAG over all capture metadata 
   and voice transcripts; answer questions like 
   "show me where plumbing was done last week"
4. **Voice Note Transcription** — Transcribe field crew audio notes, 
   auto-extract issues and materials mentioned

---

## Storage
- Google Cloud Storage (GCS) linked to user's Google AI Pro / 
  Google Cloud account
- Bucket name: `360-field-check-media`
- Folder structure:
  /sites/{site_id}/floor-plans/{filename}
  /sites/{site_id}/locations/{location_id}/sessions/{date}/{filename}
  /sites/{site_id}/voice-notes/{session_id}/{filename}

---

## Data Models

### Site
- id (uuid), name, address, gps_bounds (JSON), org_id, 
  created_by, status (active/archived), created_at

### FloorPlan
- id (uuid), site_id (FK), label (e.g. "Level 2"), 
  image_url (GCS), uploaded_at

### LocationPoint
- id (uuid), floor_plan_id (FK), label, pin_x (%), pin_y (%), 
  gps_lat, gps_lng, heading (compass degrees), created_at

### CaptureSession
- id (uuid), location_point_id (FK), captured_at, image_url (GCS),
  thumbnail_url (GCS), captured_by (user_id), device_model,
  gps_lat, gps_lng, ai_status (pending/processing/done/error),
  ai_summary (text), ai_changes (JSON), created_at

### VoiceNote
- id (uuid), session_id (FK), audio_url (GCS), transcript (text),
  ai_tags (JSON array of extracted issues/materials), created_at

### Annotation
- id (uuid), session_id (FK), created_by (user_id), 
  yaw (degrees), pitch (degrees), comment (text), 
  severity (info/warning/critical), resolved (bool), created_at

---

## Tech Stack

### Mobile App
- React Native (Expo)
- Insta360 SDK or Ricoh Theta SDK (WiFi connection)
- Firebase Auth
- Offline-first: captures queue locally, sync on WiFi

### Backend API
- Python FastAPI on Google Cloud Run
- PostgreSQL on Google Cloud SQL
- SQLAlchemy ORM + Alembic migrations
- Google Cloud Storage SDK for file uploads
- Google Gemini API (gemini-1.5-pro-vision) for AI features
- Firebase Admin SDK for auth token verification

### Web Dashboard
- React + Tailwind CSS
- Pannellum.js for 360° image rendering
- Firebase Auth (Google Sign-In)
- Hosted on Firebase Hosting or Cloud Run

---

## API Base URL
- Development: http://localhost:8000
- Production: https://api.360fieldcheck.com

---

## Environment Variables Required
GOOGLE_CLOUD_PROJECT=
GOOGLE_APPLICATION_CREDENTIALS=
GCS_BUCKET_NAME=360-field-check-media
GEMINI_API_KEY=
FIREBASE_PROJECT_ID=
DATABASE_URL=
JWT_SECRET=

---

## MVP Scope (Phases 1–4)
Phase 1: Mobile capture + GCS upload + floor plan pin
Phase 2: Web dashboard + 360 viewer + timeline comparison
Phase 3: AI change detection + progress estimation
Phase 4: Team collaboration + annotations + reports

---
