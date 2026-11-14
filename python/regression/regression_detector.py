"""
Regression classification engine.
Applies statistical thresholds to distinguish true regressions from normal measurement variance.
"""

from typing import Dict, Any, List


class RegressionClassification:
    PASS = "PASS"
    WARNING = "WARNING"
    REGRESSION = "REGRESSION"
    INCONCLUSIVE = "INCONCLUSIVE"


class RegressionDetector:
    """Evaluates metric comparisons against regression tolerances."""

    DEFAULT_TOLERANCES = {
        "max_latency_degradation_pct": 15.0,
        "warning_latency_degradation_pct": 10.0,
        "max_throughput_degradation_pct": 10.0,
        "warning_throughput_degradation_pct": 5.0,
        "max_error_rate_increase_abs": 0.01,
        "min_absolute_latency_diff_ms": 30.0,  # Noise filter: ignore % changes if delta is under 30ms
    }

    def __init__(self, tolerances: Dict[str, float] = None):
        self.tolerances = {**self.DEFAULT_TOLERANCES, **(tolerances or {})}

    def evaluate(self, comparisons: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates comparisons and produces a formal regression decision.
        """
        findings: List[str] = []
        verdict = RegressionClassification.PASS

        # 1. Latency Evaluation (p95)
        p95_comp = comparisons.get("latency_p95", {})
        p95_pct = p95_comp.get("percentage_diff", 0.0)
        p95_abs = p95_comp.get("absolute_diff", 0.0)

        # Apply noise floor: only flag if absolute difference is meaningful
        if p95_abs > self.tolerances["min_absolute_latency_diff_ms"]:
            if p95_pct > self.tolerances["max_latency_degradation_pct"]:
                verdict = RegressionClassification.REGRESSION
                findings.append(
                    f"REGRESSION: p95 latency degraded by {p95_pct:.1f}% (+{p95_abs:.1f}ms). "
                    f"Exceeds tolerance of {self.tolerances['max_latency_degradation_pct']}%."
                )
            elif p95_pct > self.tolerances["warning_latency_degradation_pct"]:
                if verdict != RegressionClassification.REGRESSION:
                    verdict = RegressionClassification.WARNING
                findings.append(
                    f"WARNING: p95 latency increased by {p95_pct:.1f}% (+{p95_abs:.1f}ms)."
                )

        # 2. Throughput Evaluation (RPS)
        rps_comp = comparisons.get("throughput_rps", {})
        rps_pct = rps_comp.get("percentage_diff", 0.0)
        rps_abs = rps_comp.get("absolute_diff", 0.0)

        if rps_pct < -self.tolerances["max_throughput_degradation_pct"]:
            verdict = RegressionClassification.REGRESSION
            findings.append(
                f"REGRESSION: Throughput dropped by {abs(rps_pct):.1f}% ({rps_abs:.1f} req/s). "
                f"Exceeds tolerance of {self.tolerances['max_throughput_degradation_pct']}%."
            )
        elif rps_pct < -self.tolerances["warning_throughput_degradation_pct"]:
            if verdict != RegressionClassification.REGRESSION:
                verdict = RegressionClassification.WARNING
            findings.append(
                f"WARNING: Throughput decreased by {abs(rps_pct):.1f}%."
            )

        # 3. Error Rate Evaluation
        err_comp = comparisons.get("error_rate", {})
        err_abs = err_comp.get("absolute_diff", 0.0)

        if err_abs > self.tolerances["max_error_rate_increase_abs"]:
            verdict = RegressionClassification.REGRESSION
            findings.append(
                f"REGRESSION: Failure rate increased by {err_abs * 100.0:.2f}% percentage points. "
                f"Exceeds absolute tolerance of {self.tolerances['max_error_rate_increase_abs'] * 100.0}%."
            )

        if not findings:
            findings.append("All metrics within approved baseline tolerances. Performance stable.")

        return {
            "verdict": verdict,
            "is_regression": verdict == RegressionClassification.REGRESSION,
            "findings": findings,
            "tolerances_used": self.tolerances,
        }
