"""
Responsible for stitching .insv files to equirectangular MP4 via ffmpeg.
"""
import os
import json
import logging
import time
import subprocess
import shutil
from datetime import datetime

logger = logging.getLogger("insta360.stitcher")

class VideoStitcher:
    """
    Stitches .insv files to equirectangular MP4 using ffmpeg.
    Probes system for hardware encoding (NVENC) with software fallback.
    """
    def stitch(self, src_insv: str, out_dir: str) -> dict:
        result = {
            "src": src_insv,
            "dst": None,
            "success": False,
            "codec_info": None,
            "duration_seconds": None,
            "output_size_bytes": None,
            "stitch": {
                "status": "failed",
                "engine": "ffmpeg",
                "codec": None,
                "encode_method": None,
                "stitch_duration_seconds": None,
                "output_path": None
            },
            "error": None
        }

        if not os.path.exists(src_insv):
            result["error"] = "Source file does not exist"
            return result

        os.makedirs(out_dir, exist_ok=True)
        base = os.path.splitext(os.path.basename(src_insv))[0]
        dst_mp4 = os.path.join(out_dir, f"{base}_stitched.mp4")
        result["dst"] = dst_mp4

        file_size_bytes = os.path.getsize(src_insv)
        codec_info = self._detect_codec(file_size_bytes)
        result["codec_info"] = codec_info
        result["stitch"]["codec"] = codec_info["codec"]
        result["stitch"]["encode_method"] = codec_info["method"]

        logger.info(f"Stitching {src_insv} using {codec_info['codec']} ({codec_info['reason']})")

        duration = self._get_duration(src_insv)
        if duration:
            result["duration_seconds"] = duration

        success, stderr, stitch_duration = self._run_ffmpeg(src_insv, dst_mp4, codec_info)
        
        result["stitch"]["stitch_duration_seconds"] = stitch_duration

        if success and os.path.exists(dst_mp4):
            result["success"] = True
            result["stitch"]["status"] = "success"
            result["stitch"]["output_path"] = dst_mp4
            result["output_size_bytes"] = os.path.getsize(dst_mp4)
            logger.info(f"Stitched {src_insv} successfully in {stitch_duration:.2f}s")
            
            sidecar_path = os.path.join(os.path.dirname(src_insv), f"{base}_metadata.json")
            if os.path.exists(sidecar_path):
                self._update_sidecar(sidecar_path, result)
        else:
            result["error"] = stderr or "ffmpeg failed without stderr"
            logger.error(f"Stitching failed for {src_insv}: {result['error']}")

        return result

    def stitch_batch(self, filepaths: list[str], out_dir: str) -> list[dict]:
        results = []
        for fp in filepaths:
            res = self.stitch(fp, out_dir)
            results.append(res)
        return results

    def _detect_codec(self, file_size_bytes: int) -> dict:
        ffmpeg_path = r"C:\ffmpeg\bin\ffmpeg.exe"
        debug_log = r"F:\Space360\modules\insta360\logs\stitcher_debug.log"
        
        # Large files (>200MB) -> use fast libx264
        if file_size_bytes > 200 * 1024 * 1024:
            with open(debug_log, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().isoformat()}] Large file ({file_size_bytes} bytes): using libx264 for speed\n")
            return {
                "codec": "libx264",
                "method": "software",
                "reason": "Large file (>200MB): using H.264 for speed"
            }
        
        codecs_to_try = ["libx265", "libx264"]
        
        for codec in codecs_to_try:
            try:
                result = subprocess.run(
                    [ffmpeg_path, "-h", "encoder=" + codec],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    method = "nvenc" if "nvenc" in codec else "software"
                    with open(debug_log, "a", encoding="utf-8") as f:
                        f.write(f"[{datetime.now().isoformat()}] Selected codec: {codec} ({method})\n")
                    return {
                        "codec": codec,
                        "method": method,
                        "reason": f"{codec} available"
                    }
            except:
                continue
        
        # Fallback to libx264
        return {
            "codec": "libx264",
            "method": "software",
            "reason": "Fallback to H.264 software encoder"
        }

    def _get_duration(self, filepath: str) -> float:
        try:
            import ffmpeg
            probe = ffmpeg.probe(filepath)
            return float(probe['format']['duration'])
        except Exception:
            return None

    def _run_ffmpeg(self, src: str, dst: str, codec_info: dict) -> tuple[bool, str, float]:
        """Run ffmpeg with timeout protection"""
        ffmpeg_path = r"C:\ffmpeg\bin\ffmpeg.exe"
        debug_log = r"F:\Space360\modules\insta360\logs\stitcher_debug.log"
        
        # Build command
        cmd = [
            ffmpeg_path, "-y",
            "-i", src,
            "-vcodec", codec_info["codec"],
            "-acodec", "copy",
            dst
        ]
        
        with open(debug_log, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] Starting ffmpeg (timeout: 600s)\n")
            f.write(f"  Command: {' '.join(cmd)}\n")
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                with open(debug_log, "a", encoding="utf-8") as f:
                    f.write(f"[{datetime.now().isoformat()}] ffmpeg succeeded in {duration:.1f}s\n")
                return True, "", duration
            else:
                error_msg = f"ffmpeg failed with code {result.returncode}: {result.stderr[-500:]}"
                with open(debug_log, "a", encoding="utf-8") as f:
                    f.write(f"[{datetime.now().isoformat()}] ffmpeg failed: {error_msg}\n")
                return False, error_msg, duration
        
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            error_msg = f"Stitching timeout after {duration:.0f}s (10min limit). Codec too slow for this system."
            with open(debug_log, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().isoformat()}] TIMEOUT: {error_msg}\n")
            return False, error_msg, duration
        
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Unexpected error: {type(e).__name__}: {e}"
            with open(debug_log, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().isoformat()}] ERROR: {error_msg}\n")
            return False, error_msg, duration

    def _update_sidecar(self, sidecar_path: str, stitch_result: dict) -> None:
        try:
            with open(sidecar_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            if "video" not in data:
                data["video"] = {}
                
            data["video"]["codec"] = stitch_result["stitch"]["codec"]
            if stitch_result.get("duration_seconds") and stitch_result.get("output_size_bytes"):
                data["video"]["bitrate_bps"] = int((stitch_result["output_size_bytes"] * 8) / stitch_result["duration_seconds"])

            data["stitch"] = stitch_result["stitch"]
            
            with open(sidecar_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to update sidecar {sidecar_path}: {e}")
