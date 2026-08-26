"""
Responsible for GPS/IMU/heading extraction via SDK + exiftool.
"""
import os
import json
import logging
from datetime import datetime
import subprocess
logger = logging.getLogger("insta360.metadata")

class MetadataExtractor:
    """
    Extracts and normalises metadata from Insta360 X4 .insv files.
    Uses exiftool as primary source and Insta360 SDK as secondary (stubbed).
    """

    def extract(self, filepath: str) -> dict:
        """
        Run full metadata extraction on a single .insv file.
        """
        logger.info(f"Starting metadata extraction for {filepath}")
        os.makedirs(r"F:\Space360\modules\insta360\logs", exist_ok=True)
        with open(r"F:\Space360\modules\insta360\logs\metadata_debug.log", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] Starting extract for {filepath}\n")
        result = {
            "filepath": filepath,
            "sidecar_path": None,
            "extraction_status": "failed",
            "metadata": {
                "camera": {
                    "make": None,
                    "model": None,
                    "firmware": None,
                    "serial": None
                },
                "capture": {
                    "timestamp_utc": None,
                    "duration_seconds": None,
                    "timezone": None
                },
                "video": {
                    "width": None,
                    "height": None,
                    "frame_rate": None,
                    "bitrate_bps": None,
                    "codec": None,
                    "projection": None
                },
                "gps": {
                    "available": False,
                    "latitude": None,
                    "longitude": None,
                    "altitude_m": None,
                    "track_points": None
                },
                "imu": {
                    "available": False,
                    "source": "none",
                    "gyroscope": None,
                    "accelerometer": None
                },
                "file": {
                    "filename": os.path.basename(filepath),
                    "size_bytes": None,
                    "format": ".insv"
                }
            },
            "raw_exiftool": {},
            "warnings": [],
            "errors": []
        }
        
        if not os.path.exists(filepath):
            result["errors"].append("File does not exist")
            return result
            
        if not filepath.lower().endswith(".insv"):
            result["errors"].append("File is not .insv format")
            return result
            
        try:
            result["metadata"]["file"]["size_bytes"] = os.path.getsize(filepath)
        except OSError as e:
            result["errors"].append(f"Failed to read file size: {e}")
            return result
        
        try:
            # 2. Extract with exiftool
            raw_exiftool, et_status, et_error = self._extract_exiftool(filepath)
            if et_error:
                result["errors"].append(f"Exiftool extraction failed: {et_error}")
                if et_status == "failed":
                    return result
                    
            result["raw_exiftool"] = raw_exiftool
            
            # 3. Extract with SDK (stub)
            raw_sdk = self._extract_sdk(filepath)
            
            # 4. Normalise
            self._normalise(result, raw_exiftool, raw_sdk)
            
            # Determine overall status
            if not result["errors"] and not result["warnings"]:
                result["extraction_status"] = "success"
            elif result["errors"]:
                result["extraction_status"] = "failed"
            else:
                result["extraction_status"] = "partial"
                
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            with open(r"F:\Space360\modules\insta360\logs\metadata_debug.log", "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().isoformat()}] Exception in extract:\n{tb}\n")
            logger.error(f"Unexpected error in extract() for {filepath}: {e}\n{tb}")
            result["errors"].append(f"Unexpected exception: {str(e)} | Traceback: {tb}")
            result["extraction_status"] = "failed"
            
        # 5. Write sidecar JSON
        base = os.path.splitext(filepath)[0]
        sidecar_path = f"{base}_metadata.json"
        result["sidecar_path"] = sidecar_path
        
        sidecar_content = result.copy()
        sidecar_content.pop("raw_exiftool", None)
        
        try:
            with open(sidecar_path, "w", encoding="utf-8") as f:
                json.dump(sidecar_content, f, indent=2)
            logger.info(f"Metadata extraction complete for {filepath}. Sidecar: {sidecar_path}")
        except Exception as e:
            logger.error(f"Failed to write sidecar for {filepath}: {e}")
            result["errors"].append(f"Failed to write sidecar: {e}")
            result["extraction_status"] = "failed"
            
        with open(r"F:\Space360\modules\insta360\logs\metadata_debug.log", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] Extract complete for {filepath}, status: {result['extraction_status']}\n")
            
        return result

    def _extract_exiftool(self, filepath: str) -> tuple[dict, str, str]:
        """
        Use subprocess to extract metadata via exiftool.
        """
        debug_log = r"F:\Space360\modules\insta360\logs\metadata_debug.log"
        
        try:
            # Log the call
            with open(debug_log, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().isoformat()}] Calling exiftool on {filepath}\n")
                f.flush()
            
            # Run exiftool
            result = subprocess.run(
                [r"F:\exiftool\exiftool.exe", "-json", filepath],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Log success immediately
            with open(debug_log, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().isoformat()}] Exiftool returned with code {result.returncode}\n")
                f.flush()
            
            if result.returncode != 0:
                error_msg = f"exiftool exited with code {result.returncode}: {result.stderr}"
                with open(debug_log, "a", encoding="utf-8") as f:
                    f.write(f"[{datetime.now().isoformat()}] ERROR: {error_msg}\n")
                    f.flush()
                return {}, "failed", error_msg
            
            # Parse JSON
            data = json.loads(result.stdout)
            with open(debug_log, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().isoformat()}] JSON parsed successfully, {len(data)} objects\n")
                f.flush()
            
            if data:
                return data[0], "success", ""
            else:
                return {}, "failed", "JSON data is empty"
            
        except FileNotFoundError as e:
            msg = f"exiftool executable not found on PATH: {e}"
            with open(debug_log, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().isoformat()}] ERROR FileNotFoundError: {msg}\n")
                f.flush()
            return {}, "failed", msg
            
        except subprocess.TimeoutExpired as e:
            msg = f"exiftool timed out after 10 seconds"
            with open(debug_log, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().isoformat()}] ERROR TimeoutExpired: {msg}\n")
                f.flush()
            return {}, "failed", msg
            
        except json.JSONDecodeError as e:
            msg = f"Failed to parse exiftool JSON output: {e}"
            with open(debug_log, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().isoformat()}] ERROR JSONDecodeError: {msg}\n")
                f.flush()
            return {}, "failed", msg
            
        except Exception as e:
            msg = f"Unexpected exception: {type(e).__name__}: {e}"
            with open(debug_log, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().isoformat()}] ERROR {type(e).__name__}: {msg}\n")
                f.flush()
            return {}, "failed", msg

    def _extract_sdk(self, filepath: str) -> dict:
        """
        Stub for Insta360 SDK metadata extraction.
        """
        return {
            "imu_available": False,
            "gyroscope": None,
            "accelerometer": None,
            "note": "SDK extraction stubbed — MediaSDK bridge not yet implemented"
        }

    def _normalise(self, result: dict, raw_et: dict, raw_sdk: dict):
        """
        Map raw exiftool tags and SDK data into the normalised schema.
        """
        def get_tag(tags, default=None):
            for t in tags:
                for k, v in raw_et.items():
                    if k == t or k.endswith(f":{t}"):
                        return v
            return default

        # Map camera
        make = get_tag(["Make"])
        model = get_tag(["Model"])
        fw = get_tag(["FirmwareVersion", "Software"])
        serial = get_tag(["SerialNumber"])
        result["metadata"]["camera"] = {"make": make, "model": model, "firmware": fw, "serial": serial}
        
        if not make: logger.debug("Camera Make missing")

        # Map capture
        createdate = get_tag(["CreateDate"])
        if createdate:
            if ":" in str(createdate) and " " in str(createdate):
                parts = str(createdate).split(" ", 1)
                createdate_iso = parts[0].replace(":", "-") + "T" + parts[1] + "Z"
            else:
                createdate_iso = str(createdate)
        else:
            createdate_iso = None
            result["warnings"].append("CreateDate missing")
            logger.debug("CreateDate missing")

        duration = get_tag(["MediaDuration", "Duration"])
        if duration:
            try:
                if isinstance(duration, str):
                    if " " in duration:
                        duration = float(duration.split(" ")[0])
                    else:
                        duration = float(duration)
                else:
                    duration = float(duration)
            except ValueError:
                duration = None
                result["warnings"].append("Could not parse duration")
                logger.warning(f"Failed to parse duration: {duration}")
        else:
            result["warnings"].append("Duration missing")
            logger.debug("Duration missing")

        timezone = get_tag(["TimeZone", "OffsetTime"])
        result["metadata"]["capture"] = {
            "timestamp_utc": createdate_iso,
            "duration_seconds": duration,
            "timezone": timezone
        }

        # Map video
        width = get_tag(["ImageWidth", "SourceImageWidth"])
        height = get_tag(["ImageHeight", "SourceImageHeight"])
        fps = get_tag(["VideoFrameRate", "FrameRate"])
        if fps:
            try:
                fps = float(fps)
            except ValueError:
                fps = None
                
        bitrate = get_tag(["AvgBitrate", "MaxBitrate"])
        if bitrate:
            if isinstance(bitrate, str):
                try:
                    if "mbps" in bitrate.lower():
                        val = float(bitrate.lower().replace("mbps", "").strip())
                        bitrate = int(val * 1_000_000)
                    elif "kbps" in bitrate.lower():
                        val = float(bitrate.lower().replace("kbps", "").strip())
                        bitrate = int(val * 1_000)
                    else:
                        bitrate = int(bitrate)
                except ValueError:
                    bitrate = None
                    result["warnings"].append("Could not parse bitrate")
                    logger.warning(f"Failed to parse bitrate: {bitrate}")
            else:
                try:
                    bitrate = int(bitrate)
                except ValueError:
                    bitrate = None
        
        codec = get_tag(["CompressorID", "VideoCodec"])
        projection = get_tag(["ProjectionType"])
        
        result["metadata"]["video"] = {
            "width": int(width) if width else None,
            "height": int(height) if height else None,
            "frame_rate": fps,
            "bitrate_bps": bitrate,
            "codec": codec,
            "projection": projection
        }

        # Map GPS
        lat = get_tag(["GPSLatitude"])
        lon = get_tag(["GPSLongitude"])
        alt = get_tag(["GPSAltitude"])
        
        def parse_gps(val):
            if isinstance(val, (int, float)):
                return float(val)
            if isinstance(val, str):
                try:
                    return float(val)
                except ValueError:
                    return None
            return None
            
        lat_f = parse_gps(lat)
        lon_f = parse_gps(lon)
        alt_f = parse_gps(alt)
        
        if lat_f is not None and lon_f is not None:
            result["metadata"]["gps"]["available"] = True
            result["metadata"]["gps"]["latitude"] = lat_f
            result["metadata"]["gps"]["longitude"] = lon_f
            result["metadata"]["gps"]["altitude_m"] = alt_f
            result["metadata"]["gps"]["track_points"] = get_tag(["GPSTrackRef", "GPSDateTime"])
        else:
            result["warnings"].append("GPS tags missing or invalid")
            logger.debug("GPS tags missing")

        # Map IMU from SDK
        result["metadata"]["imu"]["available"] = raw_sdk.get("imu_available", False)
        if result["metadata"]["imu"]["available"]:
            result["metadata"]["imu"]["source"] = "sdk"
        result["metadata"]["imu"]["gyroscope"] = raw_sdk.get("gyroscope")
        result["metadata"]["imu"]["accelerometer"] = raw_sdk.get("accelerometer")


    def extract_batch(self, filepaths: list[str]) -> dict:
        """
        Run extract() on a list of .insv files.
        """
        result = {
            "total": len(filepaths),
            "success": 0,
            "partial": 0,
            "failed": 0,
            "results": []
        }
        
        for fp in filepaths:
            res = self.extract(fp)
            result["results"].append(res)
            st = res["extraction_status"]
            if st == "success":
                result["success"] += 1
            elif st == "partial":
                result["partial"] += 1
            else:
                logger.error(f"Metadata extraction failed for file: {fp} with errors: {res.get('errors', [])}")
                result["failed"] += 1
                
        return result
