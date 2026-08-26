"""
Responsible for stitching .insv files to equirectangular MP4 via ffmpeg.
"""
import os
import json
import logging
import time
import subprocess
import shutil

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

        codec_info = self._detect_codec()
        result["codec_info"] = codec_info
        result["stitch"]["codec"] = codec_info["codec"]
        result["stitch"]["encode_method"] = codec_info["method"]

        logger.info(f"Stitching {src_insv} using {codec_info['codec']} ({codec_info['reason']})")

        duration = self._get_duration(src_insv)
        if duration:
            result["duration_seconds"] = duration

        start_time = time.time()
        success, stderr = self._run_ffmpeg(src_insv, dst_mp4, codec_info)
        stitch_duration = time.time() - start_time
        
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

    def _detect_codec(self) -> dict:
        def check_encoder(encoder: str) -> bool:
            try:
                result = subprocess.run(
                    ["ffmpeg", "-h", f"encoder={encoder}"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                return result.returncode == 0
            except FileNotFoundError:
                return False

        if check_encoder("hevc_nvenc"):
            return {"codec": "hevc_nvenc", "method": "nvenc", "reason": "NVIDIA NVENC H.265 supported"}
        elif check_encoder("h264_nvenc"):
            return {"codec": "h264_nvenc", "method": "nvenc", "reason": "NVIDIA NVENC H.264 supported"}
        elif check_encoder("libx265"):
            return {"codec": "libx265", "method": "software", "reason": "libx265 software fallback"}
        else:
            return {"codec": "libx264", "method": "software", "reason": "libx264 software fallback (default)"}

    def _get_duration(self, filepath: str) -> float:
        try:
            import ffmpeg
            probe = ffmpeg.probe(filepath)
            return float(probe['format']['duration'])
        except Exception:
            return None

    def _run_ffmpeg(self, src: str, dst: str, codec_info: dict) -> tuple[bool, str]:
        try:
            import ffmpeg
            stream = ffmpeg.input(src)
            stream = ffmpeg.output(stream, dst, vcodec=codec_info["codec"], acodec="copy")
            out, err = ffmpeg.run(stream, capture_stdout=True, capture_stderr=True, overwrite_output=True)
            return True, ""
        except ImportError:
            return False, "ffmpeg-python not installed"
        except ffmpeg.Error as e:
            return False, e.stderr.decode('utf-8', errors='replace') if e.stderr else str(e)
        except Exception as e:
            return False, str(e)

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
