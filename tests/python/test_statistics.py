"""
Unit tests for python.analysis.statistics.
"""

import math
import pytest
from python.analysis.statistics import (
    calculate_mean,
    calculate_median,
    calculate_percentile,
    calculate_variance,
    calculate_stddev,
    calculate_cv,
    calculate_iqr,
    calculate_confidence_interval,
)


def test_mean():
    assert calculate_mean([]) == 0.0
    assert calculate_mean([10.0]) == 10.0
    assert calculate_mean([10.0, 20.0, 30.0]) == 20.0


def test_percentile():
    assert calculate_percentile([], 95.0) == 0.0
    samples = [10.0, 20.0, 30.0, 40.0, 50.0]
    assert calculate_percentile(samples, 0.0) == 10.0
    assert calculate_percentile(samples, 50.0) == 30.0
    assert calculate_percentile(samples, 100.0) == 50.0
    assert calculate_percentile(samples, 90.0) == 46.0


def test_variance_and_stddev():
    assert calculate_variance([]) == 0.0
    assert calculate_variance([42.0]) == 0.0
    samples = [10.0, 12.0, 23.0, 23.0, 16.0, 23.0, 21.0, 16.0]
    var = calculate_variance(samples)
    std = calculate_stddev(samples)
    assert round(var, 2) == 27.43
    assert round(std, 2) == 5.24


def test_cv_and_iqr():
    assert calculate_cv([]) == 0.0
    assert calculate_cv([0.0, 0.0]) == 0.0
    samples = [10.0, 20.0, 30.0, 40.0, 50.0]
    iqr = calculate_iqr(samples)
    assert iqr == 20.0


def test_confidence_interval():
    assert calculate_confidence_interval([]) == (0.0, 0.0)
    samples = [100.0, 102.0, 98.0, 101.0, 99.0]
    lower, upper = calculate_confidence_interval(samples, 0.95)
    assert lower < 100.0
    assert upper > 100.0
