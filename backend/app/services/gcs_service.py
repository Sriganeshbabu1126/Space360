from google.cloud import storage
from app.config import settings
from PIL import Image
import io
import uuid
import os

client = storage.Client(project=settings.GOOGLE_CLOUD_PROJECT)
bucket = client.bucket(settings.GCS_BUCKET_NAME)

def upload_file(file_bytes: bytes, destination_path: str, 
                content_type: str = "image/jpeg") -> str:
    """Upload raw bytes to GCS and return public URL."""
    blob = bucket.blob(destination_path)
    blob.upload_from_string(file_bytes, content_type=content_type)
    blob.make_public()
    return blob.public_url

def upload_360_image(file_bytes: bytes, site_id: str, 
                     location_id: str, session_id: str) -> dict:
    """Upload a 360 image and auto-generate a thumbnail. 
    Returns dict with image_url and thumbnail_url."""
    
    try:
        # Upload full resolution image
        image_path = (f"sites/{site_id}/locations/{location_id}"
                      f"/sessions/{session_id}/image.jpg")
        image_url = upload_file(file_bytes, image_path, "image/jpeg")

        # Generate and upload thumbnail (800x400 equirectangular)
        img = Image.open(io.BytesIO(file_bytes))
        img.thumbnail((800, 400))
        thumb_bytes = io.BytesIO()
        img.save(thumb_bytes, format="JPEG", quality=75)
        thumb_bytes.seek(0)

        thumb_path = (f"sites/{site_id}/locations/{location_id}"
                      f"/sessions/{session_id}/thumbnail.jpg")
        thumbnail_url = upload_file(
            thumb_bytes.read(), thumb_path, "image/jpeg"
        )

        return {"image_url": image_url, "thumbnail_url": thumbnail_url}
    except Exception as e:
        print(f"GCS upload failed: {e}. Falling back to local storage.")
        os.makedirs("static/test-captures", exist_ok=True)
        
        # Save full resolution locally
        filename = f"{session_id}.jpg"
        local_path = os.path.join("static/test-captures", filename)
        with open(local_path, "wb") as f:
            f.write(file_bytes)
            
        # Save thumbnail locally
        img = Image.open(io.BytesIO(file_bytes))
        img.thumbnail((800, 400))
        thumb_filename = f"{session_id}_thumb.jpg"
        thumb_local_path = os.path.join("static/test-captures", thumb_filename)
        img.save(thumb_local_path, format="JPEG", quality=75)

        base_url = "http://localhost:8000/static/test-captures"
        return {
            "image_url": f"{base_url}/{filename}",
            "thumbnail_url": f"{base_url}/{thumb_filename}"
        }

def upload_floor_plan(file_bytes: bytes, site_id: str, 
                      floor_plan_id: str, 
                      content_type: str = "image/png") -> str:
    """Upload a floor plan image to GCS."""
    path = f"sites/{site_id}/floor-plans/{floor_plan_id}.png"
    return upload_file(file_bytes, path, content_type)

def upload_audio(file_bytes: bytes, site_id: str, 
                 session_id: str) -> str:
    """Upload a voice note audio file to GCS."""
    filename = f"{uuid.uuid4()}.m4a"
    path = f"sites/{site_id}/voice-notes/{session_id}/{filename}"
    return upload_file(file_bytes, path, "audio/mp4")

def delete_file(gcs_url: str):
    """Delete a file from GCS by its public URL."""
    blob_name = "/".join(gcs_url.split("/")[4:])
    blob = bucket.blob(blob_name)
    if blob.exists():
        blob.delete()
