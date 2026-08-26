import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    GCS_BUCKET: str = os.getenv("GCS_BUCKET", "360-field-check-media-sgb")
    GCS_VIDEO_PREFIX: str = "videos/"
    SDK_CAMERA_PATH: str = r"F:\Space360\modules\insta360\sdk\Desktop-CameraSDK-Cpp"
    SDK_MEDIA_PATH: str = r"F:\Space360\modules\insta360\sdk\Desktop-MediaSDK-Cpp"
    OUTPUT_DIR: str = r"F:\Space360\modules\insta360\output"
    LOG_DIR: str = r"F:\Space360\modules\insta360\logs"
    EXIFTOOL_PATH: str = "exiftool"

config = Config()
