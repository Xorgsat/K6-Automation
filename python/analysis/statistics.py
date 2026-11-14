"""
Statistical utilities for performance metric distributions and variance analysis.
"""

import math
from typing import List, Tuple, Optional


def calculate_mean(values: List[float]) -> float:
    """Calculates arithmetic mean of values."""
    if not values:
        return 0.0
    return float(sum(values)) / len(values)


def calculate_median(values: List[float]) -> float:
    """Calculates median (50th percentile) of values."""
    return calculate_percentile(values, 50.0)


def calculate_percentile(values: List[float], percentile: float) -> float:
    """
    Calculates exact percentile using nearest rank or linear interpolation.
    Percentile must be between 0 and 100.
    """
    if not values:
        return 0.0
    if percentile <= 0:
        return float(min(values))
    if percentile >= 100:
        return float(max(values))

    sorted_vals = sorted(values)
    n = len(sorted_vals)
    index = (percentile / 100.0) * (n - 1)
    lower = math.floor(index)
    upper = math.ceil(index)
    weight = index - lower

    if lower == upper:
        return float(sorted_vals[int(index)])
    return float((1.0 - weight) * sorted_vals[lower] + weight * sorted_vals[upper])


def calculate_variance(values: List[float]) -> float:
    """Calculates sample variance."""
    if len(values) < 2:
        return 0.0
    mean = calculate_mean(values)
    return sum((x - mean) ** 2 for x in values) / (len(values) - 1)


def calculate_stddev(values: List[float]) -> float:
    """Calculates sample standard deviation."""
    return math.sqrt(calculate_variance(values))


def calculate_cv(values: List[float]) -> float:
    """
    Calculates Coefficient of Variation (CV = stddev / mean).
    Useful for assessing relative stability and measurement noise.
    """
    mean = calculate_mean(values)
    if mean == 0.0:
        return 0.0
    return calculate_stddev(values) / mean


def calculate_iqr(values: List[float]) -> float:
    """Calculates Interquartile Range (IQR = p75 - p25)."""
    if not values:
        return 0.0
    p25 = calculate_percentile(values, 25.0)
    p75 = calculate_percentile(values, 75.0)
    return p75 - p25


def calculate_confidence_interval(values: List[float], confidence: float = 0.95) -> Tuple[float, float]:
    """
    Calculates confidence interval for the mean.
    Returns (lower_bound, upper_bound).
    """
    if len(values) < 2:
        val = values[0] if values else 0.0
        return val, val

    mean = calculate_mean(values)
    stddev = calculate_stddev(values)
    n = len(values)
    # Z-scores for standard confidence levels
    z_table = {0.90: 1.645, 0.95: 1.960, 0.99: 2.576}
    z = z_table.get(confidence, 1.960)
    margin = z * (stddev / math.sqrt(n))

    return max(0.0, mean - margin), mean + margin
