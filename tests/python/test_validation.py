"""
Unit tests for python.validation.result_validator.
"""

import os
import tempfile
import pytest
from python.validation.result_validator import ResultValidator


def test_validate_nonexistent_file():
    ok, err, data = ResultValidator.validate_summary_file("nonexistent.json")
    assert not ok
    assert "does not exist" in err
    assert data is None


def test_validate_empty_file():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        ok, err, data = ResultValidator.validate_summary_file(path)
        assert not ok
        assert "is empty" in err
    finally:
        os.remove(path)


def test_validate_malformed_json():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("{ invalid json")
        path = f.name
    try:
        ok, err, data = ResultValidator.validate_summary_file(path)
        assert not ok
        assert "Malformed JSON" in err
    finally:
        os.remove(path)


def test_validate_missing_metrics():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write('{"root_group": {}}')
        path = f.name
    try:
        ok, err, data = ResultValidator.validate_summary_file(path)
        assert not ok
        assert "missing required 'metrics'" in err
    finally:
        os.remove(path)


def test_validate_valid_fixture():
    fixture_path = "datasets/fixtures/synthetic_summary.json"
    ok, err, data = ResultValidator.validate_summary_file(fixture_path)
    assert ok
    assert err is None
    assert "metrics" in data


def test_validate_workload_config():
    ok, err, data = ResultValidator.validate_workload_config("config/workloads.json")
    assert ok
    assert err is None
    assert "profiles" in data


def test_validate_threshold_config():
    ok, err, data = ResultValidator.validate_threshold_config("config/thresholds.json")
    assert ok
    assert err is None
    assert "profiles" in data
