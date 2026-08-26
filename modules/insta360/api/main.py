from fastapi import FastAPI, HTTPException
from api.routes import ingest
from core.camera import CameraDetector
from core.metadata import MetadataExtractor
import os

app = FastAPI(title="Insta360 X4 Video Handling Module")

app.include_router(ingest.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "module": "insta360-handler"}

@app.get("/camera/detect")
def detect_camera():
    detector = CameraDetector()
    return detector.detect()

@app.get("/metadata")
def get_metadata(filepath: str):
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File does not exist")
    if not filepath.lower().endswith(".insv"):
        raise HTTPException(status_code=422, detail="File must be a .insv file")
        
    extractor = MetadataExtractor()
    return extractor.extract(filepath)
