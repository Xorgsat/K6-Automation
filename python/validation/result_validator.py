"""
Configuration and test result schema validation utilities.
"""

import json
import os
from typing import Dict, Any, Tuple, Optional


class ValidationError(Exception):
    """Raised when configuration or result data fails schema validation."""
    pass


class ResultValidator:
    """Validates raw k6 summary JSON files and project configurations."""

    @staticmethod
    def validate_summary_file(file_path: str) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Validates that a k6 summary file exists, is valid JSON, and contains essential metrics.
        Returns: (is_valid, error_message, parsed_data)
        """
        if not file_path or not os.path.exists(file_path):
            return False, f"File does not exist: {file_path}", None

        if os.path.getsize(file_path) == 0:
            return False, f"File is empty: {file_path}", None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return False, f"Malformed JSON in {file_path}: {str(e)}", None
        except Exception as e:
            return False, f"Failed to read {file_path}: {str(e)}", None

        if not isinstance(data, dict):
            return False, "Root of summary must be a JSON object", None

        metrics = data.get("metrics")
        if not metrics or not isinstance(metrics, dict):
            return False, "Summary is missing required 'metrics' object", None

        # Verify key baseline metrics exist
        required_metrics = ["http_req_duration", "http_reqs"]
        missing = [m for m in required_metrics if m not in metrics]
        if missing:
            return False, f"Summary missing critical metrics: {', '.join(missing)}", None

        return True, None, data

    @staticmethod
    def validate_workload_config(config_path: str) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """Validates workloads.json configuration."""
        if not os.path.exists(config_path):
            return False, f"Workload config not found: {config_path}", None

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            return False, f"Failed to parse workload config: {str(e)}", None

        profiles = data.get("profiles", {})
        if not profiles:
            return False, "Workload config missing 'profiles' dictionary", None

        for name, profile in profiles.items():
            if "executor" not in profile:
                return False, f"Profile '{name}' missing 'executor'", None
            if profile["executor"] == "constant-vus":
                if "vus" not in profile or "duration" not in profile:
                    return False, f"Profile '{name}' with constant-vus requires 'vus' and 'duration'", None
            elif profile["executor"] == "ramping-vus":
                if "stages" not in profile or not isinstance(profile["stages"], list):
                    return False, f"Profile '{name}' with ramping-vus requires 'stages' list", None

        return True, None, data

    @staticmethod
    def validate_threshold_config(config_path: str) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """Validates thresholds.json configuration."""
        if not os.path.exists(config_path):
            return False, f"Thresholds config not found: {config_path}", None

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            return False, f"Failed to parse thresholds config: {str(e)}", None

        if "profiles" not in data:
            return False, "Thresholds config missing 'profiles'", None

        return True, None, data
