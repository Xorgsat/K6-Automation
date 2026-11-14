"""
Unit tests for python.regression.baseline_manager.
"""

import os
import shutil
import tempfile
import pytest
from python.regression.baseline_manager import BaselineManager


def test_baseline_manager_save_and_load():
    temp_dir = tempfile.mkdtemp()
    try:
        mgr = BaselineManager(temp_dir)
        mock_metrics = {
            "latency": {"p95": 90.0, "med": 20.0},
            "throughput": {"requests_per_second": 30.0},
            "errors": {"failure_rate": 0.0},
        }

        # Save baseline
        saved_path = mgr.save_baseline(mock_metrics, "smoke", notes="Test baseline")
        assert os.path.exists(saved_path)
        assert os.path.exists(mgr.get_approved_baseline_path())

        # Load baseline
        loaded = mgr.load_approved_baseline()
        assert loaded is not None
        assert loaded["workload_profile"] == "smoke"
        assert loaded["metrics"]["latency"]["p95"] == 90.0
    finally:
        shutil.rmtree(temp_dir)
