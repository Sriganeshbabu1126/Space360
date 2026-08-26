import os
import re
import logging
import threading
from datetime import datetime, timezone
from core.job_manager import JobManager
from core.camera import CameraDetector
from core.validator import FileValidator
from core.metadata import MetadataExtractor
from core.stitcher import VideoStitcher
from core.uploader import GCSUploader
from config import config

logger = logging.getLogger("insta360.pipeline")

class PipelineRunner:
    def __init__(self, job_manager: JobManager):
        self.job_manager = job_manager

    def run(self, job_id: str, source_dir: str) -> None:
        thread = threading.Thread(target=self._run_pipeline, args=(job_id, source_dir))
        thread.daemon = True
        thread.start()

    def _run_pipeline(self, job_id: str, source_dir: str) -> None:
        logger.info(f"Starting pipeline for job {job_id}")
        
        try:
            # Step 1: Detect
            self.job_manager.update(job_id, "detect", "running", None)
            detector = CameraDetector()
            insv_files = detector.list_insv_files(source_dir)
            detect_result = {
                "mode": "usb_storage" if insv_files else "not_connected",
                "drive": source_dir,
                "insv_files": insv_files,
                "file_count": len(insv_files)
            }
            if not insv_files:
                self.job_manager.fail(job_id, "detect", "No .insv files found in source_dir")
                return
            self.job_manager.update(job_id, "detect", "complete", detect_result)

            # Step 2: Validate
            self.job_manager.update(job_id, "validate", "running", None)
            validator = FileValidator()
            val_res = validator.validate_batch(insv_files)
            if val_res["invalid"] > 0:
                self.job_manager.fail(job_id, "validate", "Some files failed validation")
                return
            self.job_manager.update(job_id, "validate", "complete", val_res)

            # Step 3: Transfer
            self.job_manager.update(job_id, "transfer", "running", None)
            transfer_res = detector.transfer_files(insv_files, config.OUTPUT_DIR)
            if transfer_res["failed"] > 0:
                self.job_manager.fail(job_id, "transfer", "Some files failed transfer")
                return
            self.job_manager.update(job_id, "transfer", "complete", transfer_res)

            destination_files = [f["destination"] for f in transfer_res["files"] if f["status"] in ("copied", "skipped")]

            # Step 4: Extract Metadata
            self.job_manager.update(job_id, "extract", "running", None)
            extractor = MetadataExtractor()
            extract_res = extractor.extract_batch(destination_files)
            if extract_res["failed"] > 0:
                self.job_manager.fail(job_id, "extract", "Metadata extraction failed for some files")
                return
            self.job_manager.update(job_id, "extract", "complete", extract_res)

            # Step 5: Stitch
            self.job_manager.update(job_id, "stitch", "running", None)
            stitcher = VideoStitcher()
            stitch_results = []
            for dest_file in destination_files:
                date_dir = os.path.dirname(dest_file)
                stitched_out_dir = os.path.join(date_dir, "stitched")
                stitch_res = stitcher.stitch(dest_file, stitched_out_dir)
                stitch_results.append(stitch_res)
            
            failed_stitches = sum(1 for s in stitch_results if not s["success"])
            if failed_stitches > 0:
                self.job_manager.fail(job_id, "stitch", "Stitching failed for some files")
                return
            self.job_manager.update(job_id, "stitch", "complete", {"results": stitch_results})

            # Step 6: Upload
            self.job_manager.update(job_id, "upload", "running", None)
            uploader = GCSUploader()
            upload_results = []
            gcs_uris = []
            
            for sr in stitch_results:
                if sr["success"] and sr["dst"]:
                    mp4_path = sr["dst"]
                    base = os.path.splitext(os.path.basename(sr["src"]))[0]
                    sidecar_path = os.path.join(os.path.dirname(sr["src"]), f"{base}_metadata.json")
                    
                    date_str = os.path.basename(os.path.dirname(sr["src"]))
                    if not re.match(r"\d{8}", date_str):
                        date_str = "unknown"
                    
                    pair_res = uploader.upload_pair(mp4_path, sidecar_path, date_str)
                    upload_results.append(pair_res)
                    
                    if pair_res["pair_success"]:
                        uploader._update_sidecar(sidecar_path, pair_res)
                        gcs_uris.append(pair_res["mp4"]["gcs_uri"])
                        gcs_uris.append(pair_res["sidecar"]["gcs_uri"])

            failed_uploads = sum(1 for u in upload_results if not u["pair_success"])
            self.job_manager.update(job_id, "upload", "complete", {"results": upload_results})

            # Summary
            summary = {
                "total_files": len(insv_files),
                "stitched": len(stitch_results) - failed_stitches,
                "uploaded": len(upload_results) - failed_uploads,
                "failed": failed_stitches + failed_uploads,
                "gcs_uris": gcs_uris,
                "completed_at_utc": datetime.now(timezone.utc).isoformat()
            }
            
            self.job_manager.complete(job_id, summary)
            logger.info(f"Pipeline complete for job {job_id}")

        except Exception as e:
            logger.error(f"Pipeline failed for job {job_id}: {e}")
            self.job_manager.fail(job_id, "pipeline", str(e))
