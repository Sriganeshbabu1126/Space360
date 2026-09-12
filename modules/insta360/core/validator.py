"""
Responsible for quality and completeness validation of processed videos.
"""
import os
import logging

logger = logging.getLogger("insta360.validator")

class FileValidator:
    """
    Validates .insv files before and after transfer.
    """

    def validate_insv(self, filepath: str) -> dict:
        """
        Run pre-processing validation on a single .insv file.
        
        Checks:
          1. File exists and is readable
          2. File size > 0 bytes
          3. File extension is .insv (case-insensitive)
          4. File is not currently being written to
             (check by attempting exclusive open — if fails, file is locked)
          5. Minimum size check: warn if file < 1MB (likely corrupt or incomplete)
        """
        result = {
            "filepath": filepath,
            "valid": True,
            "checks": {
                "exists": False,
                "readable": False,
                "non_empty": False,
                "correct_extension": False,
                "not_locked": False,
                "minimum_size": False
            },
            "file_size_bytes": None,
            "warnings": [],
            "errors": []
        }
        
        if not os.path.exists(filepath):
            result["errors"].append("File does not exist")
            result["valid"] = False
            return result
            
        result["checks"]["exists"] = True
        
        if not os.access(filepath, os.R_OK):
            result["checks"]["readable"] = False
            result["errors"].append("File is not readable")
            result["valid"] = False
        else:
            result["checks"]["readable"] = True
            
        try:
            size = os.path.getsize(filepath)
            result["file_size_bytes"] = size
            if size > 0:
                result["checks"]["non_empty"] = True
            else:
                result["errors"].append("File is empty")
                result["valid"] = False
                
            if size >= 1024 * 1024:
                result["checks"]["minimum_size"] = True
            else:
                result["warnings"].append("File is smaller than 1MB")
                # not setting valid to False for warning
        except OSError as e:
            result["errors"].append(f"Failed to get file size: {e}")
            result["valid"] = False
            
        if filepath.lower().endswith(".insv"):
            result["checks"]["correct_extension"] = True
        else:
            result["errors"].append("File extension is not .insv")
            result["valid"] = False
            
        # Check if file is locked
        try:
            with open(filepath, "a"):
                result["checks"]["not_locked"] = True
        except OSError:
            result["errors"].append("File is locked or currently being written to")
            result["valid"] = False
            
        return result

    def validate_batch(self, filepaths: list[str]) -> dict:
        """
        Run validate_insv on a list of files.
        """
        result = {
            "total": len(filepaths),
            "valid": 0,
            "invalid": 0,
            "results": []
        }
        
        for filepath in filepaths:
            val_res = self.validate_insv(filepath)
            result["results"].append(val_res)
            if val_res["valid"]:
                result["valid"] += 1
            else:
                result["invalid"] += 1
                
        return result
