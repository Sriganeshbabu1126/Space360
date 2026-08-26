from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.camera import CameraDetector
from core.validator import FileValidator
from core.metadata import MetadataExtractor
from config import config

router = APIRouter(prefix="/ingest", tags=["Ingest"])

class IngestRequest(BaseModel):
    source: str

@router.post("")
def ingest_video(request: IngestRequest):
    if request.source == "usb":
        detector = CameraDetector()
        detection_result = detector.detect()
        
        if detection_result["mode"] == "not_connected":
            raise HTTPException(status_code=404, detail=detection_result["message"])
            
        validator = FileValidator()
        validation_result = validator.validate_batch(detection_result["insv_files"])
        
        if validation_result["invalid"] > 0:
            raise HTTPException(status_code=422, detail=validation_result)
            
        transfer_result = detector.transfer_files(
            detection_result["insv_files"], 
            config.OUTPUT_DIR
        )
        
        extractor = MetadataExtractor()
        destination_files = [f["destination"] for f in transfer_result["files"] if f["status"] in ("copied", "skipped")]
        metadata_result = extractor.extract_batch(destination_files)
        
        return {
            "detection": detection_result,
            "validation": validation_result,
            "transfer": transfer_result,
            "metadata": metadata_result
        }
        
    return {"status": "received", "source": request.source}
