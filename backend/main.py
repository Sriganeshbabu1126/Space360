from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import sites, projects, floor_plans, locations, sessions, \
                        voice_notes, annotations, ai_features, contractors, issues, dashboard, paths, video, correlation
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

from fastapi.staticfiles import StaticFiles
import os
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.services.audit_logger import audit_logger
import firebase_admin.auth as firebase_auth

os.makedirs("static/floor-plans", exist_ok=True)

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        
        # Only log write operations
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            user_email = "anonymous"
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                try:
                    decoded = firebase_auth.verify_id_token(token, clock_skew_seconds=60)
                    user_email = decoded.get("email", "unknown")
                except Exception:
                    pass
            
            # Map path to resource type and action
            path = request.url.path
            method = request.method
            action = f"{method}_{path.split('/')[1].upper()}" if len(path.split('/')) > 1 else method
            
            audit_logger.log_action(
                user_id=user_email,
                user_name=user_email,
                action=action,
                resource_type=path.split('/')[1].upper() if len(path.split('/')) > 1 else "UNKNOWN",
                resource_id="",
                resource_name=path,
                project_id="",
                ip_address=request.client.host if request.client else None,
                status="SUCCESS" if response.status_code < 400 else "FAILURE"
            )
            
        return response

app = FastAPI(title="360 Field Check API", version="1.0.0")

app.add_middleware(AuditMiddleware)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://sgbapps.com",
        "https://www.sgbapps.com",
        "https://space360-production.web.app",
        "https://space360.sgbapps.com",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sites.router, prefix="/sites", tags=["Sites"])
app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(floor_plans.router, prefix="/floor-plans", 
                   tags=["Floor Plans"])
app.include_router(locations.router, prefix="/locations", 
                   tags=["Locations"])
app.include_router(sessions.router, prefix="/sessions", 
                   tags=["Sessions"])
app.include_router(voice_notes.router, prefix="/voice-notes", 
                   tags=["Voice Notes"])
app.include_router(annotations.router, prefix="/annotations", 
                   tags=["Annotations"])
app.include_router(ai_features.router, prefix="/ai", 
                   tags=["AI Features"])
app.include_router(contractors.router, prefix="/contractors", 
                   tags=["Contractors"])
app.include_router(issues.router, prefix="/issues", 
                   tags=["Issues"])
app.include_router(dashboard.router, prefix="/dashboard", 
                   tags=["Dashboard"])
app.include_router(paths.router, prefix="/api", tags=["Paths"])
from app.routers import insta360_videos
app.include_router(insta360_videos.router, prefix="/api", tags=["videos"])
app.include_router(video.router)
app.include_router(correlation.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "360-field-check-api"}
