# 360 Field Check — Backend API

## Setup

1. Copy .env.example to .env and fill in your values
2. Add your Firebase service account JSON as firebase-service-account.json
3. Install dependencies:
   pip install -r requirements.txt

## Run locally

   uvicorn main:app --reload --port 8000

## Run database migrations

   alembic revision --autogenerate -m "initial"
   alembic upgrade head

## API Docs (auto-generated)

   http://localhost:8000/docs

## Deploy to Cloud Run

   gcloud builds submit --tag gcr.io/YOUR_PROJECT/360-field-check-api
   gcloud run deploy 360-field-check-api \
     --image gcr.io/YOUR_PROJECT/360-field-check-api \
     --platform managed \
     --region asia-southeast1 \
     --allow-unauthenticated
