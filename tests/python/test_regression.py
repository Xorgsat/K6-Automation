"""
Unit tests for python.regression.comparison and regression_detector.
"""

import pytest
from python.regression.comparison import MetricComparison
from python.regression.regression_detector import RegressionDetector, RegressionClassification


def test_metric_comparison_numeric():
    # Latency: higher is worse
    comp = MetricComparison.compare_numeric(current_value=120.0, baseline_value=100.0, higher_is_worse=True)
    assert comp["absolute_diff"] == 20.0
    assert comp["percentage_diff"] == 20.0
    assert comp["is_degraded"] is True

    # Throughput: lower is worse
    comp_tp = MetricComparison.compare_numeric(current_value=40.0, baseline_value=50.0, higher_is_worse=False)
    assert comp_tp["absolute_diff"] == -10.0
    assert comp_tp["percentage_diff"] == -20.0
    assert comp_tp["is_degraded"] is True

    # Zero baseline handling
    comp_zero = MetricComparison.compare_numeric(current_value=10.0, baseline_value=0.0)
    assert comp_zero["percentage_diff"] == 100.0


def test_regression_detector_pass():
    detector = RegressionDetector()
    comparisons = {
        "latency_p95": {"current": 105.0, "baseline": 100.0, "absolute_diff": 5.0, "percentage_diff": 5.0, "is_degraded": True},
        "throughput_rps": {"current": 50.0, "baseline": 50.0, "absolute_diff": 0.0, "percentage_diff": 0.0, "is_degraded": False},
        "error_rate": {"current": 0.0, "baseline": 0.0, "absolute_diff": 0.0, "percentage_diff": 0.0, "is_degraded": False},
    }
    decision = detector.evaluate(comparisons)
    assert decision["verdict"] == RegressionClassification.PASS
    assert not decision["is_regression"]


def test_regression_detector_latency_regression():
    detector = RegressionDetector()
    comparisons = {
        "latency_p95": {"current": 150.0, "baseline": 100.0, "absolute_diff": 50.0, "percentage_diff": 50.0, "is_degraded": True},
        "throughput_rps": {"current": 50.0, "baseline": 50.0, "absolute_diff": 0.0, "percentage_diff": 0.0, "is_degraded": False},
        "error_rate": {"current": 0.0, "baseline": 0.0, "absolute_diff": 0.0, "percentage_diff": 0.0, "is_degraded": False},
    }
    decision = detector.evaluate(comparisons)
    assert decision["verdict"] == RegressionClassification.REGRESSION
    assert decision["is_regression"]


def test_regression_detector_noise_filter():
    detector = RegressionDetector()
    # 25% increase, but only 2ms absolute diff (noise floor is 30ms)
    comparisons = {
        "latency_p95": {"current": 10.0, "baseline": 8.0, "absolute_diff": 2.0, "percentage_diff": 25.0, "is_degraded": True},
        "throughput_rps": {"current": 50.0, "baseline": 50.0, "absolute_diff": 0.0, "percentage_diff": 0.0, "is_degraded": False},
        "error_rate": {"current": 0.0, "baseline": 0.0, "absolute_diff": 0.0, "percentage_diff": 0.0, "is_degraded": False},
    }
    decision = detector.evaluate(comparisons)
    # Should PASS because 2ms delta is filtered out as measurement noise
    assert decision["verdict"] == RegressionClassification.PASS
