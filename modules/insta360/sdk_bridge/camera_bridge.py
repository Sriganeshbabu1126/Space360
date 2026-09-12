"""
Python wrapper for CameraSDK C++ calls.
"""
import os
import logging
from config import config

logger = logging.getLogger("insta360.sdk_bridge")

class CameraBridge:
    """
    Python bridge to the Insta360 CameraSDK (C++ library).
    Currently stubbed — Android/SDK mode not yet confirmed on hardware.
    Will be wired to the actual DLL/binary once firmware is updated.
    """

    def is_sdk_available(self) -> bool:
        """
        Check if the CameraSDK DLL/binary is accessible at the path
        defined in config.SDK_CAMERA_PATH.
        Returns True if found, False otherwise.
        Check for the presence of CameraSDK.dll (Windows) in the SDK lib folder.
        """
        dll_path = os.path.join(config.SDK_CAMERA_PATH, "lib", "CameraSDK.dll")
        is_available = os.path.isfile(dll_path)
        if not is_available:
            logger.warning(f"CameraSDK.dll not found at {dll_path}")
        else:
            logger.info(f"CameraSDK.dll found at {dll_path}")
        return is_available

    def connect(self) -> dict:
        """
        Attempt to connect to camera via CameraSDK.
        Currently returns a stub response indicating SDK mode is not yet active.
        Returns: {"connected": False, "reason": "Android mode not yet enabled on hardware"}
        """
        logger.info("Attempting to connect via CameraSDK (Stub)")
        return {"connected": False, "reason": "Android mode not yet enabled on hardware"}
