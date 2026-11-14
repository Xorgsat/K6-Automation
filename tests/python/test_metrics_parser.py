"""
Unit tests for python.analysis.metrics_parser and its analyzers.
"""

import pytest
from python.analysis.metrics_parser import MetricsParser
from python.analysis.percentile_analysis import PercentileAnalysis
from python.analysis.throughput_analysis import ThroughputAnalysis
from python.analysis.error_analysis import ErrorAnalysis


def test_metrics_parser_with_fixture():
    parser = MetricsParser("datasets/fixtures/synthetic_summary.json")
    model = parser.parse()

    assert model["latency"]["p95"] == 120.0
    assert model["latency"]["med"] == 24.5
    assert model["latency"]["avg"] == 45.2

    assert model["throughput"]["total_requests"] == 100
    assert model["throughput"]["requests_per_second"] == 10.0
    assert model["throughput"]["total_iterations"] == 25

    assert model["errors"]["failed_requests"] == 2
    assert model["errors"]["successful_requests"] == 98
    assert model["errors"]["failure_percentage"] == 2.0
    assert model["errors"]["taxonomy"]["validation_errors"] == 2


def test_percentile_analysis_from_samples():
    samples = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
    stats = PercentileAnalysis.calculate_from_samples(samples)

    assert stats["min"] == 10.0
    assert stats["max"] == 100.0
    assert stats["med"] == 55.0
    assert stats["p95"] == 95.5
    assert stats["avg"] == 55.0


def test_throughput_analysis_empty():
    res = ThroughputAnalysis.extract_throughput_metrics({})
    assert res["total_requests"] == 0
    assert res["requests_per_second"] == 0.0


def test_error_analysis_empty():
    res = ErrorAnalysis.extract_error_metrics({})
    assert res["total_requests"] == 0
    assert res["failure_rate"] == 0.0
