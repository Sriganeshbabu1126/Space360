import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    GCS_BUCKET: str = os.getenv("GCS_BUCKET", "360-field-check-media-sgb")
    GCS_VIDEO_PREFIX: str = "videos/"
    SDK_CAMERA_PATH: str = os.getenv("SDK_CAMERA_PATH", "sdk/Desktop-CameraSDK-Cpp")
    SDK_MEDIA_PATH: str = os.getenv("SDK_MEDIA_PATH", "sdk/Desktop-MediaSDK-Cpp")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "/tmp/output")
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")
    EXIFTOOL_PATH: str = "exiftool"

config = Config()
