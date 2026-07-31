from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import sites, floor_plans, locations, sessions, \
                        voice_notes, annotations, ai_features
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="360 Field Check API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sites.router, prefix="/sites", tags=["Sites"])
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

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "360-field-check-api"}
