"""
Metric comparison engine for performance regression testing.
Calculates absolute and percentage deltas, taking metric directionality into account.
"""

from typing import Dict, Any


class MetricComparison:
    """Calculates differences between current execution metrics and baseline references."""

    @staticmethod
    def compare_numeric(
        current_value: float,
        baseline_value: float,
        higher_is_worse: bool = True
    ) -> Dict[str, Any]:
        """
        Compares two numeric scalar metrics safely.
        """
        curr = float(current_value) if current_value is not None else 0.0
        base = float(baseline_value) if baseline_value is not None else 0.0

        abs_diff = curr - base

        if base == 0.0:
            pct_diff = 0.0 if curr == 0.0 else 100.0
        else:
            pct_diff = (abs_diff / base) * 100.0

        # Determine degradation direction
        # If higher_is_worse (e.g. latency, errors): positive delta is degradation
        # If not higher_is_worse (e.g. throughput): negative delta is degradation
        is_degraded = (abs_diff > 0) if higher_is_worse else (abs_diff < 0)

        return {
            "current": round(curr, 2),
            "baseline": round(base, 2),
            "absolute_diff": round(abs_diff, 2),
            "percentage_diff": round(pct_diff, 2),
            "higher_is_worse": higher_is_worse,
            "is_degraded": is_degraded,
        }

    @staticmethod
    def compare_performance_models(
        current_model: Dict[str, Any],
        baseline_model: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compares full parsed performance models across latency, throughput, and error metrics.
        """
        curr_lat = current_model.get("latency", {})
        base_lat = baseline_model.get("latency", {})

        curr_tp = current_model.get("throughput", {})
        base_tp = baseline_model.get("throughput", {})

        curr_err = current_model.get("errors", {})
        base_err = baseline_model.get("errors", {})

        comparisons = {
            "latency_p95": MetricComparison.compare_numeric(
                curr_lat.get("p95", 0.0),
                base_lat.get("p95", 0.0),
                higher_is_worse=True
            ),
            "latency_p90": MetricComparison.compare_numeric(
                curr_lat.get("p90", 0.0),
                base_lat.get("p90", 0.0),
                higher_is_worse=True
            ),
            "latency_median": MetricComparison.compare_numeric(
                curr_lat.get("med", 0.0),
                base_lat.get("med", 0.0),
                higher_is_worse=True
            ),
            "latency_avg": MetricComparison.compare_numeric(
                curr_lat.get("avg", 0.0),
                base_lat.get("avg", 0.0),
                higher_is_worse=True
            ),
            "throughput_rps": MetricComparison.compare_numeric(
                curr_tp.get("requests_per_second", 0.0),
                base_tp.get("requests_per_second", 0.0),
                higher_is_worse=False
            ),
            "error_rate": MetricComparison.compare_numeric(
                curr_err.get("failure_rate", 0.0),
                base_err.get("failure_rate", 0.0),
                higher_is_worse=True
            ),
        }

        return comparisons
