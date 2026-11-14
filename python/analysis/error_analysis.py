"""
Error classification and functional check analysis engine.
Categorizes failures into Transport, 4xx Client, 5xx Server, Validation, and Business errors.
"""

from typing import Dict, Any, List


class ErrorAnalysis:
    """Analyzes and categorizes error rates and check failures."""

    @staticmethod
    def extract_error_metrics(metrics: Dict[str, Any], root_group: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Extracts error taxonomy counts and check failure breakdowns.
        """
        http_req_failed = metrics.get("http_req_failed", {}).get("values", {})
        failed_count = int(http_req_failed.get("fails", 0)) # in k6 http_req_failed, 'passes' means request failed, 'fails' means request didn't fail
        # In k6, http_req_failed is a Rate metric:
        # values.passes is count of failed requests (where condition was true)
        # values.fails is count of successful requests
        failed_requests = int(http_req_failed.get("passes", 0))
        successful_requests = int(http_req_failed.get("fails", 0))
        total_requests = failed_requests + successful_requests
        failure_rate = float(http_req_failed.get("rate", 0.0))

        # Check metrics
        checks_metric = metrics.get("checks", {}).get("values", {})
        check_passes = int(checks_metric.get("passes", 0))
        check_fails = int(checks_metric.get("fails", 0))
        total_checks = check_passes + check_fails
        check_pass_rate = float(checks_metric.get("rate", 1.0))

        # Custom error counters
        transport_errors = int(metrics.get("errors_transport", {}).get("values", {}).get("count", 0))
        client_4xx = int(metrics.get("errors_client_4xx", {}).get("values", {}).get("count", 0))
        server_5xx = int(metrics.get("errors_server_5xx", {}).get("values", {}).get("count", 0))
        validation_errors = int(metrics.get("errors_validation", {}).get("values", {}).get("count", 0))
        business_failures = int(metrics.get("business_transaction_failures", {}).get("values", {}).get("count", 0))

        # Traverse root group for check details
        detailed_checks = []
        if root_group:
            ErrorAnalysis._collect_checks(root_group, detailed_checks)

        return {
            "failed_requests": failed_requests,
            "successful_requests": successful_requests,
            "total_requests": total_requests,
            "failure_rate": round(failure_rate, 4),
            "failure_percentage": round(failure_rate * 100.0, 2),
            "total_checks": total_checks,
            "check_passes": check_passes,
            "check_fails": check_fails,
            "check_pass_rate": round(check_pass_rate, 4),
            "check_pass_percentage": round(check_pass_rate * 100.0, 2),
            "taxonomy": {
                "transport_errors": transport_errors,
                "client_4xx": client_4xx,
                "server_5xx": server_5xx,
                "validation_errors": validation_errors,
                "business_failures": business_failures,
            },
            "detailed_checks": detailed_checks,
        }

    @staticmethod
    def _collect_checks(group: Dict[str, Any], results: List[Dict[str, Any]]):
        """Recursively collects checks from k6 groups."""
        for c in group.get("checks", []):
            results.append({
                "name": c.get("name", "unnamed"),
                "passes": int(c.get("passes", 0)),
                "fails": int(c.get("fails", 0)),
                "pass_rate": round(float(c.get("passes", 0)) / max(1, (int(c.get("passes", 0)) + int(c.get("fails", 0)))), 4),
            })
        for sub in group.get("groups", []):
            ErrorAnalysis._collect_checks(sub, results)
