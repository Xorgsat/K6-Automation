"""
Response time percentile analysis engine.
Computes and formats latency percentiles from k6 summary dictionaries and raw sample series.
"""

from typing import Dict, Any, List, Optional
from python.analysis.statistics import (
    calculate_mean,
    calculate_median,
    calculate_percentile,
    calculate_stddev,
    calculate_cv,
    calculate_iqr,
)


class PercentileAnalysis:
    """Analyzes and summarizes response time percentiles."""

    @staticmethod
    def extract_from_k6_metric(metric_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extracts percentiles and statistics from a k6 summary metric values object.
        """
        if not metric_data:
            return {
                "min": 0.0,
                "med": 0.0,
                "p90": 0.0,
                "p95": 0.0,
                "p99": 0.0,
                "max": 0.0,
                "avg": 0.0,
            }

        values = metric_data.get("values", {})
        return {
            "min": float(values.get("min", 0.0)),
            "med": float(values.get("med", 0.0)),
            "p90": float(values.get("p(90)", 0.0)),
            "p95": float(values.get("p(95)", 0.0)),
            "p99": float(values.get("p(99)", 0.0)),
            "max": float(values.get("max", 0.0)),
            "avg": float(values.get("avg", 0.0)),
        }

    @staticmethod
    def calculate_from_samples(samples: List[float]) -> Dict[str, float]:
        """
        Calculates exact percentiles and descriptive statistics from raw sample values.
        """
        if not samples:
            return {
                "min": 0.0,
                "med": 0.0,
                "p90": 0.0,
                "p95": 0.0,
                "p99": 0.0,
                "max": 0.0,
                "avg": 0.0,
                "stddev": 0.0,
                "cv": 0.0,
                "iqr": 0.0,
            }

        return {
            "min": float(min(samples)),
            "med": calculate_median(samples),
            "p90": calculate_percentile(samples, 90.0),
            "p95": calculate_percentile(samples, 95.0),
            "p99": calculate_percentile(samples, 99.0),
            "max": float(max(samples)),
            "avg": calculate_mean(samples),
            "stddev": calculate_stddev(samples),
            "cv": calculate_cv(samples),
            "iqr": calculate_iqr(samples),
        }
