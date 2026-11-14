"""
Consolidated k6 metrics ingestion and parsing engine.
"""

from typing import Dict, Any, Optional
from python.analysis.percentile_analysis import PercentileAnalysis
from python.analysis.throughput_analysis import ThroughputAnalysis
from python.analysis.error_analysis import ErrorAnalysis
from python.validation.result_validator import ResultValidator, ValidationError


class MetricsParser:
    """Parses raw k6 summary JSON into a structured, typed performance analysis model."""

    def __init__(self, summary_path: str):
        self.summary_path = summary_path
        is_valid, err_msg, data = ResultValidator.validate_summary_file(summary_path)
        if not is_valid:
            raise ValidationError(f"Invalid summary file '{summary_path}': {err_msg}")
        self.raw_data = data
        self.metrics = data.get("metrics", {})
        self.root_group = data.get("root_group", {})

    def parse(self) -> Dict[str, Any]:
        """
        Parses all metrics into a consolidated dictionary.
        """
        # 1. Overall HTTP Request Duration
        http_duration_metric = self.metrics.get("http_req_duration", {})
        latency_overview = PercentileAnalysis.extract_from_k6_metric(http_duration_metric)

        # 2. Throughput & Volumes
        throughput_overview = ThroughputAnalysis.extract_throughput_metrics(self.metrics)

        # 3. Errors & Checks
        error_overview = ErrorAnalysis.extract_error_metrics(self.metrics, self.root_group)

        # 4. Custom Business Durations
        custom_durations = {}
        for custom_name in ["recommendation_duration", "rating_operation_duration", "catalog_operation_duration"]:
            if custom_name in self.metrics:
                custom_durations[custom_name] = PercentileAnalysis.extract_from_k6_metric(self.metrics[custom_name])

        # 5. Virtual Users
        vus_metric = self.metrics.get("vus", {}).get("values", {})
        vus_max_metric = self.metrics.get("vus_max", {}).get("values", {})
        vus_info = {
            "current_vus": int(vus_metric.get("value", 0)),
            "max_vus": int(vus_max_metric.get("value", 0)),
        }

        # 6. Endpoint-level Metrics Extraction
        # Look for metric thresholds or sub-metrics with tag filters
        endpoints = self._extract_endpoint_metrics()

        return {
            "summary_path": self.summary_path,
            "latency": latency_overview,
            "throughput": throughput_overview,
            "errors": error_overview,
            "vus": vus_info,
            "custom_business_metrics": custom_durations,
            "endpoints": endpoints,
        }

    def _extract_endpoint_metrics(self) -> Dict[str, Any]:
        """
        Extracts endpoint-specific metrics if available in the summary.
        """
        endpoints = {}
        # In k6 summary, tagged metrics may appear as http_req_duration{name:...}
        for key, val in self.metrics.items():
            if key.startswith("http_req_duration{") and "}" in key:
                # Extract tag content
                tag_content = key[len("http_req_duration{"):-1]
                name = tag_content.replace("name:", "").strip()
                endpoints[name] = PercentileAnalysis.extract_from_k6_metric(val)

        return endpoints
