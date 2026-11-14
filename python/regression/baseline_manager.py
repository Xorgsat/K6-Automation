"""
Baseline management and governance engine.
Saves, versions, and loads approved performance baselines alongside environment metadata.
"""

import json
import os
import platform
from datetime import datetime
from typing import Dict, Any, Optional


class BaselineManager:
    """Handles persistence and retrieval of approved baseline metrics."""

    DEFAULT_BASELINE_DIR = "baselines"
    APPROVED_FILENAME = "approved-baseline.json"

    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or self.DEFAULT_BASELINE_DIR
        self.metadata_dir = os.path.join(self.base_dir, "metadata")
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(self.metadata_dir, exist_ok=True)

    def get_approved_baseline_path(self) -> str:
        return os.path.join(self.base_dir, self.APPROVED_FILENAME)

    def load_approved_baseline(self) -> Optional[Dict[str, Any]]:
        """Loads the currently approved baseline, or returns None if none exists."""
        path = self.get_approved_baseline_path()
        if not os.path.exists(path):
            return None

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_baseline(
        self,
        parsed_metrics: Dict[str, Any],
        workload_profile: str,
        application_version: str = "quickpizza-0.15.30",
        notes: str = "Approved baseline run",
        set_as_approved: bool = True
    ) -> str:
        """
        Saves baseline with execution metadata.
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        metadata = {
            "application_version": application_version,
            "framework_version": "1.0.0",
            "created_at_utc": datetime.utcnow().isoformat() + "Z",
            "workload_profile": workload_profile,
            "notes": notes,
            "host": {
                "os": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
                "python_version": platform.python_version(),
            },
            "metrics": parsed_metrics,
        }

        # Save versioned snapshot in metadata/
        snapshot_name = f"baseline_{workload_profile}_{timestamp}.json"
        snapshot_path = os.path.join(self.metadata_dir, snapshot_name)
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        # Set as approved if requested
        if set_as_approved:
            approved_path = self.get_approved_baseline_path()
            with open(approved_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)

        return snapshot_path
