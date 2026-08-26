"""
Responsible for USB camera detection and file transfer.
"""
import os
import subprocess
import logging
import shutil
import json
import re
from datetime import datetime, timezone
from sdk_bridge.camera_bridge import CameraBridge

logger = logging.getLogger("insta360.camera")

class CameraDetector:
    """
    Detects Insta360 X4 connected via USB and determines connection mode.
    Supports USB Storage mode (direct file access) and Android mode (SDK control).
    Note: Uses Windows-only 'wmic' command for drive detection.
    """

    def __init__(self):
        self.bridge = CameraBridge()

    def detect(self) -> dict:
        """
        Scan all connected drives on Windows using the 'wmic' command.
        For each removable drive, check if a DCIM folder exists.
        If found, look for .insv files inside DCIM\\ or DCIM\\Camera\\.
        
        Returns a dict:
        {
          "mode": "usb_storage" | "android" | "not_connected",
          "drive": "D:\\" | None,
          "insv_files": ["D:\\DCIM\\Camera\\VID_001.insv", ...] | [],
          "file_count": int,
          "message": str
        }
        """
        logger.info("Starting camera detection")
        result = {
            "mode": "not_connected",
            "drive": None,
            "insv_files": [],
            "file_count": 0,
            "message": "No Insta360 camera detected"
        }

        # Check Android mode first (stubbed)
        if self._check_android_mode():
            logger.info("Camera detected in Android/SDK mode")
            result["mode"] = "android"
            result["message"] = "Camera detected in Android mode"
            return result

        # Check USB Storage Mode
        try:
            logger.info("Scanning for removable drives via wmic")
            output = subprocess.check_output(
                ["wmic", "logicaldisk", "where", "drivetype=2", "get", "deviceid"],
                text=True
            )
            
            drives = [line.strip() + "\\" for line in output.splitlines() if line.strip() and "DeviceID" not in line]
            logger.info(f"Found removable drives: {drives}")
            
            for drive in drives:
                dcim_path = os.path.join(drive, "DCIM")
                if os.path.isdir(dcim_path):
                    logger.info(f"DCIM folder found on {drive}")
                    try:
                        insv_files = self.list_insv_files(drive)
                        if insv_files:
                            result["mode"] = "usb_storage"
                            result["drive"] = drive
                            result["insv_files"] = insv_files
                            result["file_count"] = len(insv_files)
                            result["message"] = f"Camera detected in USB storage mode on {drive}"
                            logger.info(f"Found {len(insv_files)} .insv files on {drive}")
                            return result
                        else:
                            logger.info(f"DCIM folder found on {drive}, but no .insv files present.")
                    except PermissionError:
                        logger.error(f"Permission error accessing {drive}")
                    except Exception as e:
                        logger.error(f"Error accessing {drive}: {e}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to execute wmic command: {e}")
        except FileNotFoundError:
            logger.error("wmic command not found. Are you running on Windows?")
            
        logger.warning("No camera found in USB storage mode")
        return result

    def list_insv_files(self, drive: str) -> list[str]:
        """
        Given a drive letter (e.g. "D:\\"),
        recursively scan DCIM folder for all .insv files.
        Return list of absolute file paths.
        """
        insv_files = []
        dcim_path = os.path.join(drive, "DCIM")
        if not os.path.isdir(dcim_path):
            return insv_files

        for root, _, files in os.walk(dcim_path):
            for file in files:
                if file.lower().endswith(".insv"):
                    insv_files.append(os.path.join(root, file))
        return insv_files

    def _check_android_mode(self) -> bool:
        """
        Use CameraBridge.is_sdk_available() to check if SDK mode is possible.
        Returns False for now — placeholder for future Android mode detection.
        """
        if self.bridge.is_sdk_available():
            conn_status = self.bridge.connect()
            if conn_status.get("connected"):
                return True
        return False
        
    def _parse_date_from_filename(self, filename: str) -> str:
        """
        Extract YYYYMMDD from filename like VID_20260826_123606_00_004.insv
        Returns date string e.g. "20260826"
        Falls back to today's date if parsing fails.
        Uses regex for robustness.
        """
        match = re.search(r"VID_(\d{8})_", os.path.basename(filename))
        if match:
            return match.group(1)
        return datetime.now().strftime("%Y%m%d")

    def _verify_integrity(self, source: str, destination: str) -> bool:
        """
        Compare file sizes of source and destination.
        Returns True if sizes match, False otherwise.
        Log a warning if sizes differ.
        """
        try:
            src_size = os.path.getsize(source)
            dst_size = os.path.getsize(destination)
            if src_size == dst_size:
                return True
            else:
                logger.warning(f"Integrity check failed: source size {src_size} != destination size {dst_size}")
                return False
        except OSError as e:
            logger.error(f"Integrity check error for {source} and {destination}: {e}")
            return False

    def transfer_files(self, insv_files: list[str], output_dir: str) -> dict:
        """
        Copy .insv files from camera to local output staging area.
        """
        result = {
            "total": len(insv_files),
            "copied": 0,
            "skipped": 0,
            "overwritten": 0,
            "failed": 0,
            "files": []
        }
        
        manifests = {} # key: date string, value: list of file result dicts
        source_drive = None
        
        for source in insv_files:
            if source_drive is None:
                source_drive = os.path.splitdrive(source)[0] + "\\"
                
            file_result = {
                "source": source,
                "destination": None,
                "status": "failed",
                "source_size_bytes": None,
                "destination_size_bytes": None,
                "integrity": "skipped",
                "error": None
            }
            
            try:
                date_str = self._parse_date_from_filename(source)
                dest_dir = os.path.join(output_dir, date_str)
                os.makedirs(dest_dir, exist_ok=True)
                
                filename = os.path.basename(source)
                destination = os.path.join(dest_dir, filename)
                file_result["destination"] = destination
                
                src_size = os.path.getsize(source)
                file_result["source_size_bytes"] = src_size
                
                if os.path.exists(destination):
                    dst_size = os.path.getsize(destination)
                    if src_size == dst_size:
                        file_result["status"] = "skipped"
                        file_result["destination_size_bytes"] = dst_size
                        result["skipped"] += 1
                        logger.info(f"Skipped duplicate file: {source}")
                    else:
                        shutil.copy2(source, destination)
                        file_result["status"] = "overwritten"
                        file_result["destination_size_bytes"] = os.path.getsize(destination)
                        result["overwritten"] += 1
                        logger.warning(f"Overwritten file with different size: {destination}")
                else:
                    shutil.copy2(source, destination)
                    file_result["status"] = "copied"
                    file_result["destination_size_bytes"] = os.path.getsize(destination)
                    result["copied"] += 1
                    logger.info(f"Copied file: {source} to {destination}")
                    
                if file_result["status"] in ["copied", "overwritten"]:
                    if self._verify_integrity(source, destination):
                        file_result["integrity"] = "ok"
                    else:
                        file_result["integrity"] = "failed"
                        
            except Exception as e:
                file_result["status"] = "failed"
                file_result["error"] = str(e)
                result["failed"] += 1
                logger.error(f"Failed to transfer {source}: {e}")
                
            result["files"].append(file_result)
            
            if date_str not in manifests:
                manifests[date_str] = []
            manifests[date_str].append(file_result)
            
        # Write manifests
        for date_str, files_list in manifests.items():
            manifest_path = os.path.join(output_dir, date_str, "transfer_manifest.json")
            manifest_data = {
                "transfer_timestamp": datetime.now(timezone.utc).isoformat(),
                "source_drive": source_drive or "Unknown",
                "module": "insta360-handler",
                "space360_project": "Space360",
                "total_files": len(files_list),
                "copied": sum(1 for f in files_list if f["status"] == "copied"),
                "skipped": sum(1 for f in files_list if f["status"] == "skipped"),
                "overwritten": sum(1 for f in files_list if f["status"] == "overwritten"),
                "failed": sum(1 for f in files_list if f["status"] == "failed"),
                "files": files_list
            }
            try:
                with open(manifest_path, "w", encoding="utf-8") as f:
                    json.dump(manifest_data, f, indent=2)
            except Exception as e:
                logger.error(f"Failed to write manifest at {manifest_path}: {e}")
                
        return result
